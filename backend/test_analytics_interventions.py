"""
Test Analytics and Interventions System
Tests all performance analytics and intervention functionality
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
from src.models.student_session import StudentSession
from src.models.intervention import TeacherMessage, MessageTemplate, Intervention, Meeting
from src.services.analytics_service import AnalyticsService
from src.services.intervention_service import InterventionService
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
    """Run all analytics and intervention tests"""
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        
        print("=" * 60)
        print("ANALYTICS & INTERVENTIONS SYSTEM TESTS")
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
                
                # Add to class
                membership = ClassMembership(
                    class_id=test_class.id,
                    student_id=student.id
                )
                db.session.add(membership)
                
                # Create learning paths with varying accuracy
                for j, skill in enumerate(skills):
                    # Student 1: High performer (90%, 85%, 80%)
                    # Student 2: Medium performer (75%, 70%, 65%)
                    # Student 3: Struggling (60%, 55%, 50%)
                    if i == 1:
                        accuracy = 0.9 - (j * 0.05)
                    elif i == 2:
                        accuracy = 0.75 - (j * 0.05)
                    else:
                        accuracy = 0.6 - (j * 0.05)
                    
                    path = LearningPath(
                        student_id=student.id,
                        skill_id=skill.id,
                        current_accuracy=accuracy,
                        questions_answered=30,
                        correct_answers=int(30 * accuracy),
                        total_questions=30,
                        status='in_progress' if accuracy < 0.9 else 'mastered',
                        mastery_achieved=(accuracy >= 0.9)
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
        
        # Test 2: Create sessions for analytics
        print("\n[Test 2] Creating student sessions...")
        try:
            # Create sessions over last 30 days
            for day_offset in range(0, 30, 3):  # Every 3 days
                for i, student in enumerate(students):
                    # Student 1: Improving (60% -> 90%)
                    # Student 2: Stable (75%)
                    # Student 3: Declining (70% -> 50%)
                    if i == 0:
                        accuracy = 0.6 + (day_offset / 30 * 0.3)  # Improving
                    elif i == 1:
                        accuracy = 0.75  # Stable
                    else:
                        accuracy = 0.7 - (day_offset / 30 * 0.2)  # Declining
                    
                    questions = 10
                    correct = int(questions * accuracy)
                    
                    session_date = datetime.utcnow() - timedelta(days=30-day_offset)
                    
                    session = StudentSession(
                        student_id=student.id,
                        skill_id=skills[day_offset % 3].id,
                        started_at=session_date,
                        last_activity_at=session_date + timedelta(minutes=15),
                        ended_at=session_date + timedelta(minutes=15),
                        questions_answered=questions,
                        questions_correct=correct,
                        accuracy=accuracy,
                        is_active=False
                    )
                    db.session.add(session)
            
            db.session.commit()
            print(f"✓ Created sessions for trend analysis")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Get student performance report
        print("\n[Test 3] Getting student performance report...")
        try:
            report = AnalyticsService.get_student_performance_report(students[0].id, days=30)
            
            print(f"✓ Student report generated")
            print(f"  - Student: {report['student']['name']}")
            print(f"  - Overall accuracy: {report['overall']['accuracy']:.0%}")
            print(f"  - Questions answered: {report['overall']['questions']}")
            print(f"  - Skills mastered: {report['overall']['skills_mastered']}/{report['overall']['total_skills']}")
            print(f"  - Skill breakdown: {len(report['skills'])} skills")
            print(f"  - Trend points: {len(report['trends'])}")
            
            # Verify data
            if report['overall']['accuracy'] < 0.5 or report['overall']['accuracy'] > 1.0:
                print(f"  ✗ Invalid accuracy: {report['overall']['accuracy']}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Get class performance report
        print("\n[Test 4] Getting class performance report...")
        try:
            report = AnalyticsService.get_class_performance_report(test_class.id, days=30)
            
            print(f"✓ Class report generated")
            print(f"  - Class: {report['class']['name']}")
            print(f"  - Student count: {report['class']['student_count']}")
            print(f"  - Average accuracy: {report['overall']['avg_accuracy']:.0%}")
            print(f"  - Engagement rate: {report['overall']['engagement_rate']:.0%}")
            print(f"  - Distribution:")
            for level, count in report['distribution'].items():
                print(f"    • {level}: {count}")
            print(f"  - Top performers: {len(report['top_performers'])}")
            print(f"  - Struggling students: {len(report['struggling_students'])}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 5: Get student trend data
        print("\n[Test 5] Getting student trend data...")
        try:
            trends = AnalyticsService.get_student_trend_data(students[0].id, 'accuracy', 30)
            
            print(f"✓ Trend data retrieved")
            print(f"  - Data points: {len(trends)}")
            if len(trends) >= 2:
                print(f"  - First point: {trends[0]['date']} - {trends[0]['accuracy']:.0%}")
                print(f"  - Last point: {trends[-1]['date']} - {trends[-1]['accuracy']:.0%}")
                
                # Check if improving
                if trends[-1]['accuracy'] > trends[0]['accuracy']:
                    print(f"  - Trend: Improving ✓")
                else:
                    print(f"  - Trend: Stable or declining")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 6: Get class trend data
        print("\n[Test 6] Getting class trend data...")
        try:
            trends = AnalyticsService.get_class_trend_data(test_class.id, 'accuracy', 30)
            
            print(f"✓ Class trend data retrieved")
            print(f"  - Data points: {len(trends)}")
            if len(trends) >= 2:
                print(f"  - First point: {trends[0]['date']} - {trends[0]['accuracy']:.0%} ({trends[0]['active_students']} students)")
                print(f"  - Last point: {trends[-1]['date']} - {trends[-1]['accuracy']:.0%} ({trends[-1]['active_students']} students)")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 7: Get student comparison
        print("\n[Test 7] Getting student vs class comparison...")
        try:
            comparison = AnalyticsService.get_student_comparison(students[0].id)
            
            print(f"✓ Comparison data retrieved")
            print(f"  - Student accuracy: {comparison['student_accuracy']:.0%}")
            print(f"  - Class average: {comparison['class_average']:.0%}")
            print(f"  - Percentile: {comparison['percentile']:.0f}th")
            print(f"  - Rank: {comparison['rank']}/{comparison['total_students']}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 8: Create default message templates
        print("\n[Test 8] Creating default message templates...")
        try:
            result, status = InterventionService.create_default_templates()
            
            if result.get('success'):
                # Get templates
                templates_result, _ = InterventionService.get_message_templates()
                templates = templates_result.get('templates', [])
                
                print(f"✓ Created {len(templates)} default templates")
                
                # Group by category
                by_category = {}
                for t in templates:
                    cat = t['category']
                    by_category[cat] = by_category.get(cat, 0) + 1
                
                for cat, count in by_category.items():
                    print(f"  - {cat}: {count} templates")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 9: Send message to student
        print("\n[Test 9] Sending message to student...")
        try:
            message = "Hi Student 3, I noticed you're struggling with fractions. Let's meet tomorrow to go over it!"
            result, status = InterventionService.send_message(
                teacher_user.id,
                students[2].id,
                message
            )
            
            if result.get('success'):
                print(f"✓ Message sent successfully")
                print(f"  - Message ID: {result['message']['id']}")
                print(f"  - Intervention ID: {result['intervention_id']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 10: Fill template with variables
        print("\n[Test 10] Filling message template...")
        try:
            # Get a template
            templates_result, _ = InterventionService.get_message_templates('struggling')
            templates = templates_result.get('templates', [])
            
            if templates:
                template = templates[0]
                variables = {
                    'student_name': 'Student 3',
                    'skill_name': 'Fractions'
                }
                
                result, status = InterventionService.fill_template(template['id'], variables)
                
                if result.get('success'):
                    print(f"✓ Template filled successfully")
                    print(f"  - Template: {template['title']}")
                    print(f"  - Message: {result['message']}")
                else:
                    print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 11: Create targeted assignment
        print("\n[Test 11] Creating targeted assignment...")
        try:
            result, status = InterventionService.create_targeted_assignment(
                teacher_user.id,
                students[2].id,  # Student 3 - struggling
                auto_fill=True
            )
            
            if result.get('success'):
                print(f"✓ Targeted assignment created")
                print(f"  - Assignment: {result['assignment']['title']}")
                print(f"  - Skills: {len(result['assignment']['skill_ids'])} skills")
                print(f"  - Difficulty: {result['assignment']['difficulty']}")
                print(f"  - Intervention ID: {result['intervention_id']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 12: Schedule meeting
        print("\n[Test 12] Scheduling meeting...")
        try:
            meeting_time = datetime.utcnow() + timedelta(days=1, hours=10)
            result, status = InterventionService.schedule_meeting(
                teacher_user.id,
                students[2].id,
                'one_on_one',
                meeting_time,
                duration_minutes=30,
                location='Room 101',
                notes='Discuss fractions and division'
            )
            
            if result.get('success'):
                print(f"✓ Meeting scheduled")
                print(f"  - Type: {result['meeting']['meeting_type']}")
                print(f"  - Duration: {result['meeting']['duration_minutes']} minutes")
                print(f"  - Location: {result['meeting']['location']}")
                print(f"  - Intervention ID: {result['intervention_id']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 13: Notify parent
        print("\n[Test 13] Notifying parent...")
        try:
            result, status = InterventionService.notify_parent(
                teacher_user.id,
                students[2].id,
                'low_performance',
                'Student is struggling with fractions and division. Recommend extra practice at home.'
            )
            
            if result.get('success'):
                print(f"✓ Parent notification sent (placeholder)")
                print(f"  - Intervention ID: {result['intervention_id']}")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 14: Get intervention history
        print("\n[Test 14] Getting intervention history...")
        try:
            result, status = InterventionService.get_intervention_history(
                students[2].id,
                teacher_user.id
            )
            
            if result.get('success'):
                print(f"✓ Intervention history retrieved")
                print(f"  - Total interventions: {result['total']}")
                print(f"  - Resolved: {result['resolved']}")
                print(f"  - Pending: {result['pending']}")
                
                for intervention in result['interventions'][:3]:  # Show first 3
                    print(f"  - {intervention['intervention_type']}: {intervention['action_taken'][:50]}...")
            else:
                print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 15: Mark intervention resolved
        print("\n[Test 15] Marking intervention as resolved...")
        try:
            # Get first intervention
            history_result, _ = InterventionService.get_intervention_history(students[2].id)
            interventions = history_result.get('interventions', [])
            
            if interventions:
                intervention_id = interventions[0]['id']
                
                result, status = InterventionService.mark_intervention_resolved(
                    intervention_id,
                    'Student showed improvement after meeting. Will continue monitoring.',
                    effectiveness_rating=4
                )
                
                if result.get('success'):
                    print(f"✓ Intervention marked as resolved")
                    print(f"  - Intervention ID: {intervention_id}")
                    print(f"  - Effectiveness rating: {result['intervention']['effectiveness_rating']}/5")
                else:
                    print(f"✗ Error: {result.get('error')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 16: Test analytics with no data
        print("\n[Test 16] Testing analytics with non-existent student...")
        try:
            report = AnalyticsService.get_student_performance_report(9999, days=30)
            
            if not report:
                print(f"✓ Correctly returned empty report for non-existent student")
            else:
                print(f"✗ Should return empty report")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 17: Test intervention with non-existent student
        print("\n[Test 17] Testing intervention with non-existent student...")
        try:
            result, status = InterventionService.send_message(
                teacher_user.id,
                9999,
                "Test message"
            )
            
            if status == 404:
                print(f"✓ Correctly returned 404 for non-existent student")
            else:
                print(f"✗ Should return 404")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()

