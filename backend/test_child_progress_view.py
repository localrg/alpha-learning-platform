"""
Test Child Progress View System
Tests all parent viewing of child progress functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import db, init_db
from src.models.user import User
from src.models.student import Student
from src.models.parent import Parent, ParentChildLink
from src.models.assessment import Skill
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.class_group import ClassGroup
from src.models.gamification import StudentProgress
from src.models.achievement import Achievement, StudentAchievement
from src.models.streak import StreakTracking
from src.services.parent_service import ParentService
from src.services.parent_view_service import ParentViewService
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
    """Run all child progress view tests"""
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        print("=" * 60)
        print("CHILD PROGRESS VIEW SYSTEM TESTS")
        print("=" * 60)
        
        # Test 1: Create test data
        print("\n[Test 1] Creating test data...")
        try:
            # Create parent user
            parent_user = User(username='parent1', email='parent1@email.com', role='parent')
            parent_user.set_password('password123')
            db.session.add(parent_user)
            db.session.flush()
            
            # Create parent
            result, status = ParentService.create_parent_account(
                user_id=parent_user.id,
                name='Jane Smith',
                email='parent1@email.com'
            )
            parent_id = result['parent']['id']
            
            # Create student user
            student_user = User(username='student1', email='student1@email.com')
            student_user.set_password('password123')
            db.session.add(student_user)
            db.session.flush()
            
            # Create student
            student = Student(
                user_id=student_user.id,
                name='Student One',
                grade=5
            )
            db.session.add(student)
            db.session.flush()
            
            # Create student progress
            progress = StudentProgress(
                student_id=student.id,
                total_xp=1250,
                current_level=8
            )
            db.session.add(progress)
            
            # Create streak
            streak = StreakTracking(
                student_id=student.id,
                practice_streak=7,
                practice_streak_best=10,
                last_practice_date=datetime.utcnow().date()
            )
            db.session.add(streak)
            
            # Link parent to child
            result, status = ParentService.generate_invite_code(student.id)
            invite_code = result['invite_code']
            result, status = ParentService.link_child_by_code(parent_id, invite_code)
            
            # Create skills
            skill1 = Skill(
                name='Addition',
                subject_area='arithmetic',
                grade_level=5,
                description='Basic addition'
            )
            skill2 = Skill(
                name='Multiplication',
                subject_area='arithmetic',
                grade_level=5,
                description='Basic multiplication'
            )
            skill3 = Skill(
                name='Fractions',
                subject_area='fractions',
                grade_level=5,
                description='Working with fractions'
            )
            db.session.add_all([skill1, skill2, skill3])
            db.session.flush()
            
            # Create learning paths
            path1 = LearningPath(
                student_id=student.id,
                skill_id=skill1.id,
                current_accuracy=0.95,
                questions_answered=120,
                correct_answers=114,
                total_questions=120,
                mastery_achieved=True,
                mastery_date=datetime.utcnow() - timedelta(days=10),
                last_practiced=datetime.utcnow() - timedelta(days=5),
                status='mastered'
            )
            path2 = LearningPath(
                student_id=student.id,
                skill_id=skill2.id,
                current_accuracy=0.85,
                questions_answered=80,
                correct_answers=68,
                total_questions=80,
                mastery_achieved=False,
                last_practiced=datetime.utcnow() - timedelta(hours=2),
                status='in_progress'
            )
            path3 = LearningPath(
                student_id=student.id,
                skill_id=skill3.id,
                current_accuracy=0.65,
                questions_answered=40,
                correct_answers=26,
                total_questions=40,
                mastery_achieved=False,
                last_practiced=datetime.utcnow() - timedelta(days=1),
                status='in_progress'
            )
            db.session.add_all([path1, path2, path3])
            db.session.flush()
            
            # Create student sessions (last 30 days)
            for i in range(10):
                session = StudentSession(
                    student_id=student.id,
                    skill_id=skill2.id,
                    questions_answered=15,
                    questions_correct=13,
                    accuracy=0.87,
                    started_at=datetime.utcnow() - timedelta(days=i),
                    ended_at=datetime.utcnow() - timedelta(days=i) + timedelta(minutes=12)
                )
                db.session.add(session)
            
            # Create assignment (need teacher_id)
            teacher_user = User(username='teacher1', email='teacher1@email.com', role='teacher')
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            
            assignment = Assignment(
                teacher_id=teacher_user.id,
                title='Multiplication Practice',
                description='Practice multiplication',
                skill_ids=[skill2.id],
                question_count=20,
                difficulty='medium',
                due_date=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(assignment)
            db.session.flush()
            
            # Create assignment student
            assignment_student = AssignmentStudent(
                assignment_id=assignment.id,
                student_id=student.id,
                status='completed',
                questions_correct=18,
                accuracy=0.90,
                questions_answered=20,
                started_at=datetime.utcnow() - timedelta(hours=3),
                completed_at=datetime.utcnow() - timedelta(hours=2)
            )
            db.session.add(assignment_student)
            
            # Create achievement
            achievement = Achievement(
                name='Week Warrior',
                description='Practice 7 days in a row',
                category='consistency',
                tier='bronze',
                requirement_type='streak',
                requirement_value=7,
                icon_emoji='🔥',
                xp_reward=50
            )
            db.session.add(achievement)
            db.session.flush()
            
            # Create student achievement
            student_achievement = StudentAchievement(
                student_id=student.id,
                achievement_id=achievement.id,
                progress=7,
                unlocked_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(student_achievement)
            
            db.session.commit()
            
            print(f"✓ Test data created")
            print(f"  - Parent ID: {parent_id}")
            print(f"  - Student ID: {student.id}")
            print(f"  - Skills: 3 (1 mastered, 2 in progress)")
            print(f"  - Sessions: 10")
            print(f"  - Assignments: 1 completed")
            print(f"  - Achievements: 1 earned")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Get child overview
        print("\n[Test 2] Getting child overview...")
        try:
            result, status = ParentViewService.get_child_overview(parent_id, student.id)
            
            if result.get('success'):
                metrics = result['metrics']
                print(f"✓ Overview retrieved")
                print(f"  - Accuracy: {metrics['accuracy']}")
                print(f"  - Questions: {metrics['questions_answered']}")
                print(f"  - Time: {metrics['time_spent_hours']} hours")
                print(f"  - Level: {metrics['level']}")
                print(f"  - XP: {metrics['xp']}")
                print(f"  - Skills mastered: {metrics['skills_mastered']}/{metrics['total_skills']}")
                print(f"  - Streak: {metrics['current_streak']} days")
                print(f"  - Assignments: {metrics['assignments_completed']}/{metrics['total_assignments']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Get child skills (all)
        print("\n[Test 3] Getting all child skills...")
        try:
            result, status = ParentViewService.get_child_skills(parent_id, student.id, 'all')
            
            if result.get('success'):
                print(f"✓ Skills retrieved")
                print(f"  - Total: {result['count']}")
                for skill in result['skills']:
                    print(f"  - {skill['skill_name']}: {skill['accuracy']*100:.0f}% ({skill['mastery_status']})")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Get child skills (mastered only)
        print("\n[Test 4] Getting mastered skills...")
        try:
            result, status = ParentViewService.get_child_skills(parent_id, student.id, 'mastered')
            
            if result.get('success'):
                print(f"✓ Mastered skills retrieved")
                print(f"  - Count: {result['count']}")
                if result['count'] == 1:
                    print(f"  ✓ Correct count (expected 1)")
                else:
                    print(f"  ✗ Expected 1, got {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 5: Get child skills (in progress)
        print("\n[Test 5] Getting in-progress skills...")
        try:
            result, status = ParentViewService.get_child_skills(parent_id, student.id, 'in_progress')
            
            if result.get('success'):
                print(f"✓ In-progress skills retrieved")
                print(f"  - Count: {result['count']}")
                if result['count'] == 2:
                    print(f"  ✓ Correct count (expected 2)")
                else:
                    print(f"  ✗ Expected 2, got {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Get child skills (needs practice)
        print("\n[Test 6] Getting skills that need practice...")
        try:
            result, status = ParentViewService.get_child_skills(parent_id, student.id, 'needs_practice')
            
            if result.get('success'):
                print(f"✓ Skills needing practice retrieved")
                print(f"  - Count: {result['count']}")
                if result['count'] == 1:
                    print(f"  ✓ Correct count (expected 1 with accuracy < 70%)")
                else:
                    print(f"  ✗ Expected 1, got {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 7: Get child activity (30 days)
        print("\n[Test 7] Getting child activity (last 30 days)...")
        try:
            result, status = ParentViewService.get_child_activity(parent_id, student.id, 30)
            
            if result.get('success'):
                print(f"✓ Activity feed retrieved")
                print(f"  - Total activities: {result['count']}")
                
                # Count by type
                types = {}
                for activity in result['activities']:
                    types[activity['type']] = types.get(activity['type'], 0) + 1
                
                for activity_type, count in types.items():
                    print(f"  - {activity_type}: {count}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 8: Get child activity (7 days)
        print("\n[Test 8] Getting child activity (last 7 days)...")
        try:
            result, status = ParentViewService.get_child_activity(parent_id, student.id, 7)
            
            if result.get('success'):
                print(f"✓ Recent activity retrieved")
                print(f"  - Total activities: {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 9: Get child assignments (all)
        print("\n[Test 9] Getting all child assignments...")
        try:
            result, status = ParentViewService.get_child_assignments(parent_id, student.id, 'all')
            
            if result.get('success'):
                print(f"✓ Assignments retrieved")
                print(f"  - Total: {result['count']}")
                for assignment in result['assignments']:
                    print(f"  - {assignment['title']}: {assignment['status']} (Correct: {assignment['questions_correct']}/{assignment['questions_answered']})")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 10: Get child assignments (completed)
        print("\n[Test 10] Getting completed assignments...")
        try:
            result, status = ParentViewService.get_child_assignments(parent_id, student.id, 'completed')
            
            if result.get('success'):
                print(f"✓ Completed assignments retrieved")
                print(f"  - Count: {result['count']}")
                if result['count'] == 1:
                    print(f"  ✓ Correct count (expected 1)")
                else:
                    print(f"  ✗ Expected 1, got {result['count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Get child achievements
        print("\n[Test 11] Getting child achievements...")
        try:
            result, status = ParentViewService.get_child_achievements(parent_id, student.id)
            
            if result.get('success'):
                print(f"✓ Achievements retrieved")
                print(f"  - Total: {result['count']}")
                for achievement in result['achievements']:
                    print(f"  - {achievement['name']}: {achievement['description']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 12: Test unauthorized access
        print("\n[Test 12] Testing unauthorized access...")
        try:
            # Create another parent
            parent2_user = User(username='parent2', email='parent2@email.com', role='parent')
            parent2_user.set_password('password123')
            db.session.add(parent2_user)
            db.session.flush()
            
            result, status = ParentService.create_parent_account(
                user_id=parent2_user.id,
                name='John Doe',
                email='parent2@email.com'
            )
            parent2_id = result['parent']['id']
            
            # Try to access student without link
            result, status = ParentViewService.get_child_overview(parent2_id, student.id)
            
            if status == 403:
                print(f"✓ Correctly denied unauthorized access")
            else:
                print(f"✗ Should deny unauthorized access")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 13: Test non-existent student
        print("\n[Test 13] Testing with non-existent student...")
        try:
            result, status = ParentViewService.get_child_overview(parent_id, 9999)
            
            if status == 403 or status == 404:
                print(f"✓ Correctly handled non-existent student")
            else:
                print(f"✗ Should return error for non-existent student")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 14: Test verify_parent_child_link
        print("\n[Test 14] Testing verify_parent_child_link...")
        try:
            # Valid link
            is_linked = ParentViewService.verify_parent_child_link(parent_id, student.id)
            if is_linked:
                print(f"✓ Correctly verified valid link")
            else:
                print(f"✗ Should verify valid link")
            
            # Invalid link
            is_linked = ParentViewService.verify_parent_child_link(parent2_id, student.id)
            if not is_linked:
                print(f"✓ Correctly rejected invalid link")
            else:
                print(f"✗ Should reject invalid link")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 15: Test with no data
        print("\n[Test 15] Testing with student with no data...")
        try:
            # Create new student with no data
            student2_user = User(username='student2', email='student2@email.com')
            student2_user.set_password('password123')
            db.session.add(student2_user)
            db.session.flush()
            
            student2 = Student(
                user_id=student2_user.id,
                name='Student Two',
                grade=6
            )
            db.session.add(student2)
            db.session.flush()
            
            # Link to parent
            result, status = ParentService.generate_invite_code(student2.id)
            invite_code = result['invite_code']
            result, status = ParentService.link_child_by_code(parent_id, invite_code)
            
            # Get overview
            result, status = ParentViewService.get_child_overview(parent_id, student2.id)
            
            if result.get('success'):
                metrics = result['metrics']
                print(f"✓ Handled student with no data")
                print(f"  - Accuracy: {metrics['accuracy']}")
                print(f"  - Questions: {metrics['questions_answered']}")
                if metrics['questions_answered'] == 0:
                    print(f"  ✓ Correctly shows 0 for empty data")
                else:
                    print(f"  ✗ Should show 0 for empty data")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()

