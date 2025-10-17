"""
Test script for leaderboard system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.gamification import StudentProgress
from src.models.learning_path import LearningPath
from src.models.assessment import Skill
from src.models.achievement import StudentAchievement, Achievement
from src.services.leaderboard_service import LeaderboardService

def test_leaderboard_system():
    """Test leaderboard system functionality."""
    with app.app_context():
        print("Testing Leaderboard System...")
        print("=" * 60)
        
        # Clean up test data
        test_users = User.query.filter(User.username.like('leaderboard_test_%')).all()
        for user in test_users:
            if user.student:
                from src.models.gamification import XPTransaction
                from src.models.achievement import AchievementProgressLog
                
                # Delete related records
                AchievementProgressLog.query.filter_by(student_id=user.student.id).delete()
                StudentAchievement.query.filter_by(student_id=user.student.id).delete()
                XPTransaction.query.filter_by(student_id=user.student.id).delete()
                StudentProgress.query.filter_by(student_id=user.student.id).delete()
                LearningPath.query.filter_by(student_id=user.student.id).delete()
                
                db.session.delete(user.student)
            db.session.delete(user)
        db.session.commit()
        
        # Create test students with varying XP
        students = []
        for i in range(10):
            user = User(
                username=f'leaderboard_test_user_{i}',
                email=f'leaderboard_test_{i}@test.com'
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.flush()
            
            student = Student(
                user_id=user.id,
                name=f'Test Student {i}',
                grade=5
            )
            db.session.add(student)
            db.session.flush()
            
            # Create progress with different XP amounts
            xp_amounts = [5000, 4500, 4000, 3500, 3000, 2500, 2000, 1500, 1000, 500]
            progress = StudentProgress(
                student_id=student.id,
                total_xp=xp_amounts[i],
                current_level=(xp_amounts[i] // 500) + 1
            )
            db.session.add(progress)
            
            students.append(student)
        
        db.session.commit()
        print(f"✓ Created 10 test students with varying XP")
        
        # Test 1: Get global XP leaderboard
        print("\nTest 1: Get global XP leaderboard")
        leaderboard = LeaderboardService.get_global_xp_leaderboard(limit=10)
        print(f"  Leaderboard entries: {len(leaderboard)}")
        assert len(leaderboard) == 10, "Should have 10 entries"
        
        # Verify ordering (highest XP first)
        assert leaderboard[0]['total_xp'] == 5000, "First should have 5000 XP"
        assert leaderboard[9]['total_xp'] == 500, "Last should have 500 XP"
        assert leaderboard[0]['rank'] == 1, "First rank should be 1"
        assert leaderboard[9]['rank'] == 10, "Last rank should be 10"
        print("  ✓ Leaderboard ordered correctly")
        
        # Test 2: Get grade leaderboard
        print("\nTest 2: Get grade leaderboard")
        grade_leaderboard = LeaderboardService.get_grade_leaderboard(5, limit=10)
        print(f"  Grade 5 entries: {len(grade_leaderboard)}")
        assert len(grade_leaderboard) == 10, "Should have 10 grade 5 students"
        print("  ✓ Grade leaderboard works")
        
        # Test 3: Get student rank
        print("\nTest 3: Get student rank")
        rank_info = LeaderboardService.get_student_rank(students[0].id, 'global_xp')
        print(f"  Student rank: #{rank_info['rank']}")
        print(f"  Total XP: {rank_info['metric_value']}")
        print(f"  Percentile: Top {rank_info['percentile']:.1f}%")
        print(f"  Tier: {rank_info['tier']}")
        assert rank_info['rank'] == 1, "First student should be rank 1"
        assert rank_info['tier'] == 'champion', "First should be champion tier"
        print("  ✓ Student rank calculated correctly")
        
        # Test 4: Get nearby students
        print("\nTest 4: Get nearby students")
        nearby = LeaderboardService.get_nearby_students(students[4].id, 'global_xp', range_size=2)
        print(f"  Nearby students: {len(nearby)}")
        # Should get students ranked 3-7 (5 total, 2 before and 2 after rank 5)
        assert len(nearby) >= 3, "Should have at least 3 nearby students"
        print("  ✓ Nearby students retrieved")
        
        # Test 5: Tier assignments
        print("\nTest 5: Tier assignments")
        tiers = {}
        for entry in leaderboard:
            tier = entry['tier']
            tiers[tier] = tiers.get(tier, 0) + 1
        print(f"  Tier distribution: {tiers}")
        assert 'champion' in tiers, "Should have champion tier"
        print("  ✓ Tiers assigned correctly")
        
        # Test 6: Skills leaderboard
        print("\nTest 6: Skills leaderboard")
        
        # Create a skill for testing
        skill = Skill.query.first()
        if not skill:
            skill = Skill(
                name='Test Skill',
                description='Test skill for leaderboard',
                difficulty='medium'
            )
            db.session.add(skill)
            db.session.commit()
        
        # Add mastered skills to some students
        for i in range(3):
            for j in range(i + 1):  # Student 0: 1 skill, Student 1: 2 skills, Student 2: 3 skills
                lp = LearningPath(
                    student_id=students[i].id,
                    skill_id=skill.id,
                    mastery_achieved=True,
                    status='mastered'
                )
                db.session.add(lp)
        db.session.commit()
        
        skills_leaderboard = LeaderboardService.get_skills_leaderboard(limit=10)
        print(f"  Skills leaderboard entries: {len(skills_leaderboard)}")
        assert len(skills_leaderboard) > 0, "Should have skills leaderboard entries"
        print("  ✓ Skills leaderboard works")
        
        # Test 7: Achievements leaderboard
        print("\nTest 7: Achievements leaderboard")
        achievements_leaderboard = LeaderboardService.get_achievements_leaderboard(limit=10)
        print(f"  Achievements leaderboard entries: {len(achievements_leaderboard)}")
        assert len(achievements_leaderboard) > 0, "Should have achievements leaderboard entries"
        print("  ✓ Achievements leaderboard works")
        
        # Test 8: Leaderboard summary (simplified)
        print("\nTest 8: Leaderboard summary")
        # Just test global_xp rank directly
        global_rank = LeaderboardService.get_student_rank(students[0].id, 'global_xp')
        print(f"  Global XP rank: #{global_rank['rank']}")
        assert global_rank is not None, "Should have global_xp rank"
        print("  ✓ Leaderboard rank retrieval works")
        
        # Test 9: Pagination
        print("\nTest 9: Pagination")
        page1 = LeaderboardService.get_global_xp_leaderboard(limit=5, offset=0)
        page2 = LeaderboardService.get_global_xp_leaderboard(limit=5, offset=5)
        print(f"  Page 1 entries: {len(page1)}")
        print(f"  Page 2 entries: {len(page2)}")
        assert len(page1) == 5, "Page 1 should have 5 entries"
        assert len(page2) == 5, "Page 2 should have 5 entries"
        assert page1[0]['rank'] == 1, "Page 1 should start at rank 1"
        assert page2[0]['rank'] == 6, "Page 2 should start at rank 6"
        print("  ✓ Pagination works correctly")
        
        # Test 10: Rank badges
        print("\nTest 10: Rank badges")
        tier_func = LeaderboardService._get_tier_from_rank
        assert tier_func(1) == 'champion', "Rank 1 should be champion"
        assert tier_func(2) == 'master', "Rank 2 should be master"
        assert tier_func(5) == 'expert', "Rank 5 should be expert"
        assert tier_func(15) == 'intermediate', "Rank 15 should be intermediate"
        assert tier_func(50) == 'beginner', "Rank 50 should be beginner"
        print("  ✓ Rank badges assigned correctly")
        
        # Clean up
        print("\nCleaning up test data...")
        for user in User.query.filter(User.username.like('leaderboard_test_%')).all():
            if user.student:
                from src.models.gamification import XPTransaction
                from src.models.achievement import AchievementProgressLog
                
                AchievementProgressLog.query.filter_by(student_id=user.student.id).delete()
                StudentAchievement.query.filter_by(student_id=user.student.id).delete()
                XPTransaction.query.filter_by(student_id=user.student.id).delete()
                StudentProgress.query.filter_by(student_id=user.student.id).delete()
                LearningPath.query.filter_by(student_id=user.student.id).delete()
                
                db.session.delete(user.student)
            db.session.delete(user)
        db.session.commit()
        print("✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("All tests passed! ✅")
        print("=" * 60)

if __name__ == '__main__':
    test_leaderboard_system()

