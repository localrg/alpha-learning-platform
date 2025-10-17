"""
Comprehensive tests for Communication Tools and Goal Setting (Steps 8.4 & 8.5).
Tests messaging, goal creation, tracking, and authorization.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from src.database import db, init_db
from src.models.user import User
from src.models.student import Student
from src.models.parent import Parent, ParentChildLink
from src.models.assessment import Skill
from src.models.learning_path import LearningPath
from src.models.class_group import ClassGroup, ClassMembership
from src.models.gamification import StudentProgress
from src.models.streak import StreakTracking
from src.models.assignment_model import Assignment, AssignmentStudent
from src.services.parent_service import ParentService
from src.services.communication_service import CommunicationService
from src.services.goal_service import GoalService
from datetime import datetime, timedelta


def run_tests():
    """Run all communication and goal tests"""
    print("=" * 60)
    print("COMMUNICATION & GOAL SETTING TESTS")
    print("=" * 60)
    
    # Create Flask app and initialize database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
    
    with app.app_context():
        try:
            # Drop and recreate all tables
            db.drop_all()
            db.session.commit()
            db.create_all()
            db.session.commit()
            
            # Test 1: Create test data
            print("[Test 1] Creating test data...")
            
            # Create parent
            parent_user = User(username='parent1', email='parent1@email.com', role='parent')
            parent_user.set_password('password123')
            db.session.add(parent_user)
            db.session.flush()
            
            parent = Parent(
                user_id=parent_user.id,
                name='Test Parent',
                email='parent1@email.com'
            )
            db.session.add(parent)
            db.session.flush()
            parent_id = parent.id
            
            # Create student
            student_user = User(username='student1', email='student1@email.com', role='student')
            student_user.set_password('password123')
            db.session.add(student_user)
            db.session.flush()
            
            student = Student(
                user_id=student_user.id,
                name='Test Student',
                grade=5
            )
            db.session.add(student)
            db.session.flush()
            student_id = student.id
            
            # Create student progress
            progress = StudentProgress(
                student_id=student.id,
                total_xp=2000,
                current_level=10
            )
            db.session.add(progress)
            
            # Create streak
            streak = StreakTracking(
                student_id=student.id,
                practice_streak=5,
                practice_streak_best=10,
                last_practice_date=datetime.utcnow().date()
            )
            db.session.add(streak)
            
            # Link parent to child
            result, status = ParentService.generate_invite_code(student.id)
            invite_code = result['invite_code']
            result, status = ParentService.link_child_by_code(parent_id, invite_code)
            
            # Create teacher
            teacher_user = User(username='teacher1', email='teacher1@email.com', role='teacher')
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            teacher_id = teacher_user.id
            
            # Create class and add student
            class_group = ClassGroup(
                teacher_id=teacher_id,
                name='Math Class',
                grade_level=5,
                invite_code='MATH123'
            )
            db.session.add(class_group)
            db.session.flush()
            
            membership = ClassMembership(
                class_id=class_group.id,
                student_id=student_id,
                role='student'
            )
            db.session.add(membership)
            
            # Create skill for goals
            skill = Skill(
                name='Addition',
                subject_area='arithmetic',
                grade_level=5,
                description='Basic addition'
            )
            db.session.add(skill)
            db.session.flush()
            
            # Create learning path
            path = LearningPath(
                student_id=student.id,
                skill_id=skill.id,
                current_accuracy=0.75,
                questions_answered=100,
                correct_answers=75,
                total_questions=100,
                mastery_achieved=False,
                last_practiced=datetime.utcnow(),
                status='in_progress'
            )
            db.session.add(path)
            
            db.session.commit()
            
            print("✓ Test data created")
            print(f"  - Parent ID: {parent_id}")
            print(f"  - Student ID: {student_id}")
            print(f"  - Teacher ID: {teacher_id}")
            print(f"  - Skill ID: {skill.id}")
            
            # COMMUNICATION TESTS
            
            # Test 2: Send message from parent to teacher
            print("[Test 2] Sending message from parent to teacher...")
            result, status = CommunicationService.send_message(
                parent_id=parent_id,
                teacher_id=teacher_id,
                student_id=student_id,
                subject='Question about homework',
                message='Can you clarify the assignment?',
                message_type='question'
            )
            
            if result.get('success'):
                message_id = result['message']['id']
                print("✓ Message sent successfully")
                print(f"  - Message ID: {message_id}")
                print(f"  - Subject: {result['message']['subject']}")
                print(f"  - Type: {result['message']['message_type']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 3: Get messages for parent
            print("[Test 3] Getting messages for parent...")
            result, status = CommunicationService.get_messages(parent_id, filter_type='all')
            
            if result.get('success'):
                print("✓ Messages retrieved")
                print(f"  - Count: {len(result['messages'])}")
                if result['messages']:
                    print(f"  - First message subject: {result['messages'][0]['subject']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 4: Reply to message
            print("[Test 4] Replying to message...")
            result, status = CommunicationService.reply_to_message(
                parent_id=parent_id,
                message_id=message_id,
                reply_text='Thank you for the clarification!'
            )
            
            if result.get('success'):
                print("✓ Reply sent successfully")
                print(f"  - Reply ID: {result['message']['id']}")
                print(f"  - Replied to: {result['message']['replied_to_id']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 5: Get message with thread
            print("[Test 5] Getting message with thread...")
            result, status = CommunicationService.get_message(parent_id, message_id)
            
            if result.get('success'):
                print("✓ Message and thread retrieved")
                print(f"  - Thread length: {len(result['thread'])}")
                if len(result['thread']) >= 2:
                    print("  ✓ Thread includes original and reply")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 6: Unread count
            print("[Test 6] Getting unread count...")
            result, status = CommunicationService.get_unread_count(parent_id)
            
            if result.get('success'):
                print("✓ Unread count retrieved")
                print(f"  - Unread: {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 7: Unauthorized message (student not in teacher's class)
            print("[Test 7] Testing unauthorized messaging...")
            
            # Create another teacher
            teacher_user2 = User(username='teacher2', email='teacher2@email.com', role='teacher')
            teacher_user2.set_password('password123')
            db.session.add(teacher_user2)
            db.session.flush()
            
            result, status = CommunicationService.send_message(
                parent_id=parent_id,
                teacher_id=teacher_user2.id,
                student_id=student_id,
                subject='Test',
                message='Test',
                message_type='question'
            )
            
            if not result.get('success') and status == 400:
                print("✓ Correctly denied unauthorized messaging")
            else:
                print("✗ Should have denied unauthorized messaging")
            
            # GOAL SETTING TESTS
            
            # Test 8: Create skill mastery goal
            print("[Test 8] Creating skill mastery goal...")
            result, status = GoalService.create_goal(
                student_id=student_id,
                created_by_id=parent_id,
                created_by_type='parent',
                goal_type='skill_mastery',
                title='Master Addition',
                description='Achieve 90% accuracy in addition',
                target_value=90.0,
                skill_id=skill.id
            )
            
            if result.get('success'):
                skill_goal_id = result['goal']['id']
                print("✓ Skill mastery goal created")
                print(f"  - Goal ID: {skill_goal_id}")
                print(f"  - Title: {result['goal']['title']}")
                print(f"  - Current progress: {result['goal']['progress_percent']}%")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 9: Create streak goal
            print("[Test 9] Creating streak goal...")
            result, status = GoalService.create_goal(
                student_id=student_id,
                created_by_id=student_user.id,
                created_by_type='student',
                goal_type='streak',
                title='10-Day Streak',
                description='Maintain a 10-day practice streak',
                target_value=10.0
            )
            
            if result.get('success'):
                streak_goal_id = result['goal']['id']
                print("✓ Streak goal created")
                print(f"  - Goal ID: {streak_goal_id}")
                print(f"  - Current progress: {result['goal']['progress_percent']}%")
                print(f"  - Current value: {result['goal']['current_value']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 10: Create custom goal
            print("[Test 10] Creating custom goal...")
            result, status = GoalService.create_goal(
                student_id=student_id,
                created_by_id=parent_id,
                created_by_type='parent',
                goal_type='custom',
                title='Complete homework on time',
                description='Submit all homework by due date',
                target_value=100.0,
                due_date=datetime.utcnow() + timedelta(days=30)
            )
            
            if result.get('success'):
                custom_goal_id = result['goal']['id']
                print("✓ Custom goal created")
                print(f"  - Goal ID: {custom_goal_id}")
                print(f"  - Due date: {result['goal']['due_date']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 11: Get student goals
            print("[Test 11] Getting student goals...")
            result, status = GoalService.get_student_goals(student_id, status='all')
            
            if result.get('success'):
                print("✓ Student goals retrieved")
                print(f"  - Total goals: {len(result['goals'])}")
                print(f"  - Active goals: {sum(1 for g in result['goals'] if g['status'] == 'active')}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 12: Add note to goal
            print("[Test 12] Adding note to goal...")
            result, status = GoalService.add_note(
                goal_id=skill_goal_id,
                user_id=parent_id,
                user_type='parent',
                note='Keep up the great work!'
            )
            
            if result.get('success'):
                print("✓ Note added to goal")
                print(f"  - Note: {result['note']['note']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 13: Update custom goal progress manually
            print("[Test 13] Updating custom goal progress...")
            result, status = GoalService.add_manual_progress(
                goal_id=custom_goal_id,
                value=50.0,
                note='Halfway there!'
            )
            
            if result.get('success'):
                print("✓ Custom goal progress updated")
                print(f"  - Progress: {result['goal']['progress_percent']}%")
                print(f"  - Status: {result['goal']['status']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 14: Complete custom goal
            print("[Test 14] Completing custom goal...")
            result, status = GoalService.add_manual_progress(
                goal_id=custom_goal_id,
                value=100.0,
                note='Goal achieved!'
            )
            
            if result.get('success'):
                print("✓ Custom goal completed")
                print(f"  - Progress: {result['goal']['progress_percent']}%")
                print(f"  - Status: {result['goal']['status']}")
                if result['goal']['status'] == 'completed':
                    print("  ✓ Status correctly set to completed")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 15: Update goal
            print("[Test 15] Updating goal...")
            result, status = GoalService.update_goal(
                goal_id=skill_goal_id,
                title='Master Addition (Updated)',
                target_value=95.0
            )
            
            if result.get('success'):
                print("✓ Goal updated")
                print(f"  - New title: {result['goal']['title']}")
                print(f"  - New target: {result['goal']['target_value']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 16: Get goal with notes and progress
            print("[Test 16] Getting goal with notes and progress...")
            result, status = GoalService.get_goal(skill_goal_id)
            
            if result.get('success'):
                print("✓ Goal details retrieved")
                print(f"  - Notes: {len(result['goal']['notes'])}")
                print(f"  - Progress history: {len(result['goal']['progress_history'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 17: Cannot update completed goal
            print("[Test 17] Testing completed goal update restriction...")
            result, status = GoalService.update_goal(
                goal_id=custom_goal_id,
                title='Should not update'
            )
            
            if not result.get('success') and status == 400:
                print("✓ Correctly prevented updating completed goal")
            else:
                print("✗ Should have prevented updating completed goal")
            
            # Test 18: Delete goal
            print("[Test 18] Deleting goal...")
            result, status = GoalService.delete_goal(custom_goal_id)
            
            if result.get('success'):
                print("✓ Goal deleted successfully")
                
                # Verify deletion
                result, status = GoalService.get_goal(custom_goal_id)
                if not result.get('success'):
                    print("  ✓ Goal no longer exists")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 19: Automatic goal progress tracking (streak)
            print("[Test 19] Testing automatic progress tracking...")
            
            # Update streak
            streak.practice_streak = 8
            db.session.commit()
            
            # Trigger goal update
            GoalService._update_goal_progress(streak_goal_id)
            
            result, status = GoalService.get_goal(streak_goal_id)
            if result.get('success'):
                print("✓ Automatic progress tracking working")
                print(f"  - Current value: {result['goal']['current_value']}")
                print(f"  - Progress: {result['goal']['progress_percent']}%")
                if result['goal']['current_value'] == 8:
                    print("  ✓ Progress correctly updated from streak")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 20: Unauthorized goal creation
            print("[Test 20] Testing unauthorized goal creation...")
            
            # Try to create goal for student without parent link
            fake_parent_id = 999
            result, status = GoalService.create_goal(
                student_id=student_id,
                created_by_id=fake_parent_id,
                created_by_type='parent',
                goal_type='custom',
                title='Unauthorized',
                description='Should fail',
                target_value=100.0
            )
            
            if not result.get('success') and status == 403:
                print("✓ Correctly denied unauthorized goal creation")
            else:
                print("✗ Should have denied unauthorized goal creation")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED!")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()

