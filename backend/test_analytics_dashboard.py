"""
Comprehensive tests for Learning Analytics Dashboard (Step 9.1).
Tests student dashboard, teacher dashboard, comparative analytics, and engagement scoring.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from src.database import db, init_db
from src.models.user import User
from src.models.student import Student
from src.models.assessment import Skill
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.class_group import ClassGroup, ClassMembership
from src.models.gamification import StudentProgress
from src.services.analytics_dashboard_service import AnalyticsDashboardService
from datetime import datetime, timedelta


def run_tests():
    """Run all analytics dashboard tests"""
    print("=" * 60)
    print("ANALYTICS DASHBOARD TESTS")
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
            
            # Create teacher
            teacher_user = User(username='teacher1', email='teacher1@email.com', role='teacher')
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            teacher_id = teacher_user.id
            
            # Create class
            class_group = ClassGroup(
                teacher_id=teacher_id,
                name='Math Class',
                grade_level=5,
                invite_code='MATH123'
            )
            db.session.add(class_group)
            db.session.flush()
            class_id = class_group.id
            
            # Create students
            students = []
            for i in range(3):
                user = User(username=f'student{i+1}', email=f'student{i+1}@email.com', role='student')
                user.set_password('password123')
                db.session.add(user)
                db.session.flush()
                
                student = Student(
                    user_id=user.id,
                    name=f'Student {i+1}',
                    grade=5
                )
                db.session.add(student)
                db.session.flush()
                students.append(student)
                
                # Add to class
                membership = ClassMembership(
                    class_id=class_id,
                    student_id=student.id,
                    role='student'
                )
                db.session.add(membership)
                
                # Create progress
                progress = StudentProgress(
                    student_id=student.id,
                    total_xp=1000 * (i+1),
                    current_level=5 + i
                )
                db.session.add(progress)
            
            # Create skills
            skill1 = Skill(
                name='Addition',
                subject_area='arithmetic',
                grade_level=5,
                description='Basic addition'
            )
            skill2 = Skill(
                name='Subtraction',
                subject_area='arithmetic',
                grade_level=5,
                description='Basic subtraction'
            )
            db.session.add_all([skill1, skill2])
            db.session.flush()
            
            # Create learning paths for first student
            student_id = students[0].id
            
            path1 = LearningPath(
                student_id=student_id,
                skill_id=skill1.id,
                current_accuracy=0.85,
                questions_answered=100,
                correct_answers=85,
                total_questions=100,
                mastery_achieved=True,
                last_practiced=datetime.utcnow(),
                status='mastered'
            )
            
            path2 = LearningPath(
                student_id=student_id,
                skill_id=skill2.id,
                current_accuracy=0.70,
                questions_answered=50,
                correct_answers=35,
                total_questions=50,
                mastery_achieved=False,
                last_practiced=datetime.utcnow(),
                status='in_progress'
            )
            db.session.add_all([path1, path2])
            
            # Create sessions for first student (last 30 days)
            for day_offset in [1, 3, 5, 7, 10, 12, 15, 20, 25]:
                start_time = datetime.utcnow() - timedelta(days=day_offset)
                end_time = start_time + timedelta(minutes=20)
                
                session = StudentSession(
                    student_id=student_id,
                    started_at=start_time,
                    ended_at=end_time,
                    questions_answered=10,
                    questions_correct=8
                )
                db.session.add(session)
            
            # Create sessions for other students (for class averages)
            for student in students[1:]:
                for day_offset in [2, 6, 14]:
                    start_time = datetime.utcnow() - timedelta(days=day_offset)
                    end_time = start_time + timedelta(minutes=15)
                    
                    session = StudentSession(
                        student_id=student.id,
                        started_at=start_time,
                        ended_at=end_time,
                        questions_answered=10,
                        questions_correct=7
                    )
                    db.session.add(session)
            
            db.session.commit()
            
            print("✓ Test data created")
            print(f"  - Teacher ID: {teacher_id}")
            print(f"  - Class ID: {class_id}")
            print(f"  - Students: {len(students)}")
            print(f"  - Primary student ID: {student_id}")
            
            # Test 2: Get student dashboard
            print("[Test 2] Getting student dashboard...")
            result, status = AnalyticsDashboardService.get_student_dashboard(student_id, days=30)
            
            if result.get('success'):
                dashboard = result['dashboard']
                print("✓ Student dashboard retrieved")
                print(f"  - Total time: {dashboard['summary']['total_time_minutes']} minutes")
                print(f"  - Total sessions: {dashboard['summary']['total_sessions']}")
                print(f"  - Average accuracy: {dashboard['summary']['average_accuracy']}%")
                print(f"  - Skills mastered: {dashboard['summary']['skills_mastered']}")
                print(f"  - Learning velocity: {dashboard['summary']['learning_velocity']} skills/week")
                print(f"  - Engagement score: {dashboard['summary']['engagement_score']}")
                print(f"  - Consistency score: {dashboard['summary']['consistency_score']}%")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 3: Engagement score calculation
            print("[Test 3] Calculating engagement score...")
            score = AnalyticsDashboardService.calculate_engagement_score(student_id, 30)
            
            print(f"✓ Engagement score calculated: {round(score, 1)}")
            if score > 0:
                print("  ✓ Score is positive (student has activity)")
            
            # Test 4: Get teacher dashboard
            print("[Test 4] Getting teacher dashboard...")
            result, status = AnalyticsDashboardService.get_teacher_dashboard(teacher_id)
            
            if result.get('success'):
                dashboard = result['dashboard']
                print("✓ Teacher dashboard retrieved")
                print(f"  - Total classes: {dashboard['summary']['total_classes']}")
                print(f"  - Total students: {dashboard['summary']['total_students']}")
                print(f"  - On track: {dashboard['summary']['on_track']}")
                print(f"  - Needs practice: {dashboard['summary']['needs_practice']}")
                print(f"  - Struggling: {dashboard['summary']['struggling']}")
                print(f"  - On track %: {dashboard['summary']['on_track_percent']}%")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 5: Get teacher dashboard for specific class
            print("[Test 5] Getting teacher dashboard for specific class...")
            result, status = AnalyticsDashboardService.get_teacher_dashboard(teacher_id, class_id)
            
            if result.get('success'):
                dashboard = result['dashboard']
                print("✓ Class-specific dashboard retrieved")
                print(f"  - Classes shown: {len(dashboard['classes'])}")
                if dashboard['classes']:
                    print(f"  - Class name: {dashboard['classes'][0]['class_name']}")
                    print(f"  - Student count: {dashboard['classes'][0]['student_count']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 6: Comparative analytics (vs class)
            print("[Test 6] Getting comparative analytics (vs class)...")
            result, status = AnalyticsDashboardService.get_comparative_analytics(student_id, 'class')
            
            if result.get('success'):
                comparison = result['comparison']
                print("✓ Comparative analytics retrieved")
                print(f"  - Comparison type: {comparison['comparison_type']}")
                print(f"  - Student accuracy: {comparison['student']['accuracy']}%")
                print(f"  - Class average accuracy: {comparison['comparison_group']['accuracy']}%")
                print(f"  - Difference: {comparison['differences']['accuracy']}%")
                print(f"  - Student engagement: {comparison['student']['engagement_score']}")
                print(f"  - Class engagement: {comparison['comparison_group']['engagement_score']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 7: Comparative analytics (vs grade)
            print("[Test 7] Getting comparative analytics (vs grade)...")
            result, status = AnalyticsDashboardService.get_comparative_analytics(student_id, 'grade')
            
            if result.get('success'):
                comparison = result['comparison']
                print("✓ Grade-level comparative analytics retrieved")
                print(f"  - Comparison label: {comparison['comparison_label']}")
                print(f"  - Student vs grade accuracy diff: {comparison['differences']['accuracy']}%")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 8: Daily aggregates (trend data)
            print("[Test 8] Testing daily aggregates...")
            daily_data = AnalyticsDashboardService._get_daily_aggregates(student_id, 30)
            
            print("✓ Daily aggregates calculated")
            print(f"  - Days with time data: {len(daily_data['time'])}")
            print(f"  - Days with accuracy data: {len(daily_data['accuracy'])}")
            print(f"  - Days with questions data: {len(daily_data['questions'])}")
            
            # Test 9: Subject distribution
            print("[Test 9] Testing subject distribution...")
            subject_dist = AnalyticsDashboardService._get_subject_distribution(student_id)
            
            print("✓ Subject distribution calculated")
            print(f"  - Subjects: {len(subject_dist)}")
            for item in subject_dist:
                print(f"    - {item['subject']}: {item['time_estimate']} questions")
            
            # Test 10: Student status determination
            print("[Test 10] Testing student status determination...")
            status = AnalyticsDashboardService._get_student_status(student_id)
            
            print(f"✓ Student status determined: {status}")
            if status in ['on_track', 'needs_practice', 'struggling']:
                print("  ✓ Valid status category")
            
            # Test 11: Class average accuracy
            print("[Test 11] Testing class average accuracy...")
            avg_accuracy = AnalyticsDashboardService._get_class_average_accuracy(class_id)
            
            print(f"✓ Class average accuracy calculated: {round(avg_accuracy, 1)}%")
            if avg_accuracy > 0:
                print("  ✓ Accuracy is positive")
            
            # Test 12: Class engagement
            print("[Test 12] Testing class engagement...")
            class_engagement = AnalyticsDashboardService._get_class_engagement(class_id)
            
            print(f"✓ Class engagement calculated: {round(class_engagement, 1)}")
            if class_engagement >= 0:
                print("  ✓ Engagement score is valid")
            
            # Test 13: Student with no data
            print("[Test 13] Testing student with no data...")
            
            # Create student with no sessions
            user = User(username='newstudent', email='new@email.com', role='student')
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            new_student = Student(
                user_id=user.id,
                name='New Student',
                grade=5
            )
            db.session.add(new_student)
            db.session.flush()
            
            result, status = AnalyticsDashboardService.get_student_dashboard(new_student.id, 30)
            
            if result.get('success'):
                dashboard = result['dashboard']
                print("✓ Dashboard generated for student with no data")
                print(f"  - Total sessions: {dashboard['summary']['total_sessions']}")
                print(f"  - Engagement score: {dashboard['summary']['engagement_score']}")
                if dashboard['summary']['total_sessions'] == 0:
                    print("  ✓ Correctly shows zero sessions")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 14: Invalid student
            print("[Test 14] Testing invalid student...")
            result, status = AnalyticsDashboardService.get_student_dashboard(999, 30)
            
            if not result.get('success') and status == 404:
                print("✓ Correctly handled invalid student")
            else:
                print("✗ Should have returned 404 for invalid student")
            
            # Test 15: Invalid comparison type
            print("[Test 15] Testing invalid comparison type...")
            result, status = AnalyticsDashboardService.get_comparative_analytics(student_id, 'invalid')
            
            if not result.get('success') and status == 400:
                print("✓ Correctly handled invalid comparison type")
            else:
                print("✗ Should have returned 400 for invalid comparison type")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED!")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()

