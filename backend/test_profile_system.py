"""
Test script for Student Profile system.
"""
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.gamification import StudentProgress
from src.models.achievement import Achievement, StudentAchievement
from src.models.streak import StreakTracking
from src.models.learning_path import LearningPath
from src.models.assessment import Skill
from src.services.profile_service import ProfileService


def test_profile_system():
    """Test the student profile system."""
    with app.app_context():
        print("\n" + "="*60)
        print("TESTING STUDENT PROFILE SYSTEM")
        print("="*60)
        
        # Cleanup
        StudentAchievement.query.filter_by(student_id=999).delete()
        StreakTracking.query.filter_by(student_id=999).delete()
        StudentProgress.query.filter_by(student_id=999).delete()
        LearningPath.query.filter_by(student_id=999).delete()
        Student.query.filter_by(id=999).delete()
        User.query.filter_by(id=999).delete()
        db.session.commit()
        
        # Create test user and student
        user = User(id=999, username='profile_test', email='profile_test@test.com')
        user.set_password('password')
        db.session.add(user)
        
        student = Student(
            id=999,
            user_id=999,
            name='Profile Tester',
            grade=5,
            bio='I love learning math!',
            avatar='🎓',
            profile_visibility='public'
        )
        db.session.add(student)
        
        # Create student progress
        progress = StudentProgress(
            student_id=999,
            total_xp=5000,
            current_level=10,
            xp_to_next_level=1000
        )
        db.session.add(progress)
        
        # Create streak data
        streak = StreakTracking(
            student_id=999,
            login_streak=7,
            login_streak_best=10,
            practice_streak=5,
            practice_streak_best=8
        )
        db.session.add(streak)
        
        # Create learning paths
        skill = Skill.query.first()
        if skill:
            lp1 = LearningPath(
                student_id=999,
                skill_id=skill.id,
                attempts=50,
                correct_answers=45,
                total_questions=50,
                current_accuracy=90.0,
                mastery_achieved=True
            )
            db.session.add(lp1)
        
        # Create achievement
        achievement = Achievement.query.first()
        if achievement:
            sa = StudentAchievement(
                student_id=999,
                achievement_id=achievement.id,
                progress=100,  # Completed
                unlocked_at=datetime.utcnow()
            )
            db.session.add(sa)
        
        db.session.commit()
        
        # Test 1: Get own profile
        print("\n1. Testing get own profile...")
        profile = ProfileService.get_profile(999, 999)
        assert profile is not None, "❌ Failed to get profile"
        assert profile['name'] == 'Profile Tester', "❌ Wrong name"
        assert profile['bio'] == 'I love learning math!', "❌ Wrong bio"
        assert profile['avatar'] == '🎓', "❌ Wrong avatar"
        print("✓ Own profile retrieved successfully")
        
        # Test 2: Profile stats
        print("\n2. Testing profile stats...")
        assert 'stats' in profile, "❌ Missing stats"
        stats = profile['stats']
        assert stats['level'] == 10, f"❌ Wrong level: {stats['level']}"
        assert stats['xp'] == 5000, f"❌ Wrong XP: {stats['xp']}"
        assert stats['login_streak'] == 7, f"❌ Wrong login streak: {stats['login_streak']}"
        assert stats['practice_streak'] == 5, f"❌ Wrong practice streak: {stats['practice_streak']}"
        print("✓ Profile stats correct")
        print(f"   Level: {stats['level']}, XP: {stats['xp']}")
        print(f"   Login streak: {stats['login_streak']}, Practice streak: {stats['practice_streak']}")
        
        # Test 3: Profile achievements
        print("\n3. Testing profile achievements...")
        assert 'achievements' in profile, "❌ Missing achievements"
        achievements = profile['achievements']
        assert 'total' in achievements, "❌ Missing total count"
        assert 'featured' in achievements, "❌ Missing featured achievements"
        print(f"✓ Achievements: {achievements['total']} total")
        
        # Test 4: Update profile
        print("\n4. Testing profile update...")
        updated = ProfileService.update_profile(
            999,
            bio='Updated bio!',
            avatar='🚀',
            profile_visibility='friends'
        )
        assert updated is not None, "❌ Failed to update profile"
        assert updated['bio'] == 'Updated bio!', "❌ Bio not updated"
        assert updated['avatar'] == '🚀', "❌ Avatar not updated"
        assert updated['profile_visibility'] == 'friends', "❌ Visibility not updated"
        print("✓ Profile updated successfully")
        
        # Test 5: Privacy settings
        print("\n5. Testing privacy settings...")
        updated = ProfileService.update_profile(
            999,
            show_stats=False,
            show_achievements=False,
            show_activity=False
        )
        assert updated['show_stats'] == False, "❌ show_stats not updated"
        assert updated['show_achievements'] == False, "❌ show_achievements not updated"
        assert updated['show_activity'] == False, "❌ show_activity not updated"
        print("✓ Privacy settings updated")
        
        # Test 6: Public profile view (different viewer)
        print("\n6. Testing public profile view...")
        # Reset visibility to public
        ProfileService.update_profile(999, profile_visibility='public')
        
        public_profile = ProfileService.get_profile(999, 888)  # Different viewer
        assert public_profile is not None, "❌ Failed to get public profile"
        assert public_profile['name'] == 'Profile Tester', "❌ Wrong name in public view"
        print("✓ Public profile viewable by others")
        
        # Test 7: Private profile view (should be blocked)
        print("\n7. Testing private profile view...")
        ProfileService.update_profile(999, profile_visibility='private')
        
        private_profile = ProfileService.get_profile(999, 888)  # Different viewer
        assert 'error' in private_profile, "❌ Private profile should be blocked"
        assert private_profile['error'] == 'This profile is private', "❌ Wrong error message"
        print("✓ Private profile blocked from others")
        
        # Test 8: Profile with hidden stats
        print("\n8. Testing profile with hidden stats...")
        ProfileService.update_profile(
            999,
            profile_visibility='public',
            show_stats=False
        )
        
        profile_no_stats = ProfileService.get_profile(999, 888)
        assert 'stats' not in profile_no_stats or profile_no_stats.get('stats') is None, "❌ Stats should be hidden"
        print("✓ Stats hidden from other viewers")
        
        # Test 9: Own profile always shows everything
        print("\n9. Testing own profile shows everything...")
        own_profile = ProfileService.get_profile(999, 999)
        assert 'stats' in own_profile, "❌ Own profile should show stats even if hidden"
        print("✓ Own profile shows all data regardless of privacy settings")
        
        # Test 10: Profile serialization
        print("\n10. Testing profile serialization...")
        student_dict = student.to_dict()
        assert 'bio' in student_dict, "❌ Missing bio in dict"
        assert 'avatar' in student_dict, "❌ Missing avatar in dict"
        assert 'profile_visibility' in student_dict, "❌ Missing profile_visibility in dict"
        print("✓ Profile serialization working")
        
        # Cleanup
        StudentAchievement.query.filter_by(student_id=999).delete()
        StreakTracking.query.filter_by(student_id=999).delete()
        StudentProgress.query.filter_by(student_id=999).delete()
        LearningPath.query.filter_by(student_id=999).delete()
        Student.query.filter_by(id=999).delete()
        User.query.filter_by(id=999).delete()
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")


if __name__ == '__main__':
    test_profile_system()

