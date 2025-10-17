"""
Test Teacher Dashboard System
Tests all teacher dashboard functionality
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
from src.models.gamification import StudentProgress
from src.models.streak import StreakTracking
from src.services.teacher_service import TeacherService
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
    """Run all teacher dashboard tests"""
    with app.app_context():
        # Drop and recreate tables to get updated schema
        db.drop_all()
        db.create_all()
        
        print("=" * 60)
        print("TEACHER DASHBOARD SYSTEM TESTS")
        print("=" * 60)
        
        # Cleanup any existing test data first
        print("\n[Setup] Cleaning up any existing test data...")
        try:
            db.session.query(StreakTracking).delete()
            db.session.query(StudentProgress).delete()
            db.session.query(LearningPath).delete()
            db.session.query(ClassMembership).delete()
            db.session.query(ClassGroup).delete()
            db.session.query(Skill).delete()
            db.session.query(Teacher).delete()
            db.session.query(Student).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("✓ Cleanup complete")
        except Exception as e:
            print(f"Note: {e}")
            db.session.rollback()
        
        # Test 1: Create teacher account
        print("\n[Test 1] Creating teacher account...")
        try:
            teacher_user = User(username='teacher1', email='teacher1@school.edu', role='teacher')
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            
            teacher = Teacher(
                user_id=teacher_user.id,
                name='Ms. Johnson',
                email='teacher1@school.edu',
                school='Test Elementary',
                subject='Mathematics',
                grade_levels='3,4,5',
                avatar='👩‍🏫'
            )
            db.session.add(teacher)
            db.session.commit()
            print(f"✓ Created teacher: {teacher.name}")
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 2: Create test class
        print("\n[Test 2] Creating test class...")
        try:
            test_class = ClassGroup(
                name='Math 5A',
                description='5th grade mathematics',
                teacher_id=teacher_user.id,
                grade_level=5,
                invite_code='TEST01'
            )
            db.session.add(test_class)
            db.session.commit()
            print(f"✓ Created class: {test_class.name}")
        except Exception as e:
            print(f"✗ Error: {e}")
            return
        
        # Test 3: Create test students
        print("\n[Test 3] Creating test students...")
        try:
            students = []
            for i in range(1, 6):
                # Create user
                student_user = User(username=f'student{i}', email=f'student{i}@test.com')
                student_user.set_password('password123')
                db.session.add(student_user)
                db.session.flush()
                
                # Create student
                student = Student(
                    user_id=student_user.id,
                    name=f'Student {i}',
                    grade=5,
                    avatar='😊'
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
                
                # Create streak
                streak = StreakTracking(
                    student_id=student.id,
                    practice_streak=i,
                    practice_streak_best=i
                )
                db.session.add(streak)
                
                # Add to class
                membership = ClassMembership(
                    class_id=test_class.id,
                    student_id=student.id
                )
                db.session.add(membership)
                
                students.append(student)
            
            db.session.commit()
            print(f"✓ Created {len(students)} students")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 4: Create learning paths with varying performance
        print("\n[Test 4] Creating learning paths with varying performance...")
        try:
            skills = ['Multiplication', 'Division', 'Fractions', 'Decimals']
            
            for i, student in enumerate(students):
                # Create paths with different accuracy levels
                base_accuracy = 0.6 + (i * 0.08)  # 0.6, 0.68, 0.76, 0.84, 0.92
                
                for j, skill in enumerate(skills):
                    # Create a dummy skill if needed
                    from src.models.assessment import Skill
                    test_skill = Skill.query.filter_by(name=skill).first()
                    if not test_skill:
                        test_skill = Skill(
                            name=skill,
                            description=f'{skill} skill',
                            grade_level=5,
                            subject_area='arithmetic'
                        )
                        db.session.add(test_skill)
                        db.session.flush()
                    
                    path = LearningPath(
                        student_id=student.id,
                        skill_id=test_skill.id,
                        current_accuracy=min(base_accuracy + (0.05 * j), 0.98),
                        questions_answered=10 + (i * 5),
                        updated_at=datetime.utcnow() - timedelta(days=i)
                    )
                    db.session.add(path)
            
            db.session.commit()
            print("✓ Created learning paths with varying performance")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 5: Get dashboard data
        print("\n[Test 5] Getting teacher dashboard data...")
        try:
            result, status = TeacherService.get_dashboard_data(teacher_user.id)
            
            if result.get('success'):
                print(f"✓ Dashboard data retrieved")
                print(f"  - Teacher: {result['teacher']['name']}")
                print(f"  - Total students: {result['stats']['total_students']}")
                print(f"  - Total classes: {result['stats']['total_classes']}")
                print(f"  - Avg performance: {result['stats']['avg_class_performance']}")
                print(f"  - Classes: {len(result['classes'])}")
                print(f"  - Alerts: {len(result['alerts'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 6: Get class overview
        print("\n[Test 6] Getting class overview...")
        try:
            result, status = TeacherService.get_class_overview(test_class.id, teacher_user.id)
            
            if result.get('success'):
                print(f"✓ Class overview retrieved")
                print(f"  - Class: {result['class']['name']}")
                print(f"  - Students: {len(result['students'])}")
                print(f"  - Avg accuracy: {result['metrics']['avg_accuracy']}")
                print(f"  - Mastery rate: {result['metrics']['mastery_rate']}")
                print(f"  - Engagement rate: {result['metrics']['engagement_rate']}")
                print(f"  - Skills tracked: {len(result['skill_performance'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 7: Get student summary
        print("\n[Test 7] Getting student summary...")
        try:
            student_id = students[0].id
            result, status = TeacherService.get_student_summary(student_id, teacher_user.id)
            
            if result.get('success'):
                print(f"✓ Student summary retrieved")
                print(f"  - Student: {result['student']['name']}")
                print(f"  - Avg accuracy: {result['performance']['avg_accuracy']}")
                print(f"  - Questions answered: {result['performance']['questions_answered']}")
                print(f"  - Skills mastered: {result['performance']['skills_mastered']}")
                print(f"  - Current streak: {result['performance']['current_streak']}")
                print(f"  - Struggling skills: {len(result['struggling_skills'])}")
                print(f"  - Mastered skills: {len(result['mastered_skills'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 8: Get class metrics
        print("\n[Test 8] Getting class metrics...")
        try:
            metrics = TeacherService.get_class_metrics(test_class.id)
            
            print(f"✓ Class metrics calculated")
            print(f"  - Student count: {metrics['student_count']}")
            print(f"  - Avg accuracy: {metrics['avg_accuracy']}")
            print(f"  - Avg questions: {metrics['avg_questions']}")
            print(f"  - Active students: {metrics['active_students']}")
            print(f"  - Struggling students: {len(metrics['struggling_students'])}")
            print(f"  - Mastery rate: {metrics['mastery_rate']}")
            print(f"  - Engagement rate: {metrics['engagement_rate']}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 9: Get struggling students
        print("\n[Test 9] Getting struggling students...")
        try:
            struggling = TeacherService.get_struggling_students(test_class.id, threshold=0.7)
            
            print(f"✓ Struggling students identified: {len(struggling)}")
            for student in struggling:
                print(f"  - {student['name']}: {student['accuracy']:.0%} accuracy")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 10: Get top performers
        print("\n[Test 10] Getting top performers...")
        try:
            top_performers = TeacherService.get_top_performers(test_class.id, limit=3)
            
            print(f"✓ Top performers identified: {len(top_performers)}")
            for i, student in enumerate(top_performers, 1):
                print(f"  {i}. {student['name']}: {student['avg_accuracy']:.0%} accuracy")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Get teacher stats
        print("\n[Test 11] Getting teacher statistics...")
        try:
            stats = TeacherService.get_teacher_stats(teacher_user.id)
            
            print(f"✓ Teacher stats calculated")
            print(f"  - Total students: {stats['total_students']}")
            print(f"  - Total classes: {stats['total_classes']}")
            print(f"  - Avg class performance: {stats['avg_class_performance']}")
            print(f"  - Total questions answered: {stats['total_questions_answered']}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 12: Get alerts
        print("\n[Test 12] Getting alerts...")
        try:
            alerts = TeacherService.get_alerts(teacher_user.id)
            
            print(f"✓ Alerts generated: {len(alerts)}")
            for alert in alerts:
                print(f"  - [{alert['severity']}] {alert['class_name']}: {alert['message']}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 13: Test unauthorized access
        print("\n[Test 13] Testing unauthorized access...")
        try:
            # Create another teacher
            other_teacher_user = User(username='teacher2', email='teacher2@school.edu', role='teacher')
            other_teacher_user.set_password('password123')
            db.session.add(other_teacher_user)
            db.session.commit()
            
            # Try to access first teacher's class
            result, status = TeacherService.get_class_overview(test_class.id, other_teacher_user.id)
            
            if status == 403:
                print("✓ Unauthorized access correctly blocked")
            else:
                print("✗ Unauthorized access not blocked!")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 14: Test auto-creation of teacher profile
        print("\n[Test 14] Testing auto-creation of teacher profile...")
        try:
            # Create teacher user without profile
            new_teacher_user = User(username='teacher3', email='teacher3@school.edu', role='teacher')
            new_teacher_user.set_password('password123')
            db.session.add(new_teacher_user)
            db.session.commit()
            
            # Get dashboard (should auto-create profile)
            result, status = TeacherService.get_dashboard_data(new_teacher_user.id)
            
            if result.get('success'):
                teacher_profile = Teacher.query.filter_by(user_id=new_teacher_user.id).first()
                if teacher_profile:
                    print("✓ Teacher profile auto-created")
                else:
                    print("✗ Teacher profile not created")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 15: Cleanup
        print("\n[Test 15] Cleanup test data...")
        try:
            db.session.query(StreakTracking).delete()
            db.session.query(StudentProgress).delete()
            db.session.query(LearningPath).delete()
            db.session.query(ClassMembership).delete()
            db.session.query(ClassGroup).delete()
            db.session.query(Skill).delete()
            db.session.query(Teacher).delete()
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

