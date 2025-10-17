"""
Comprehensive tests for Advanced Analytics Features (Steps 9.2-9.5).
Tests predictive modeling, recommendations, and export functionality.
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
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.class_group import ClassGroup, ClassMembership
from src.services.predictive_analytics_service import PredictiveAnalyticsService
from src.services.recommendation_service import RecommendationService
from src.services.export_service import ExportService
from datetime import datetime, timedelta


def run_tests():
    """Run all advanced analytics tests"""
    print("=" * 60)
    print("ADVANCED ANALYTICS TESTS (Steps 9.2-9.5)")
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
            skill3 = Skill(
                name='Multiplication',
                subject_area='arithmetic',
                grade_level=5,
                description='Basic multiplication'
            )
            db.session.add_all([skill1, skill2, skill3])
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
            
            # Create sessions for first student
            for day_offset in [1, 2, 3, 5, 7, 10]:
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
            
            # Create assignment
            assignment = Assignment(
                teacher_id=teacher_id,
                title='Practice Assignment',
                description='Practice problems',
                skill_ids=[skill1.id],
                question_count=20,
                difficulty='medium',
                due_date=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(assignment)
            db.session.flush()
            
            # Assign to student
            student_assignment = AssignmentStudent(
                assignment_id=assignment.id,
                student_id=student_id,
                status='assigned'
            )
            db.session.add(student_assignment)
            
            db.session.commit()
            
            print("✓ Test data created")
            print(f"  - Students: {len(students)}")
            print(f"  - Skills: 3")
            print(f"  - Primary student ID: {student_id}")
            
            # PREDICTIVE ANALYTICS TESTS (Step 9.2)
            
            # Test 2: Predict skill mastery
            print("[Test 2] Predicting skill mastery...")
            result, status = PredictiveAnalyticsService.predict_skill_mastery(student_id, skill2.id)
            
            if result.get('success'):
                pred = result['prediction']
                print("✓ Skill mastery prediction generated")
                print(f"  - Will master: {pred['will_master']}")
                print(f"  - Probability: {pred['probability']}%")
                print(f"  - Days to mastery: {pred.get('days_to_mastery', 'N/A')}")
                print(f"  - Current accuracy: {pred['current_accuracy']}%")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 3: Predict already mastered skill
            print("[Test 3] Predicting already mastered skill...")
            result, status = PredictiveAnalyticsService.predict_skill_mastery(student_id, skill1.id)
            
            if result.get('success') and result['prediction'].get('already_mastered'):
                print("✓ Correctly identified already mastered skill")
                print(f"  - Probability: {result['prediction']['probability']}%")
            else:
                print("✗ Should have identified as already mastered")
            
            # Test 4: Predict assignment completion
            print("[Test 4] Predicting assignment completion...")
            result, status = PredictiveAnalyticsService.predict_assignment_completion(student_id, assignment.id)
            
            if result.get('success'):
                pred = result['prediction']
                print("✓ Assignment completion prediction generated")
                print(f"  - Will complete: {pred['will_complete']}")
                print(f"  - Probability: {pred['probability']}%")
                print(f"  - Days remaining: {pred.get('days_remaining', 'N/A')}")
                print(f"  - Recommendation: {pred['recommendation']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 5: Detect at-risk students
            print("[Test 5] Detecting at-risk students...")
            result, status = PredictiveAnalyticsService.detect_at_risk_students(class_id)
            
            if result.get('success'):
                at_risk = result['at_risk_students']
                print(f"✓ At-risk detection completed")
                print(f"  - At-risk students: {len(at_risk)}")
                for student in at_risk:
                    print(f"    - {student['student_name']}: {student['risk_level']} risk ({student['risk_score']} points)")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 6: Forecast performance
            print("[Test 6] Forecasting performance...")
            result, status = PredictiveAnalyticsService.forecast_performance(student_id, 7)
            
            if result.get('success'):
                forecast = result['forecast']
                if forecast.get('insufficient_data'):
                    print(f"✓ Correctly identified insufficient data")
                else:
                    print("✓ Performance forecast generated")
                    print(f"  - Current accuracy: {forecast['current_accuracy']}%")
                    print(f"  - Forecast accuracy: {forecast['forecast_accuracy']}%")
                    print(f"  - Trend: {forecast['trend']}")
                    print(f"  - Confidence: {forecast['confidence']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # RECOMMENDATION TESTS (Step 9.3)
            
            # Test 7: Get skill recommendations
            print("[Test 7] Getting skill recommendations...")
            result, status = RecommendationService.get_skill_recommendations(student_id, 5)
            
            if result.get('success'):
                recs = result['recommendations']
                print(f"✓ Skill recommendations generated")
                print(f"  - Recommendations: {len(recs)}")
                for rec in recs[:3]:
                    print(f"    - {rec['skill_name']}: {rec['reason']} (priority: {rec['priority']})")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 8: Get practice time recommendations
            print("[Test 8] Getting practice time recommendations...")
            result, status = RecommendationService.get_practice_time_recommendations(student_id)
            
            if result.get('success'):
                recs = result['recommendations']
                print("✓ Practice time recommendations generated")
                print(f"  - Best time: {recs['best_time']}")
                print(f"  - Optimal duration: {recs['optimal_duration']} minutes")
                print(f"  - Frequency: {recs['frequency']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 9: Get study strategies
            print("[Test 9] Getting study strategies...")
            result, status = RecommendationService.get_study_strategies(student_id)
            
            if result.get('success'):
                strategies = result['strategies']
                print(f"✓ Study strategies generated")
                print(f"  - Strategies: {len(strategies)}")
                for strategy in strategies[:2]:
                    print(f"    - {strategy['strategy']} ({strategy['priority']} priority)")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 10: Analyze skill gaps
            print("[Test 10] Analyzing skill gaps...")
            result, status = RecommendationService.analyze_skill_gaps(student_id)
            
            if result.get('success'):
                gaps = result['gaps']
                print(f"✓ Skill gap analysis completed")
                print(f"  - Gaps found: {result['gap_count']}")
                for gap in gaps[:2]:
                    print(f"    - {gap['skill_name']} (Grade {gap['grade_level']}, {gap['priority']} priority)")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # EXPORT TESTS (Step 9.5)
            
            # Test 11: Export student data (JSON)
            print("[Test 11] Exporting student data (JSON)...")
            result, status = ExportService.export_student_data(student_id, 'json')
            
            if result.get('success'):
                data = result['data']
                print("✓ Student data exported (JSON)")
                print(f"  - Student name: {data['student']['name']}")
                print(f"  - Learning paths: {len(data['learning_paths'])}")
                print(f"  - Recent sessions: {len(data['recent_sessions'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 12: Export student data (CSV)
            print("[Test 12] Exporting student data (CSV)...")
            result, status = ExportService.export_student_data(student_id, 'csv')
            
            if result.get('success'):
                csv_data = result['data']
                print("✓ Student data exported (CSV)")
                print(f"  - CSV length: {len(csv_data)} characters")
                if 'Student Name' in csv_data:
                    print("  ✓ CSV contains header row")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 13: Export class data (JSON)
            print("[Test 13] Exporting class data (JSON)...")
            result, status = ExportService.export_class_data(class_id, 'json')
            
            if result.get('success'):
                data = result['data']
                print("✓ Class data exported (JSON)")
                print(f"  - Class name: {data['class']['name']}")
                print(f"  - Student count: {data['class']['student_count']}")
                print(f"  - Students in export: {len(data['students'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 14: Export class data (CSV)
            print("[Test 14] Exporting class data (CSV)...")
            result, status = ExportService.export_class_data(class_id, 'csv')
            
            if result.get('success'):
                csv_data = result['data']
                print("✓ Class data exported (CSV)")
                print(f"  - CSV length: {len(csv_data)} characters")
                if 'Student Name' in csv_data:
                    print("  ✓ CSV contains header row")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 15: Generate report
            print("[Test 15] Generating student progress report...")
            result, status = ExportService.generate_report('student_progress', student_id, 'json')
            
            if result.get('success'):
                print("✓ Student progress report generated")
                print(f"  - Format: {result['format']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 16: Invalid student
            print("[Test 16] Testing invalid student...")
            result, status = PredictiveAnalyticsService.predict_skill_mastery(999, skill1.id)
            
            if not result.get('success') and status == 404:
                print("✓ Correctly handled invalid student")
            else:
                print("✗ Should have returned 404")
            
            # Test 17: Invalid format
            print("[Test 17] Testing invalid export format...")
            result, status = ExportService.export_student_data(student_id, 'pdf')
            
            if not result.get('success') and status == 400:
                print("✓ Correctly handled invalid format")
            else:
                print("✗ Should have returned 400")
            
            # Test 18: Student with no data (recommendations)
            print("[Test 18] Testing recommendations for student with no data...")
            
            # Create new student with no sessions
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
            
            result, status = RecommendationService.get_practice_time_recommendations(new_student.id)
            
            if result.get('success'):
                recs = result['recommendations']
                print("✓ Recommendations generated for new student")
                print(f"  - Best time: {recs['best_time']}")
                print(f"  - Reason: {recs['reason']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED!")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()

