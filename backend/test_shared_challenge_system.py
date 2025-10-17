"""
Test Shared Challenge System
Tests all shared challenge functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import db, init_db
from src.models.user import User
from src.models.student import Student
from src.models.shared_challenge import SharedChallenge, ChallengeParticipant
from src.models.class_group import ClassGroup, ClassMembership
from src.models.friendship import Friendship
from src.services.shared_challenge_service import SharedChallengeService
from flask import Flask
from datetime import datetime, timedelta

# Create test app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'

# Initialize database
init_db(app)

def run_tests():
    """Run all shared challenge tests"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("=" * 60)
        print("SHARED CHALLENGE SYSTEM TESTS")
        print("=" * 60)
        
        # Cleanup any existing test data first
        print("\n[Setup] Cleaning up any existing test data...")
        try:
            db.session.query(ChallengeParticipant).delete()
            db.session.query(SharedChallenge).delete()
            db.session.query(ClassMembership).delete()
            db.session.query(ClassGroup).delete()
            db.session.query(Friendship).delete()
            from src.models.gamification import StudentProgress
            db.session.query(StudentProgress).delete()
            db.session.query(Student).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("✓ Cleanup complete")
        except Exception as e:
            print(f"Note: {e}")
            db.session.rollback()
        
        # Test 1: Create test users
        print("\n[Test 1] Creating test users...")
        try:
            # Create teacher
            teacher_user = User(
                username='teacher1',
                email='teacher1@test.com'
            )
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            
            # Create students
            student1_user = User(username='student1', email='student1@test.com')
            student1_user.set_password('password123')
            db.session.add(student1_user)
            db.session.flush()
            
            student2_user = User(username='student2', email='student2@test.com')
            student2_user.set_password('password123')
            db.session.add(student2_user)
            db.session.flush()
            
            student3_user = User(username='student3', email='student3@test.com')
            student3_user.set_password('password123')
            db.session.add(student3_user)
            db.session.flush()
            
            # Create student profiles
            student1 = Student(
                user_id=student1_user.id,
                name='Student One',
                grade=5,
                avatar='😊'
            )
            db.session.add(student1)
            db.session.flush()
            
            student2 = Student(
                user_id=student2_user.id,
                name='Student Two',
                grade=5,
                avatar='😊'
            )
            db.session.add(student2)
            db.session.flush()
            
            student3 = Student(
                user_id=student3_user.id,
                name='Student Three',
                grade=5,
                avatar='😊'
            )
            db.session.add(student3)
            db.session.flush()
            
            # Create student progress (for XP and levels)
            from src.models.gamification import StudentProgress
            progress1 = StudentProgress(student_id=student1.id, total_xp=500, current_level=3)
            progress2 = StudentProgress(student_id=student2.id, total_xp=300, current_level=2)
            progress3 = StudentProgress(student_id=student3.id, total_xp=700, current_level=4)
            db.session.add_all([progress1, progress2, progress3])
            
            db.session.commit()
            print("✓ Created teacher and 3 students")
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 2: Create friend challenge
        print("\n[Test 2] Creating friend challenge...")
        try:
            # First, make students friends
            friendship = Friendship(
                requester_id=student1.id,
                addressee_id=student2.id,
                status='accepted'
            )
            db.session.add(friendship)
            db.session.commit()
            
            challenge_data = {
                'title': 'Multiplication Challenge',
                'description': 'Who can master multiplication fastest?',
                'challenge_type': 'friend',
                'mode': 'competitive',
                'skill_id': 5,
                'target_questions': 20,
                'target_accuracy': 0.9,
                'duration_hours': 24,
                'participant_ids': [student2.id, student3.id]
            }
            
            result, status = SharedChallengeService.create_challenge(student1.id, challenge_data)
            
            if result.get('success'):
                challenge = result['challenge']
                print(f"✓ Created challenge: {challenge['title']}")
                print(f"  - ID: {challenge['id']}")
                print(f"  - Participants: {challenge['participant_count']}")
                print(f"  - XP Reward: {challenge['xp_reward']}")
                challenge_id = challenge['id']
            else:
                print(f"✗ Error: {result.get('error')}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 3: Accept challenge
        print("\n[Test 3] Student 2 accepts challenge...")
        try:
            result, status = SharedChallengeService.accept_challenge(challenge_id, student2.id)
            
            if result.get('success'):
                print(f"✓ Challenge accepted by Student 2")
                print(f"  - Status: {result['participation']['status']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Update progress
        print("\n[Test 4] Updating challenge progress...")
        try:
            # Student 2 answers 10 questions, 9 correct
            for i in range(10):
                result, status = SharedChallengeService.update_progress(
                    challenge_id,
                    student2.id,
                    {'correct': i < 9}  # 9 out of 10 correct
                )
            
            if result.get('success'):
                progress = result['progress']
                print(f"✓ Progress updated for Student 2")
                print(f"  - Questions answered: {progress['questions_answered']}")
                print(f"  - Accuracy: {progress['accuracy']:.2%}")
                print(f"  - Completed: {progress['completed']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 5: Get challenge leaderboard
        print("\n[Test 5] Getting challenge leaderboard...")
        try:
            result, status = SharedChallengeService.get_challenge_leaderboard(challenge_id)
            
            if result.get('success'):
                leaderboard = result['leaderboard']
                print(f"✓ Leaderboard retrieved ({len(leaderboard)} participants)")
                for participant in leaderboard:
                    print(f"  - Rank #{participant['rank']}: {participant['student']['display_name']}")
                    print(f"    Questions: {participant['questions_answered']}, Accuracy: {participant['accuracy']:.2%}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Get student challenges
        print("\n[Test 6] Getting challenges for Student 1...")
        try:
            result, status = SharedChallengeService.get_student_challenges(student1.id)
            
            if result.get('success'):
                challenges = result['challenges']
                print(f"✓ Found {len(challenges)} challenge(s)")
                for ch in challenges:
                    print(f"  - {ch['title']}: {ch['participant_count']} participants")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 7: Create class challenge
        print("\n[Test 7] Creating class challenge...")
        try:
            # Create a class
            test_class = ClassGroup(
                name='Math Class 5A',
                description='5th grade math',
                teacher_id=teacher_user.id,
                grade_level=5,
                invite_code='TEST01'
            )
            db.session.add(test_class)
            db.session.flush()
            
            # Add students to class
            membership1 = ClassMembership(class_id=test_class.id, student_id=student1.id)
            membership2 = ClassMembership(class_id=test_class.id, student_id=student2.id)
            membership3 = ClassMembership(class_id=test_class.id, student_id=student3.id)
            db.session.add_all([membership1, membership2, membership3])
            db.session.commit()
            
            # Create teacher student profile (needed for creator_id)
            teacher_student = Student(
                user_id=teacher_user.id,
                name='Teacher One',
                grade=5,
                avatar='👨‍🏫'
            )
            db.session.add(teacher_student)
            db.session.commit()
            
            class_challenge_data = {
                'title': 'Class Division Challenge',
                'description': 'Practice division together!',
                'challenge_type': 'class',
                'mode': 'collaborative',
                'skill_id': 6,
                'target_questions': 15,
                'target_accuracy': 0.85,
                'duration_hours': 48,
                'class_id': test_class.id
            }
            
            result, status = SharedChallengeService.create_challenge(
                teacher_student.id,
                class_challenge_data
            )
            
            if result.get('success'):
                class_challenge = result['challenge']
                print(f"✓ Created class challenge: {class_challenge['title']}")
                print(f"  - Participants: {class_challenge['participant_count']}")
                print(f"  - Mode: {class_challenge['mode']}")
                class_challenge_id = class_challenge['id']
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 8: Decline challenge
        print("\n[Test 8] Student 3 declines friend challenge...")
        try:
            result, status = SharedChallengeService.decline_challenge(challenge_id, student3.id)
            
            if result.get('success'):
                print(f"✓ Challenge declined by Student 3")
                print(f"  - Status: {result['participation']['status']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 9: Complete challenge (meet criteria)
        print("\n[Test 9] Student 2 completes challenge...")
        try:
            # Answer 10 more questions, all correct (total: 20 questions, 19 correct = 95%)
            for i in range(10):
                result, status = SharedChallengeService.update_progress(
                    challenge_id,
                    student2.id,
                    {'correct': True}
                )
            
            if result.get('success'):
                progress = result['progress']
                print(f"✓ Challenge progress updated")
                print(f"  - Questions answered: {progress['questions_answered']}")
                print(f"  - Accuracy: {progress['accuracy']:.2%}")
                print(f"  - Completed: {progress['completed']}")
                print(f"  - Challenge completed: {result.get('challenge_completed')}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 10: Get challenge details
        print("\n[Test 10] Getting challenge details...")
        try:
            result, status = SharedChallengeService.get_challenge(challenge_id, student1.id)
            
            if result.get('success'):
                challenge = result['challenge']
                print(f"✓ Challenge details retrieved")
                print(f"  - Title: {challenge['title']}")
                print(f"  - Status: {challenge['status']}")
                print(f"  - Participants: {len(challenge['participants'])}")
                print(f"  - My participation: {challenge['my_participation']['status']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Delete challenge
        print("\n[Test 11] Deleting challenge (creator only)...")
        try:
            # Try to delete as non-creator (should fail)
            result, status = SharedChallengeService.delete_challenge(challenge_id, student2.id)
            
            if status == 403:
                print(f"✓ Non-creator correctly blocked from deleting")
            
            # Delete as creator (should succeed)
            result, status = SharedChallengeService.delete_challenge(challenge_id, student1.id)
            
            if result.get('success'):
                print(f"✓ Challenge deleted by creator")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 12: Cleanup
        print("\n[Test 12] Cleanup test data...")
        try:
            db.session.query(ChallengeParticipant).delete()
            db.session.query(SharedChallenge).delete()
            db.session.query(ClassMembership).delete()
            db.session.query(ClassGroup).delete()
            db.session.query(Friendship).delete()
            db.session.query(Student).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("✓ Test data cleaned up")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()

