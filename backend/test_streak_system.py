"""
Test script for Streak Tracking system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, date, timedelta
from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.streak import StreakTracking
from src.models.gamification import StudentProgress
from src.services.streak_service import StreakService


def test_streak_system():
    """Test the streak tracking system."""
    with app.app_context():
        print("\n" + "="*60)
        print("TESTING STREAK TRACKING SYSTEM")
        print("="*60)
        
        # Cleanup
        StreakTracking.query.filter_by(student_id=999).delete()
        StudentProgress.query.filter_by(student_id=999).delete()
        Student.query.filter_by(id=999).delete()
        User.query.filter_by(id=999).delete()
        db.session.commit()
        
        # Create test user and student
        user = User(id=999, username='streak_test', email='streak_test@test.com')
        user.set_password('password')
        db.session.add(user)
        
        student = Student(id=999, user_id=999, name='Streak Tester', grade=5)
        db.session.add(student)
        
        # Create student progress
        progress = StudentProgress(
            student_id=999,
            total_xp=1000,
            current_level=5,
            xp_to_next_level=1000
        )
        db.session.add(progress)
        db.session.commit()
        
        # Test 1: Get or create streak
        print("\n1. Testing get or create streak...")
        streak = StreakService.get_or_create_streak(999)
        assert streak is not None, "❌ Failed to create streak"
        assert streak.login_streak == 0, "❌ Initial login streak not 0"
        assert streak.practice_streak == 0, "❌ Initial practice streak not 0"
        print("✓ Streak tracking created")
        
        # Test 2: First login
        print("\n2. Testing first login...")
        result = StreakService.update_login_streak(999)
        assert result['streak'] == 1, f"❌ First login streak should be 1, got {result['streak']}"
        assert not result.get('milestone_reached'), "❌ Should not reach milestone on day 1"
        print("✓ First login tracked: 1 day streak")
        
        # Test 3: Same day login (no change)
        print("\n3. Testing same day login...")
        result = StreakService.update_login_streak(999)
        assert result['streak'] == 1, "❌ Same day login should not increment"
        print("✓ Same day login handled correctly")
        
        # Test 4: Consecutive login
        print("\n4. Testing consecutive login...")
        streak = StreakTracking.query.filter_by(student_id=999).first()
        # Simulate yesterday's login
        streak.last_login_date = date.today() - timedelta(days=1)
        streak.login_streak = 1
        db.session.commit()
        
        result = StreakService.update_login_streak(999)
        assert result['streak'] == 2, f"❌ Consecutive login should be 2, got {result['streak']}"
        print("✓ Consecutive login tracked: 2 day streak")
        
        # Test 5: Login streak milestone (3 days)
        print("\n5. Testing login streak milestone...")
        streak = StreakTracking.query.filter_by(student_id=999).first()
        streak.last_login_date = date.today() - timedelta(days=1)
        streak.login_streak = 2
        db.session.commit()
        
        initial_xp = progress.total_xp
        result = StreakService.update_login_streak(999)
        db.session.refresh(progress)
        
        assert result['streak'] == 3, f"❌ Should be 3 day streak, got {result['streak']}"
        assert result.get('milestone_reached'), "❌ Should reach 3-day milestone"
        assert result.get('milestone_xp') == 25, f"❌ Should get 25 XP, got {result.get('milestone_xp')}"
        assert progress.total_xp > initial_xp, "❌ XP not awarded for milestone"
        print(f"✓ 3-day milestone reached! XP: {initial_xp} → {progress.total_xp} (+{progress.total_xp - initial_xp})")
        
        # Test 6: Broken login streak
        print("\n6. Testing broken login streak...")
        streak = StreakTracking.query.filter_by(student_id=999).first()
        streak.last_login_date = date.today() - timedelta(days=3)  # 3 days ago
        streak.login_streak = 5
        db.session.commit()
        
        result = StreakService.update_login_streak(999)
        assert result['streak'] == 1, f"❌ Broken streak should reset to 1, got {result['streak']}"
        assert result.get('streak_broken'), "❌ Should indicate streak was broken"
        print("✓ Broken streak reset to 1 day")
        
        # Test 7: First practice
        print("\n7. Testing first practice...")
        result = StreakService.update_practice_streak(999)
        assert result['streak'] == 1, f"❌ First practice streak should be 1, got {result['streak']}"
        print("✓ First practice tracked: 1 day streak")
        
        # Test 8: Practice streak milestone (3 days)
        print("\n8. Testing practice streak milestone...")
        streak = StreakTracking.query.filter_by(student_id=999).first()
        streak.last_practice_date = date.today() - timedelta(days=1)
        streak.practice_streak = 2
        db.session.commit()
        
        initial_xp = progress.total_xp
        result = StreakService.update_practice_streak(999)
        db.session.refresh(progress)
        
        assert result['streak'] == 3, f"❌ Should be 3 day streak, got {result['streak']}"
        assert result.get('milestone_reached'), "❌ Should reach 3-day milestone"
        assert result.get('milestone_xp') == 50, f"❌ Should get 50 XP, got {result.get('milestone_xp')}"
        print(f"✓ 3-day practice milestone! XP: {initial_xp} → {progress.total_xp} (+{progress.total_xp - initial_xp})")
        
        # Test 9: Best streak tracking
        print("\n9. Testing best streak tracking...")
        streak = StreakTracking.query.filter_by(student_id=999).first()
        assert streak.login_streak_best >= 3, "❌ Best login streak not updated"
        assert streak.practice_streak_best >= 3, "❌ Best practice streak not updated"
        print(f"✓ Best streaks tracked: Login={streak.login_streak_best}, Practice={streak.practice_streak_best}")
        
        # Test 10: Streak statistics
        print("\n10. Testing streak statistics...")
        stats = StreakService.get_streak_stats(999)
        assert 'login_streak' in stats, "❌ Missing login_streak in stats"
        assert 'practice_streak' in stats, "❌ Missing practice_streak in stats"
        assert 'login_next_milestone' in stats, "❌ Missing login_next_milestone"
        assert 'practice_next_milestone' in stats, "❌ Missing practice_next_milestone"
        print("✓ Streak statistics retrieved:")
        print(f"   Login: {stats['login_streak']} days (best: {stats['login_streak_best']})")
        print(f"   Practice: {stats['practice_streak']} days (best: {stats['practice_streak_best']})")
        if stats['login_next_milestone']:
            print(f"   Next login milestone: {stats['login_next_milestone']['days']} days (+{stats['login_next_milestone']['xp']} XP)")
        if stats['practice_next_milestone']:
            print(f"   Next practice milestone: {stats['practice_next_milestone']['days']} days (+{stats['practice_next_milestone']['xp']} XP)")
        
        # Test 11: Multiple milestones
        print("\n11. Testing 7-day milestone...")
        streak = StreakTracking.query.filter_by(student_id=999).first()
        streak.last_login_date = date.today() - timedelta(days=1)
        streak.login_streak = 6
        db.session.commit()
        
        initial_xp = progress.total_xp
        result = StreakService.update_login_streak(999)
        db.session.refresh(progress)
        
        assert result['streak'] == 7, "❌ Should be 7 day streak"
        assert result.get('milestone_xp') == 75, f"❌ Should get 75 XP for 7-day milestone, got {result.get('milestone_xp')}"
        print(f"✓ 7-day milestone reached! +{result.get('milestone_xp')} XP")
        
        # Test 12: to_dict serialization
        print("\n12. Testing streak serialization...")
        streak_dict = streak.to_dict()
        assert 'student_id' in streak_dict, "❌ Missing student_id in dict"
        assert 'login_streak' in streak_dict, "❌ Missing login_streak in dict"
        assert 'practice_streak' in streak_dict, "❌ Missing practice_streak in dict"
        print("✓ Streak serialization working")
        
        # Cleanup
        StreakTracking.query.filter_by(student_id=999).delete()
        StudentProgress.query.filter_by(student_id=999).delete()
        Student.query.filter_by(id=999).delete()
        User.query.filter_by(id=999).delete()
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")


if __name__ == '__main__':
    test_streak_system()

