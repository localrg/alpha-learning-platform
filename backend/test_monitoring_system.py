"""
Test Monitoring System
Tests all monitoring and real-time tracking functionality
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
from src.models.learning_path import LearningPath
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.student_session import StudentSession
from src.services.monitoring_service import MonitoringService
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
    """Run all monitoring tests"""
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        print("=" * 60)
        print("MONITORING SYSTEM TESTS")
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
            
            # Create skills
            skills = []
            for skill_name in ['Multiplication', 'Division', 'Fractions']:
                skill = Skill(
                    name=skill_name,
                    description=f'{skill_name} skill',
                    grade_level=5,
                    subject_area='arithmetic'
                )
                db.session.add(skill)
                db.session.flush()
                skills.append(skill)
            
            # Create students with varying performance
            students = []
            for i in range(1, 6):
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
                
                # Add to class
                membership = ClassMembership(
                    class_id=test_class.id,
                    student_id=student.id
                )
                db.session.add(membership)
                
                # Create learning paths with varying accuracy
                for skill in skills:
                    # Student 1: High performer (90%)
                    # Student 2: Medium performer (75%)
                    # Student 3: Struggling (60%)
                    # Student 4: Very struggling (50%)
                    # Student 5: Inactive (no recent activity)
                    accuracy = 0.9 if i == 1 else 0.75 if i == 2 else 0.6 if i == 3 else 0.5
                    
                    path = LearningPath(
                        student_id=student.id,
                        skill_id=skill.id,
                        current_accuracy=accuracy,
                        questions_answered=20,
                        correct_answers=int(20 * accuracy),
                        total_questions=20
                    )
                    db.session.add(path)
                
                students.append(student)
            
            db.session.commit()
            print(f"✓ Created teacher, class, {len(students)} students, {len(skills)} skills")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Create sessions with varying activity
        print("\n[Test 2] Creating student sessions...")
        try:
            # Student 1: Active now
            session1 = StudentSession(
                student_id=students[0].id,
                skill_id=skills[0].id,
                started_at=datetime.utcnow() - timedelta(minutes=3),
                last_activity_at=datetime.utcnow() - timedelta(seconds=30),
                questions_answered=5,
                questions_correct=5,
                accuracy=1.0,
                is_active=True
            )
            db.session.add(session1)
            
            # Student 2: Active now
            session2 = StudentSession(
                student_id=students[1].id,
                skill_id=skills[1].id,
                started_at=datetime.utcnow() - timedelta(minutes=10),
                last_activity_at=datetime.utcnow() - timedelta(minutes=1),
                questions_answered=8,
                questions_correct=6,
                accuracy=0.75,
                is_active=True
            )
            db.session.add(session2)
            
            # Student 3: Last active 2 days ago
            session3 = StudentSession(
                student_id=students[2].id,
                skill_id=skills[2].id,
                started_at=datetime.utcnow() - timedelta(days=2, hours=1),
                last_activity_at=datetime.utcnow() - timedelta(days=2),
                questions_answered=10,
                questions_correct=6,
                accuracy=0.6,
                is_active=False,
                ended_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(session3)
            
            # Student 4: Last active 5 days ago
            session4 = StudentSession(
                student_id=students[3].id,
                skill_id=skills[0].id,
                started_at=datetime.utcnow() - timedelta(days=5, hours=1),
                last_activity_at=datetime.utcnow() - timedelta(days=5),
                questions_answered=10,
                questions_correct=5,
                accuracy=0.5,
                is_active=False,
                ended_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(session4)
            
            # Student 5: Last active 10 days ago (inactive)
            session5 = StudentSession(
                student_id=students[4].id,
                skill_id=skills[1].id,
                started_at=datetime.utcnow() - timedelta(days=10, hours=1),
                last_activity_at=datetime.utcnow() - timedelta(days=10),
                questions_answered=5,
                questions_correct=3,
                accuracy=0.6,
                is_active=False,
                ended_at=datetime.utcnow() - timedelta(days=10)
            )
            db.session.add(session5)
            
            db.session.commit()
            print(f"✓ Created 5 sessions with varying activity levels")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Get active students
        print("\n[Test 3] Getting active students...")
        try:
            active_students = MonitoringService.get_active_students(test_class.id)
            
            print(f"✓ Found {len(active_students)} active students")
            for student in active_students:
                print(f"  - {student['student_name']}: {student['skill_name']} ({student['questions_answered']} questions, {student['accuracy']:.0%})")
            
            if len(active_students) != 2:
                print(f"  ✗ Expected 2 active students, got {len(active_students)}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Get student status
        print("\n[Test 4] Getting student statuses...")
        try:
            for i, student in enumerate(students, 1):
                status_data = MonitoringService.get_student_status(student.id)
                print(f"  Student {i}: {status_data['status']} (accuracy: {status_data['avg_accuracy']:.0%}, inactive: {status_data['days_inactive']} days)")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 5: Get struggling students
        print("\n[Test 5] Getting struggling students...")
        try:
            struggling = MonitoringService.get_struggling_students(test_class.id, threshold=0.7)
            
            print(f"✓ Found {len(struggling)} struggling students")
            for student in struggling:
                print(f"  - {student['name']}: {student['avg_accuracy']:.0%} accuracy")
                for skill in student['struggling_skills']:
                    print(f"    • {skill['skill_name']}: {skill['accuracy']:.0%}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Get inactive students
        print("\n[Test 6] Getting inactive students...")
        try:
            inactive = MonitoringService.get_inactive_students(test_class.id, days=7)
            
            print(f"✓ Found {len(inactive)} inactive students (>7 days)")
            for student in inactive:
                print(f"  - {student['name']}: {student['days_inactive']} days inactive")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 7: Get class monitoring data
        print("\n[Test 7] Getting class monitoring dashboard...")
        try:
            result, status = MonitoringService.get_class_monitoring_data(test_class.id, teacher_user.id)
            
            if result.get('success'):
                print(f"✓ Class monitoring data retrieved")
                print(f"  - Active students: {len(result['active_students'])}")
                print(f"  - Total students: {len(result['students'])}")
                print(f"  - Status breakdown:")
                for status_type, count in result['status_breakdown'].items():
                    print(f"    • {status_type}: {count}")
                print(f"  - Alerts: {len(result['alerts'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 8: Get class alerts
        print("\n[Test 8] Getting class alerts...")
        try:
            alerts = MonitoringService.get_class_alerts(test_class.id, teacher_user.id)
            
            print(f"✓ Generated {len(alerts)} alerts")
            for alert in alerts[:5]:  # Show first 5
                print(f"  [{alert['severity'].upper()}] {alert['message']}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 9: Create assignment and test overdue alerts
        print("\n[Test 9] Testing overdue assignment alerts...")
        try:
            # Create overdue assignment
            assignment = Assignment(
                teacher_id=teacher_user.id,
                class_id=test_class.id,
                title='Overdue Assignment',
                skill_ids=[skills[0].id],
                question_count=10,
                due_date=datetime.utcnow() - timedelta(days=2)  # 2 days overdue
            )
            db.session.add(assignment)
            db.session.flush()
            
            # Assign to students 3 and 4 (not completed)
            for student in students[2:4]:
                as_record = AssignmentStudent(
                    assignment_id=assignment.id,
                    student_id=student.id,
                    status='assigned'
                )
                db.session.add(as_record)
            
            db.session.commit()
            
            # Get alerts again
            alerts = MonitoringService.get_class_alerts(test_class.id, teacher_user.id)
            overdue_alerts = [a for a in alerts if a['type'] == 'overdue_assignments']
            
            print(f"✓ Found {len(overdue_alerts)} overdue assignment alerts")
            for alert in overdue_alerts:
                print(f"  - {alert['message']}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 10: Track session activity
        print("\n[Test 10] Tracking session activity...")
        try:
            student_id = students[0].id
            skill_id = skills[0].id
            
            # Track 3 questions
            for i in range(3):
                correct = i < 2  # First 2 correct, last one wrong
                result, status = MonitoringService.track_session_activity(
                    student_id, skill_id, f'q{i}', correct
                )
                
                if not result.get('success'):
                    print(f"✗ Error tracking activity: {result.get('error')}")
                    break
            else:
                print(f"✓ Tracked 3 questions")
                print(f"  - Questions answered: {result['session']['questions_answered']}")
                print(f"  - Accuracy: {result['session']['accuracy']:.0%}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Start and end session
        print("\n[Test 11] Testing session start/end...")
        try:
            student_id = students[2].id
            skill_id = skills[1].id
            
            # Start session
            result, status = MonitoringService.start_session(student_id, skill_id)
            
            if result.get('success'):
                session_id = result['session']['id']
                print(f"✓ Session started (ID: {session_id})")
                
                # End session
                result, status = MonitoringService.end_session(session_id)
                
                if result.get('success'):
                    print(f"✓ Session ended")
                    print(f"  - Duration: {result['session']['duration']} seconds")
                else:
                    print(f"✗ Error ending session: {result.get('error')}")
            else:
                print(f"✗ Error starting session: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 12: Get student activity timeline
        print("\n[Test 12] Getting student activity timeline...")
        try:
            student_id = students[0].id
            timeline = MonitoringService.get_student_activity_timeline(student_id, days=7)
            
            print(f"✓ Retrieved timeline with {len(timeline)} sessions")
            for session in timeline[:3]:  # Show first 3
                print(f"  - {session['skill_name']}: {session['questions_answered']} questions, {session['accuracy']:.0%}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 13: Get current session
        print("\n[Test 13] Getting current session...")
        try:
            student_id = students[0].id
            current_session = MonitoringService.get_student_current_session(student_id)
            
            if current_session:
                print(f"✓ Current session found")
                print(f"  - Questions answered: {current_session['questions_answered']}")
                print(f"  - Accuracy: {current_session['accuracy']:.0%}")
                print(f"  - Duration: {current_session['duration']} seconds")
            else:
                print(f"✓ No current session (student not active)")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 14: Get assignment compliance
        print("\n[Test 14] Getting assignment compliance...")
        try:
            compliance = MonitoringService.get_assignment_compliance(test_class.id)
            
            print(f"✓ Assignment compliance retrieved")
            print(f"  - Total assignments: {compliance['total_assignments']}")
            print(f"  - Total assigned: {compliance['total_assigned']}")
            print(f"  - Completed: {compliance['total_completed']}")
            print(f"  - Completion rate: {compliance['completion_rate']:.0%}")
            print(f"  - On-time rate: {compliance['on_time_rate']:.0%}")
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
            
            # Try to access first teacher's class
            result, status = MonitoringService.get_class_monitoring_data(test_class.id, other_teacher_user.id)
            
            if status == 403:
                print("✓ Unauthorized access correctly blocked")
            else:
                print("✗ Unauthorized access not blocked!")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()

