"""
Test script for achievement system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.achievement import Achievement, StudentAchievement
from src.services.achievement_service import AchievementService

def test_achievement_system():
    """Test achievement system functionality."""
    with app.app_context():
        print("Testing Achievement System...")
        print("=" * 60)
        
        # Clean up test data
        test_user = User.query.filter_by(username='achievement_test_user').first()
        if test_user:
            if test_user.student:
                # Delete in correct order: logs -> achievements -> progress -> student
                from src.models.achievement import AchievementProgressLog
                from src.models.gamification import StudentProgress, XPTransaction
                AchievementProgressLog.query.filter_by(student_id=test_user.student.id).delete()
                StudentAchievement.query.filter_by(student_id=test_user.student.id).delete()
                XPTransaction.query.filter_by(student_id=test_user.student.id).delete()
                StudentProgress.query.filter_by(student_id=test_user.student.id).delete()
                db.session.delete(test_user.student)
            db.session.delete(test_user)
            db.session.commit()
        
        # Create test user and student
        user = User(username='achievement_test_user', email='achievement@test.com')
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        
        student = Student(
            user_id=user.id,
            name='Achievement Test Student',
            grade=5
        )
        db.session.add(student)
        db.session.commit()
        
        print(f"✓ Created test student (ID: {student.id})")
        
        # Test 1: Get all achievements
        print("\nTest 1: Get all achievements")
        achievements = AchievementService.get_student_achievements(student.id)
        print(f"  Total achievements: {len(achievements)}")
        assert len(achievements) == 40, "Should have 40 achievements"
        print("  ✓ All achievements retrieved")
        
        # Test 2: Track question completion
        print("\nTest 2: Track question completion")
        AchievementService.track_action(student.id, 'question_complete', {'first_try': True})
        
        # Check First Steps progress
        first_steps = Achievement.query.filter_by(name='First Steps').first()
        sa = StudentAchievement.query.filter_by(
            student_id=student.id,
            achievement_id=first_steps.id
        ).first()
        print(f"  First Steps progress: {sa.progress}/10")
        assert sa.progress == 1, "Should have 1 progress"
        print("  ✓ Question completion tracked")
        
        # Test 3: Unlock achievement
        print("\nTest 3: Unlock achievement")
        for i in range(9):
            AchievementService.track_action(student.id, 'question_complete', {'first_try': True})
        
        sa = StudentAchievement.query.filter_by(
            student_id=student.id,
            achievement_id=first_steps.id
        ).first()
        print(f"  First Steps progress: {sa.progress}/10")
        print(f"  Unlocked: {sa.unlocked_at is not None}")
        assert sa.unlocked_at is not None, "Should be unlocked"
        print("  ✓ Achievement unlocked")
        
        # Test 4: Get unlocked achievements
        print("\nTest 4: Get unlocked achievements")
        unlocked = AchievementService.get_unlocked_achievements(student.id)
        print(f"  Unlocked count: {len(unlocked)}")
        assert len(unlocked) >= 1, "Should have at least 1 unlocked"
        print("  ✓ Unlocked achievements retrieved")
        
        # Test 5: Track skill mastery
        print("\nTest 5: Track skill mastery")
        AchievementService.track_action(student.id, 'skill_mastered')
        
        first_mastery = Achievement.query.filter_by(name='First Mastery').first()
        sa = StudentAchievement.query.filter_by(
            student_id=student.id,
            achievement_id=first_mastery.id
        ).first()
        print(f"  First Mastery unlocked: {sa.unlocked_at is not None}")
        assert sa.unlocked_at is not None, "Should be unlocked"
        print("  ✓ Skill mastery tracked")
        
        # Test 6: Get in-progress achievements
        print("\nTest 6: Get in-progress achievements")
        in_progress = AchievementService.get_in_progress_achievements(student.id, limit=5)
        print(f"  In-progress count: {len(in_progress)}")
        assert len(in_progress) > 0, "Should have in-progress achievements"
        print("  ✓ In-progress achievements retrieved")
        
        # Test 7: Toggle display
        print("\nTest 7: Toggle achievement display")
        sa = AchievementService.toggle_display(student.id, first_steps.id)
        print(f"  Display toggled: {sa.is_displayed}")
        assert sa.is_displayed == True, "Should be displayed"
        
        sa = AchievementService.toggle_display(student.id, first_steps.id)
        print(f"  Display toggled again: {sa.is_displayed}")
        assert sa.is_displayed == False, "Should not be displayed"
        print("  ✓ Display toggle works")
        
        # Test 8: Get displayed achievements
        print("\nTest 8: Get displayed achievements")
        AchievementService.toggle_display(student.id, first_steps.id)  # Turn on
        displayed = AchievementService.get_displayed_achievements(student.id)
        print(f"  Displayed count: {len(displayed)}")
        assert len(displayed) >= 1, "Should have at least 1 displayed"
        print("  ✓ Displayed achievements retrieved")
        
        # Test 9: Get achievement stats
        print("\nTest 9: Get achievement stats")
        stats = AchievementService.get_achievement_stats(student.id)
        print(f"  Total: {stats['total_achievements']}")
        print(f"  Unlocked: {stats['unlocked_count']}")
        print(f"  Completion: {stats['completion_percentage']:.1f}%")
        assert stats['total_achievements'] == 40, "Should have 40 total"
        assert stats['unlocked_count'] >= 2, "Should have at least 2 unlocked"
        print("  ✓ Stats calculated correctly")
        
        # Test 10: Track various actions
        print("\nTest 10: Track various actions")
        AchievementService.track_action(student.id, 'video_watch')
        AchievementService.track_action(student.id, 'resource_download')
        AchievementService.track_action(student.id, 'example_try')
        AchievementService.track_action(student.id, 'hint_use')
        AchievementService.track_action(student.id, 'solution_view')
        print("  ✓ Various actions tracked")
        
        # Test 11: Category filtering
        print("\nTest 11: Category filtering")
        practice_achievements = AchievementService.get_student_achievements(
            student.id,
            category='practice'
        )
        print(f"  Practice achievements: {len(practice_achievements)}")
        assert len(practice_achievements) == 5, "Should have 5 practice achievements"
        print("  ✓ Category filtering works")
        
        # Test 12: Achievement tiers
        print("\nTest 12: Achievement tiers")
        bronze = Achievement.query.filter_by(tier='bronze').count()
        silver = Achievement.query.filter_by(tier='silver').count()
        gold = Achievement.query.filter_by(tier='gold').count()
        platinum = Achievement.query.filter_by(tier='platinum').count()
        diamond = Achievement.query.filter_by(tier='diamond').count()
        print(f"  Bronze: {bronze}, Silver: {silver}, Gold: {gold}, Platinum: {platinum}, Diamond: {diamond}")
        assert bronze + silver + gold + platinum + diamond == 40, "All tiers should sum to 40"
        print("  ✓ All tiers present")
        
        # Clean up
        print("\nCleaning up test data...")
        from src.models.achievement import AchievementProgressLog
        from src.models.gamification import StudentProgress, XPTransaction
        AchievementProgressLog.query.filter_by(student_id=student.id).delete()
        StudentAchievement.query.filter_by(student_id=student.id).delete()
        XPTransaction.query.filter_by(student_id=student.id).delete()
        StudentProgress.query.filter_by(student_id=student.id).delete()
        db.session.delete(student)
        db.session.delete(user)
        db.session.commit()
        print("✓ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("All tests passed! ✅")
        print("=" * 60)

if __name__ == '__main__':
    test_achievement_system()

