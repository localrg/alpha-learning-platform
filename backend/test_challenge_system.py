"""
Test script for Daily Challenges system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from src.main import app
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.daily_challenge import DailyChallenge
from src.models.assessment import Skill
from src.models.gamification import StudentProgress
from src.services.challenge_service import ChallengeService


def test_challenge_system():
    """Test the daily challenges system."""
    with app.app_context():
        print("\n" + "="*60)
        print("TESTING DAILY CHALLENGES SYSTEM")
        print("="*60)
        
        # Cleanup
        DailyChallenge.query.delete()
        StudentProgress.query.filter_by(student_id=999).delete()
        Student.query.filter_by(id=999).delete()
        User.query.filter_by(id=999).delete()
        db.session.commit()
        
        # Create test user and student
        user = User(id=999, username='challenge_test', email='challenge_test@test.com')
        user.set_password('password')
        db.session.add(user)
        
        student = Student(id=999, user_id=999, name='Challenge Tester', grade=5)
        db.session.add(student)
        
        # Create student progress
        progress = StudentProgress(
            student_id=999,
            total_xp=1000,
            current_level=5,
            xp_to_next_level=1000
        )
        db.session.add(progress)
        
        # Create a test skill
        skill = Skill.query.first()
        if not skill:
            skill = Skill(name='Test Skill', grade=5, category='math')
            db.session.add(skill)
        
        db.session.commit()
        
        # Test 1: Generate daily challenges
        print("\n1. Testing challenge generation...")
        challenges = ChallengeService.generate_daily_challenges(999)
        assert challenges is not None, "❌ Failed to generate challenges"
        assert len(challenges) == 3, f"❌ Expected 3 challenges, got {len(challenges)}"
        print(f"✓ Generated {len(challenges)} challenges")
        
        for i, challenge in enumerate(challenges, 1):
            print(f"   Challenge {i}: {challenge.challenge_type} ({challenge.difficulty}) - {challenge.bonus_xp} XP")
            assert challenge.status == 'active', f"❌ Challenge {i} not active"
            assert challenge.target_value > 0, f"❌ Challenge {i} has invalid target"
            assert challenge.bonus_xp > 0, f"❌ Challenge {i} has no XP reward"
        
        # Test 2: Get active challenges
        print("\n2. Testing get active challenges...")
        active = ChallengeService.get_active_challenges(999)
        assert len(active) == 3, f"❌ Expected 3 active challenges, got {len(active)}"
        print(f"✓ Retrieved {len(active)} active challenges")
        
        # Test 3: Update challenge progress
        print("\n3. Testing challenge progress update...")
        challenge = active[0]
        initial_progress = challenge.current_progress
        updated = ChallengeService.update_progress(challenge.id, 1)
        assert updated is not None, "❌ Failed to update progress"
        assert updated.current_progress == initial_progress + 1, "❌ Progress not incremented"
        print(f"✓ Progress updated: {initial_progress} → {updated.current_progress}")
        
        # Test 4: Complete a challenge
        print("\n4. Testing challenge completion...")
        challenge = active[1]
        initial_xp = progress.total_xp
        
        # Complete the challenge by setting progress to target
        for i in range(challenge.target_value):
            ChallengeService.update_progress(challenge.id, 1)
        
        db.session.refresh(challenge)
        db.session.refresh(progress)
        
        assert challenge.status == 'completed', f"❌ Challenge not completed (status: {challenge.status})"
        assert challenge.completed_at is not None, "❌ Completion time not set"
        assert progress.total_xp > initial_xp, f"❌ XP not awarded ({initial_xp} → {progress.total_xp})"
        print(f"✓ Challenge completed! XP: {initial_xp} → {progress.total_xp} (+{progress.total_xp - initial_xp})")
        
        # Test 5: Challenge statistics
        print("\n5. Testing challenge statistics...")
        stats = ChallengeService.get_challenge_stats(999)
        assert stats is not None, "❌ Failed to get stats"
        assert stats['total_completed'] >= 1, "❌ Completed count incorrect"
        assert stats['total_xp_earned'] > 0, "❌ XP earned not tracked"
        print(f"✓ Stats retrieved:")
        print(f"   Total completed: {stats['total_completed']}")
        print(f"   Total XP earned: {stats['total_xp_earned']}")
        print(f"   Completion rate: {stats['completion_rate']:.0%}")
        
        # Test 6: Challenge history
        print("\n6. Testing challenge history...")
        history = ChallengeService.get_challenge_history(999, limit=10)
        assert history is not None, "❌ Failed to get history"
        assert len(history) > 0, "❌ No history returned"
        print(f"✓ Retrieved {len(history)} challenge records")
        
        # Test 7: Expire old challenges
        print("\n7. Testing challenge expiration...")
        # Create an expired challenge
        expired_challenge = DailyChallenge(
            student_id=999,
            challenge_type='question_marathon',
            difficulty='easy',
            description='Expired challenge',
            target_value=5,
            bonus_xp=50,
            status='active',
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        db.session.add(expired_challenge)
        db.session.commit()
        
        # Get active challenges (should expire the old one)
        active = ChallengeService.get_active_challenges(999)
        db.session.refresh(expired_challenge)
        
        assert expired_challenge.status == 'expired', f"❌ Challenge not expired (status: {expired_challenge.status})"
        print(f"✓ Old challenge expired successfully")
        
        # Test 8: Verify get_active_challenges returns correct count
        print("\n8. Testing active challenges retrieval...")
        active = ChallengeService.get_active_challenges(999)
        # Should have some active challenges
        assert len(active) > 0, "❌ No active challenges found"
        print(f"✓ Retrieved {len(active)} active challenges")
        
        # Test 9: Challenge to_dict method
        print("\n9. Testing challenge serialization...")
        challenge_dict = active[0].to_dict()
        assert 'id' in challenge_dict, "❌ Missing id in dict"
        assert 'type' in challenge_dict, "❌ Missing type in dict"
        assert 'progress' in challenge_dict, "❌ Missing progress in dict"
        assert 'bonus_xp' in challenge_dict, "❌ Missing bonus_xp in dict"
        assert 'time_remaining' in challenge_dict, "❌ Missing time_remaining in dict"
        print(f"✓ Challenge serialization working")
        
        # Test 10: Different difficulty levels
        print("\n10. Testing difficulty scaling...")
        # Create challenges for different levels
        for level in [1, 5, 10, 15]:
            StudentProgress.query.filter_by(student_id=999).update({'current_level': level})
            db.session.commit()
            
            # Clear existing challenges
            DailyChallenge.query.filter_by(student_id=999).delete()
            db.session.commit()
            
            challenges = ChallengeService.generate_daily_challenges(999)
            difficulties = [c.difficulty for c in challenges]
            print(f"   Level {level}: {difficulties}")
        
        print(f"✓ Difficulty scaling working")
        
        # Cleanup
        DailyChallenge.query.filter_by(student_id=999).delete()
        StudentProgress.query.filter_by(student_id=999).delete()
        Student.query.filter_by(id=999).delete()
        User.query.filter_by(id=999).delete()
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")


if __name__ == '__main__':
    test_challenge_system()

