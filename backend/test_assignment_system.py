"""
Test Assignment System
Tests all assignment functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import db, init_db
from src.models.user import User
from src.models.teacher import Teacher
from src.models.student import Student
from src.models.assessment import Skill
from src.models.class_group import ClassGroup, ClassMembership
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.gamification import StudentProgress
from src.services.assignment_service import AssignmentService
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
    """Run all assignment tests"""
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        print("=" * 60)
        print("ASSIGNMENT SYSTEM TESTS")
        print("=" * 60)
        
        # Test 1: Create test data
        print("\n[Test 1] Creating test data...")
        try:
            # Create teacher
            teacher_user = User(username='teacher1', email='teacher1@school.edu', role='teacher')
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            
            teacher = Teacher(
                user_id=teacher_user.id,
                name='Ms. Johnson',
                email='teacher1@school.edu'
            )
            db.session.add(teacher)
            
            # Create class
            test_class = ClassGroup(
                name='Math 5A',
                teacher_id=teacher_user.id,
                grade_level=5,
                invite_code='TEST01'
            )
            db.session.add(test_class)
            db.session.flush()
            
            # Create students
            students = []
            for i in range(1, 4):
                student_user = User(username=f'student{i}', email=f'student{i}@test.com')
                student_user.set_password('password123')
                db.session.add(student_user)
                db.session.flush()
                
                student = Student(
                    user_id=student_user.id,
                    name=f'Student {i}',
                    grade=5
                )
                db.session.add(student)
                db.session.flush()
                
                # Create progress
                progress = StudentProgress(
                    student_id=student.id,
                    total_xp=100 * i,
                    current_level=i
                )
                db.session.add(progress)
                
                # Add to class
                membership = ClassMembership(
                    class_id=test_class.id,
                    student_id=student.id
                )
                db.session.add(membership)
                
                students.append(student)
            
            # Create skills
            skills = []
            for skill_name in ['Multiplication', 'Division']:
                skill = Skill(
                    name=skill_name,
                    description=f'{skill_name} skill',
                    grade_level=5,
                    subject_area='arithmetic'
                )
                db.session.add(skill)
                db.session.flush()
                skills.append(skill)
            
            db.session.commit()
            print(f"✓ Created teacher, class, {len(students)} students, {len(skills)} skills")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Create class assignment
        print("\n[Test 2] Creating class assignment...")
        try:
            assignment_data = {
                'title': 'Fractions Practice',
                'description': 'Practice adding and subtracting fractions',
                'class_id': test_class.id,
                'skill_ids': [skills[0].id, skills[1].id],
                'question_count': 15,
                'difficulty': 'medium',
                'due_date': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            result, status = AssignmentService.create_assignment(teacher_user.id, assignment_data)
            
            if result.get('success'):
                assignment_id = result['assignment']['id']
                print(f"✓ Created assignment: {result['assignment']['title']}")
                print(f"  - ID: {assignment_id}")
                print(f"  - Students: {result['assignment']['student_count']}")
                print(f"  - Questions: {result['assignment']['question_count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
                return
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Get teacher assignments
        print("\n[Test 3] Getting teacher assignments...")
        try:
            assignments = AssignmentService.get_teacher_assignments(teacher_user.id)
            
            print(f"✓ Retrieved {len(assignments)} assignments")
            for assignment in assignments:
                print(f"  - {assignment['title']}: {assignment['completed_students']}/{assignment['total_students']} completed")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Get student assignments
        print("\n[Test 4] Getting student assignments...")
        try:
            student_id = students[0].id
            assignments = AssignmentService.get_student_assignments(student_id)
            
            print(f"✓ Retrieved {len(assignments)} assignments for Student 1")
            for assignment in assignments:
                print(f"  - {assignment['title']}: {assignment['student_status']}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 5: Start assignment
        print("\n[Test 5] Starting assignment...")
        try:
            student_id = students[0].id
            result, status = AssignmentService.start_assignment(assignment_id, student_id)
            
            if result.get('success'):
                print(f"✓ Assignment started")
                print(f"  - Status: {result['progress']['status']}")
                print(f"  - Started at: {result['progress']['started_at']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Get assignment progress
        print("\n[Test 6] Getting assignment progress...")
        try:
            student_id = students[0].id
            result, status = AssignmentService.get_student_assignment_progress(assignment_id, student_id)
            
            if result.get('success'):
                progress = result['progress']
                print(f"✓ Progress retrieved")
                print(f"  - Status: {progress['status']}")
                print(f"  - Questions answered: {progress['questions_answered']}/{progress['questions_total']}")
                print(f"  - Accuracy: {progress['accuracy']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 7: Simulate answering questions
        print("\n[Test 7] Simulating question answering...")
        try:
            student_id = students[0].id
            assignment_student = AssignmentStudent.query.filter_by(
                assignment_id=assignment_id,
                student_id=student_id
            ).first()
            
            # Simulate answering 15 questions with 80% accuracy
            assignment_student.questions_answered = 15
            assignment_student.questions_correct = 12
            assignment_student.accuracy = 0.8
            assignment_student.time_spent = 600  # 10 minutes
            db.session.commit()
            
            print(f"✓ Simulated answering {assignment_student.questions_answered} questions")
            print(f"  - Correct: {assignment_student.questions_correct}")
            print(f"  - Accuracy: {assignment_student.accuracy}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 8: Complete assignment
        print("\n[Test 8] Completing assignment...")
        try:
            student_id = students[0].id
            result, status = AssignmentService.complete_assignment(assignment_id, student_id)
            
            if result.get('success'):
                print(f"✓ Assignment completed")
                print(f"  - Accuracy: {result['accuracy']}")
                print(f"  - XP earned: {result['xp_earned']}")
                print(f"  - Questions correct: {result['questions_correct']}/{result['questions_total']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 9: Get assignment stats
        print("\n[Test 9] Getting assignment statistics...")
        try:
            stats = AssignmentService.get_assignment_stats(assignment_id, teacher_user.id)
            
            print(f"✓ Assignment stats retrieved")
            print(f"  - Total students: {stats['total_students']}")
            print(f"  - Completed: {stats['completed_students']}")
            print(f"  - In progress: {stats['in_progress_students']}")
            print(f"  - Not started: {stats['not_started_students']}")
            print(f"  - Completion rate: {stats['completion_rate']:.0%}")
            print(f"  - Avg accuracy: {stats['avg_accuracy']}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 10: Update assignment
        print("\n[Test 10] Updating assignment...")
        try:
            update_data = {
                'title': 'Fractions Practice (Updated)',
                'description': 'Updated description',
                'due_date': (datetime.utcnow() + timedelta(days=10)).isoformat()
            }
            
            result, status = AssignmentService.update_assignment(assignment_id, teacher_user.id, update_data)
            
            if result.get('success'):
                print(f"✓ Assignment updated")
                print(f"  - New title: {result['assignment']['title']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Try to update skills after students started (should fail)
        print("\n[Test 11] Testing update restrictions...")
        try:
            update_data = {
                'skill_ids': [skills[0].id]  # Try to change skills
            }
            
            result, status = AssignmentService.update_assignment(assignment_id, teacher_user.id, update_data)
            
            if status == 400:
                print(f"✓ Update correctly blocked: {result.get('error')}")
            else:
                print(f"✗ Update should have been blocked!")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 12: Create individual assignment
        print("\n[Test 12] Creating individual assignment...")
        try:
            assignment_data = {
                'title': 'Extra Practice for Student 2',
                'description': 'Additional practice',
                'student_ids': [students[1].id],
                'skill_ids': [skills[0].id],
                'question_count': 10,
                'difficulty': 'easy'
            }
            
            result, status = AssignmentService.create_assignment(teacher_user.id, assignment_data)
            
            if result.get('success'):
                individual_assignment_id = result['assignment']['id']
                print(f"✓ Created individual assignment")
                print(f"  - Students: {result['assignment']['student_count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 13: Try to delete completed assignment (should fail)
        print("\n[Test 13] Testing delete restrictions...")
        try:
            result, status = AssignmentService.delete_assignment(assignment_id, teacher_user.id)
            
            if status == 400:
                print(f"✓ Delete correctly blocked: {result.get('error')}")
            else:
                print(f"✗ Delete should have been blocked!")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 14: Delete assignment with no completions
        print("\n[Test 14] Deleting assignment with no completions...")
        try:
            result, status = AssignmentService.delete_assignment(individual_assignment_id, teacher_user.id)
            
            if result.get('success'):
                print(f"✓ Assignment deleted successfully")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 15: Test unauthorized access
        print("\n[Test 15] Testing unauthorized access...")
        try:
            # Create another teacher
            other_teacher_user = User(username='teacher2', email='teacher2@school.edu', role='teacher')
            other_teacher_user.set_password('password123')
            db.session.add(other_teacher_user)
            db.session.commit()
            
            # Try to access first teacher's assignment
            result, status = AssignmentService.get_assignment(assignment_id, other_teacher_user.id, 'teacher')
            
            if status == 403:
                print("✓ Unauthorized access correctly blocked")
            else:
                print("✗ Unauthorized access not blocked!")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 16: Test XP calculation
        print("\n[Test 16] Testing XP calculation...")
        try:
            # Create test assignment
            test_assignment = Assignment(
                teacher_id=teacher_user.id,
                title='Test',
                skill_ids=[skills[0].id],
                question_count=10,
                due_date=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(test_assignment)
            db.session.flush()
            
            # Create test assignment_student
            test_as = AssignmentStudent(
                assignment_id=test_assignment.id,
                student_id=students[0].id,
                status='completed',
                questions_answered=10,
                questions_correct=9,
                accuracy=0.9,
                completed_at=datetime.utcnow()
            )
            db.session.add(test_as)
            db.session.commit()
            
            # Calculate XP
            xp = AssignmentService._calculate_xp(test_assignment, test_as)
            
            # Base: 10 * 10 = 100
            # Accuracy bonus (90%): 100 * 0.5 = 50
            # On-time bonus: 100 * 0.2 = 20
            # Total: 170
            
            print(f"✓ XP calculation tested")
            print(f"  - Base XP: 100")
            print(f"  - Accuracy bonus: 50")
            print(f"  - On-time bonus: 20")
            print(f"  - Total XP: {xp}")
            
            if xp == 170:
                print(f"  ✓ XP calculation correct!")
            else:
                print(f"  ✗ XP calculation incorrect (expected 170, got {xp})")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()

