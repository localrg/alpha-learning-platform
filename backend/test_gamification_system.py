"""
Comprehensive tests for the Gamification System.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.gamification import StudentProgress, XPTransaction, LevelReward, StudentReward
from src.models.student import Student
from src.models.user import User
from src.services.gamification_service import GamificationService

def test_gamification_system():
    """Test all gamification system functionality."""
    with app.app_context():
        print("=" * 60)
        print("TESTING GAMIFICATION SYSTEM")
        print("=" * 60)
        
        # Test 1: Create test student
        print("\n1. Creating test student...")
        # Clean up existing test user
        test_user = User.query.filter_by(username='gamification_test').first()
        if test_user:
            if test_user.student:
                if test_user.student.progress:
                    # Delete XP transactions
                    XPTransaction.query.filter_by(student_id=test_user.student.id).delete()
                    # Delete student rewards
                    StudentReward.query.filter_by(student_id=test_user.student.id).delete()
                    # Delete progress
                    db.session.delete(test_user.student.progress)
                db.session.delete(test_user.student)
            db.session.delete(test_user)
            db.session.commit()
        
        test_user = User(
            username='gamification_test',
            email='gamification_test@example.com'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        
        test_student = Student(
            user_id=test_user.id,
            name='Gamification Test Student',
            grade=3
        )
        db.session.add(test_student)
        db.session.commit()
        print(f"  ✓ Created test student: {test_student.name}")
        
        # Test 2: Get or create progress
        print("\n2. Testing get or create progress...")
        progress = GamificationService.get_or_create_progress(test_student.id)
        assert progress is not None
        assert progress.student_id == test_student.id
        assert progress.current_level == 1
        assert progress.total_xp == 0
        assert progress.level_title == 'Novice'
        print(f"  ✓ Initial progress created")
        print(f"  ✓ Level: {progress.current_level}, XP: {progress.total_xp}")
        
        # Test 3: Award XP for question
        print("\n3. Testing award XP for question...")
        result = GamificationService.award_xp(
            student_id=test_student.id,
            action_type='question_complete'
        )
        assert result['xp_awarded'] == 10
        assert result['total_xp'] == 10
        assert result['current_level'] == 1
        assert result['leveled_up'] is False
        print(f"  ✓ Awarded {result['xp_awarded']} XP")
        print(f"  ✓ Total XP: {result['total_xp']}")
        
        # Test 4: Award XP with difficulty multiplier
        print("\n4. Testing XP with difficulty multiplier...")
        result = GamificationService.award_xp(
            student_id=test_student.id,
            action_type='question_complete',
            difficulty='hard'
        )
        assert result['xp_awarded'] == 20  # 10 * 2.0 (hard)
        assert result['total_xp'] == 30
        print(f"  ✓ Awarded {result['xp_awarded']} XP (hard difficulty)")
        print(f"  ✓ Total XP: {result['total_xp']}")
        
        # Test 5: Award XP with bonuses
        print("\n5. Testing XP with bonuses...")
        result = GamificationService.award_xp(
            student_id=test_student.id,
            action_type='question_complete',
            base_xp=10,
            difficulty='medium',
            metadata={'first_try': True}
        )
        # Base: 10 * 1.5 (medium) = 15
        # Bonus: 10 * 1.5 = 15
        # Total: 30
        assert result['xp_awarded'] == 30
        assert result['total_xp'] == 60
        print(f"  ✓ Awarded {result['xp_awarded']} XP (medium + first try)")
        print(f"  ✓ Total XP: {result['total_xp']}")
        
        # Test 6: Award enough XP to level up
        print("\n6. Testing level up...")
        # Need 282 XP for level 2, currently at 60, need 222 more
        result = GamificationService.award_xp(
            student_id=test_student.id,
            action_type='skill_mastered',
            base_xp=250  # Award 250 to ensure level up
        )
        assert result['xp_awarded'] == 250
        assert result['total_xp'] == 310
        assert result['previous_level'] == 1
        assert result['current_level'] == 2
        assert result['leveled_up'] is True
        assert result['level_title'] == 'Novice'
        print(f"  ✓ Leveled up from {result['previous_level']} to {result['current_level']}")
        print(f"  ✓ New title: {result['level_title']}")
        print(f"  ✓ Rewards unlocked: {len(result['new_rewards'])}")
        
        # Test 7: Get student progress
        print("\n7. Testing get student progress...")
        progress_data = GamificationService.get_student_progress(test_student.id)
        assert progress_data['student_id'] == test_student.id
        assert progress_data['total_xp'] == 310
        assert progress_data['current_level'] == 2
        assert progress_data['level_title'] == 'Novice'
        assert 'rank' in progress_data
        assert 'progress_percentage' in progress_data
        print(f"  ✓ Level: {progress_data['current_level']}")
        print(f"  ✓ Total XP: {progress_data['total_xp']}")
        print(f"  ✓ XP to next level: {progress_data['xp_to_next_level']}")
        print(f"  ✓ Progress: {progress_data['progress_percentage']}%")
        
        # Test 8: Get XP history
        print("\n8. Testing get XP history...")
        history = GamificationService.get_xp_history(test_student.id, limit=10)
        assert len(history) == 4  # 4 transactions so far
        assert history[0]['total_xp'] == 250  # Most recent (skill mastered)
        print(f"  ✓ Found {len(history)} transactions")
        print(f"  ✓ Latest: {history[0]['description']}")
        
        # Test 9: Get student rewards
        print("\n9. Testing get student rewards...")
        rewards = GamificationService.get_student_rewards(test_student.id)
        assert 'unlocked_rewards' in rewards
        assert 'upcoming_rewards' in rewards
        print(f"  ✓ Unlocked rewards: {len(rewards['unlocked_rewards'])}")
        print(f"  ✓ Upcoming rewards: {len(rewards['upcoming_rewards'])}")
        
        # Test 10: Level progression calculations
        print("\n10. Testing level progression calculations...")
        xp_level_2 = StudentProgress.calculate_xp_for_level(2)
        xp_level_3 = StudentProgress.calculate_xp_for_level(3)
        xp_level_5 = StudentProgress.calculate_xp_for_level(5)
        assert xp_level_2 == 282
        assert xp_level_3 == 801
        print(f"  ✓ XP for level 2: {xp_level_2}")
        print(f"  ✓ XP for level 3: {xp_level_3}")
        print(f"  ✓ XP for level 5: {xp_level_5}")
        
        # Test 11: Level titles
        print("\n11. Testing level titles...")
        assert StudentProgress.get_level_title(1) == 'Novice'
        assert StudentProgress.get_level_title(5) == 'Apprentice'
        assert StudentProgress.get_level_title(10) == 'Practitioner'
        assert StudentProgress.get_level_title(15) == 'Expert'
        assert StudentProgress.get_level_title(20) == 'Master'
        print(f"  ✓ Level 1: {StudentProgress.get_level_title(1)}")
        print(f"  ✓ Level 5: {StudentProgress.get_level_title(5)}")
        print(f"  ✓ Level 10: {StudentProgress.get_level_title(10)}")
        print(f"  ✓ Level 20: {StudentProgress.get_level_title(20)}")
        
        # Test 12: Create another student for leaderboard
        print("\n12. Creating second student for leaderboard...")
        test_user2 = User(
            username='gamification_test2',
            email='gamification_test2@example.com'
        )
        test_user2.set_password('password123')
        db.session.add(test_user2)
        db.session.commit()
        
        test_student2 = Student(
            user_id=test_user2.id,
            name='Second Test Student',
            grade=3
        )
        db.session.add(test_student2)
        db.session.commit()
        
        # Award some XP to second student
        GamificationService.award_xp(test_student2.id, 'skill_mastered', base_xp=200)
        print(f"  ✓ Created second student with 200 XP")
        
        # Test 13: Get leaderboard
        print("\n13. Testing leaderboard...")
        leaderboard = GamificationService.get_leaderboard(timeframe='all', limit=10)
        assert len(leaderboard) >= 2
        assert leaderboard[0]['total_xp'] == 310  # First student is first now
        assert leaderboard[1]['total_xp'] == 200  # Second student is second
        print(f"  ✓ Leaderboard has {len(leaderboard)} students")
        print(f"  ✓ Rank 1: {leaderboard[0]['student_name']} ({leaderboard[0]['total_xp']} XP)")
        print(f"  ✓ Rank 2: {leaderboard[1]['student_name']} ({leaderboard[1]['total_xp']} XP)")
        
        # Test 14: Verify level rewards exist
        print("\n14. Testing level rewards...")
        all_rewards = LevelReward.query.all()
        assert len(all_rewards) > 0
        print(f"  ✓ Total level rewards: {len(all_rewards)}")
        for reward in all_rewards[:5]:
            print(f"    Level {reward.level}: {reward.reward_type} - {reward.reward_value}")
        
        # Test 15: Test streak multiplier
        print("\n15. Testing streak multiplier...")
        result = GamificationService.award_xp(
            student_id=test_student.id,
            action_type='question_complete',
            base_xp=10,
            metadata={'streak': 5}
        )
        # 10 * 1.5 (streak 5) = 15
        assert result['xp_awarded'] == 15
        print(f"  ✓ Awarded {result['xp_awarded']} XP with 5-streak multiplier")
        
        # Test 16: Test perfect review
        print("\n16. Testing perfect review bonus...")
        result = GamificationService.award_xp(
            student_id=test_student.id,
            action_type='review_complete',
            base_xp=20,
            metadata={'perfect': True}
        )
        # Base: 20, Bonus: 30, Total: 50
        assert result['xp_awarded'] == 50
        print(f"  ✓ Awarded {result['xp_awarded']} XP for perfect review")
        
        # Test 17: Cleanup
        print("\n17. Cleaning up test data...")
        # Delete second student's data
        XPTransaction.query.filter_by(student_id=test_student2.id).delete()
        StudentReward.query.filter_by(student_id=test_student2.id).delete()
        if test_student2.progress:
            db.session.delete(test_student2.progress)
        db.session.delete(test_student2)
        db.session.delete(test_user2)
        
        # Delete first student's data
        XPTransaction.query.filter_by(student_id=test_student.id).delete()
        StudentReward.query.filter_by(student_id=test_student.id).delete()
        if test_student.progress:
            db.session.delete(test_student.progress)
        db.session.delete(test_student)
        db.session.delete(test_user)
        
        db.session.commit()
        print(f"  ✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("Gamification System Features Verified:")
        print("  ✓ Student progress creation")
        print("  ✓ XP awarding")
        print("  ✓ Difficulty multipliers")
        print("  ✓ Bonus XP (first try, perfect)")
        print("  ✓ Level progression")
        print("  ✓ Level titles")
        print("  ✓ Reward unlocking")
        print("  ✓ XP history tracking")
        print("  ✓ Student rewards")
        print("  ✓ Leaderboard rankings")
        print("  ✓ Streak multipliers")
        print("  ✓ Level calculations")
        print("=" * 60)

if __name__ == '__main__':
    test_gamification_system()

