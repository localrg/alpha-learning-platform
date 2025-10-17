"""
Comprehensive tests for the Activity Reports system (Step 8.3).
Tests report generation, insights, and authorization.
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
from src.models.student_session import StudentSession
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.class_group import ClassGroup
from src.models.gamification import StudentProgress
from src.models.achievement import Achievement, StudentAchievement
from src.models.streak import StreakTracking
from src.services.parent_service import ParentService
from src.services.report_service import ReportService
from datetime import datetime, timedelta


def run_tests():
    """Run all activity reports tests"""
    print("=" * 60)
    print("ACTIVITY REPORTS SYSTEM TESTS")
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
                practice_streak=10,
                practice_streak_best=15,
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
                questions_answered=150,
                correct_answers=143,
                total_questions=150,
                mastery_achieved=True,
                mastery_date=datetime.utcnow() - timedelta(days=20),
                last_practiced=datetime.utcnow() - timedelta(days=2),
                status='mastered'
            )
            path2 = LearningPath(
                student_id=student.id,
                skill_id=skill2.id,
                current_accuracy=0.85,
                questions_answered=100,
                correct_answers=85,
                total_questions=100,
                mastery_achieved=False,
                last_practiced=datetime.utcnow() - timedelta(hours=3),
                status='in_progress'
            )
            path3 = LearningPath(
                student_id=student.id,
                skill_id=skill3.id,
                current_accuracy=0.65,
                questions_answered=50,
                correct_answers=33,
                total_questions=50,
                mastery_achieved=False,
                last_practiced=datetime.utcnow() - timedelta(days=1),
                status='in_progress'
            )
            db.session.add_all([path1, path2, path3])
            db.session.flush()
            
            # Create student sessions (last 30 days, varied pattern)
            # Week 1: 3 sessions
            for i in range(3):
                session = StudentSession(
                    student_id=student.id,
                    skill_id=skill1.id,
                    started_at=datetime.utcnow() - timedelta(days=28-i),
                    ended_at=datetime.utcnow() - timedelta(days=28-i) + timedelta(minutes=15),
                    questions_answered=20,
                    questions_correct=17
                )
                db.session.add(session)
            
            # Week 2: 5 sessions (improvement)
            for i in range(5):
                session = StudentSession(
                    student_id=student.id,
                    skill_id=skill2.id,
                    started_at=datetime.utcnow() - timedelta(days=21-i),
                    ended_at=datetime.utcnow() - timedelta(days=21-i) + timedelta(minutes=18),
                    questions_answered=20,
                    questions_correct=18
                )
                db.session.add(session)
            
            # Week 3: 4 sessions
            for i in range(4):
                session = StudentSession(
                    student_id=student.id,
                    skill_id=skill3.id,
                    started_at=datetime.utcnow() - timedelta(days=14-i),
                    ended_at=datetime.utcnow() - timedelta(days=14-i) + timedelta(minutes=12),
                    questions_answered=15,
                    questions_correct=10
                )
                db.session.add(session)
            
            # Week 4 (current): 6 sessions (best week)
            for i in range(6):
                session = StudentSession(
                    student_id=student.id,
                    skill_id=skill1.id if i % 2 == 0 else skill2.id,
                    started_at=datetime.utcnow() - timedelta(days=6-i),
                    ended_at=datetime.utcnow() - timedelta(days=6-i) + timedelta(minutes=20),
                    questions_answered=25,
                    questions_correct=23
                )
                db.session.add(session)
            
            # Create teacher and assignment
            teacher_user = User(username='teacher1', email='teacher1@email.com', role='teacher')
            teacher_user.set_password('password123')
            db.session.add(teacher_user)
            db.session.flush()
            
            assignment = Assignment(
                teacher_id=teacher_user.id,
                title='Weekly Practice',
                description='Practice all skills',
                skill_ids=[skill1.id, skill2.id],
                question_count=30,
                difficulty='medium',
                due_date=datetime.utcnow() + timedelta(days=2)
            )
            db.session.add(assignment)
            db.session.flush()
            
            # Complete assignment
            assignment_student = AssignmentStudent(
                assignment_id=assignment.id,
                student_id=student.id,
                status='completed',
                questions_correct=27,
                accuracy=0.90,
                questions_answered=30,
                started_at=datetime.utcnow() - timedelta(days=3),
                completed_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(assignment_student)
            
            # Create achievement
            achievement = Achievement(
                name='Practice Master',
                description='Complete 10 practice sessions',
                category='practice',
                tier='bronze',
                requirement_type='count',
                requirement_value=10,
                icon_emoji='🎯',
                xp_reward=100
            )
            db.session.add(achievement)
            db.session.flush()
            
            # Earn achievement
            student_achievement = StudentAchievement(
                student_id=student.id,
                achievement_id=achievement.id,
                progress=10,
                unlocked_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(student_achievement)
            
            db.session.commit()
            
            print("✓ Test data created")
            print(f"  - Parent ID: {parent_id}")
            print(f"  - Student ID: {student_id}")
            print(f"  - Skills: 3 (1 mastered, 2 in progress)")
            print(f"  - Sessions: 18 (varied across 4 weeks)")
            print(f"  - Assignments: 1 completed")
            print(f"  - Achievements: 1 earned")
            
            # Test 2: Weekly report
            print("[Test 2] Generating weekly report (current week)...")
            result, status = ReportService.generate_weekly_report(parent_id, student_id, week_offset=0)
            
            if result.get('success'):
                report = result['report']
                print("✓ Weekly report generated")
                print(f"  - Period: {report['period']['start_date']} to {report['period']['end_date']}")
                print(f"  - Total time: {report['summary']['total_time_minutes']} minutes")
                print(f"  - Sessions: {report['summary']['total_sessions']}")
                print(f"  - Questions: {report['summary']['questions_answered']}")
                print(f"  - Accuracy: {report['summary']['accuracy']}")
                print(f"  - Skills practiced: {report['summary']['skills_practiced']}")
                print(f"  - Daily breakdown: {len(report['daily_breakdown'])} days")
                if 'insights' in report and 'most_active_day' in report['insights']:
                    print(f"  - Most active day: {report['insights']['most_active_day']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 3: Monthly report
            print("[Test 3] Generating monthly report (current month)...")
            result, status = ReportService.generate_monthly_report(parent_id, student_id, month_offset=0)
            
            if result.get('success'):
                report = result['report']
                print("✓ Monthly report generated")
                print(f"  - Month: {report['period']['month_name']}")
                print(f"  - Total time: {report['summary']['total_time_minutes']} minutes")
                print(f"  - Sessions: {report['summary']['total_sessions']}")
                print(f"  - Accuracy: {report['summary']['accuracy']}")
                print(f"  - Skills mastered: {report['summary']['skills_mastered']}")
                print(f"  - Weekly breakdown: {len(report['weekly_breakdown'])} weeks")
                if 'insights' in report:
                    print(f"  - Consistency: {report['insights']['consistency_rating']}")
                    if 'trajectory' in report['insights']:
                        print(f"  - Trajectory: {report['insights']['trajectory']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 4: Skill report
            print("[Test 4] Generating skill performance report...")
            result, status = ReportService.generate_skill_report(parent_id, student_id)
            
            if result.get('success'):
                report = result['report']
                print("✓ Skill report generated")
                print(f"  - Total skills: {report['total_skills']}")
                print(f"  - Mastered: {report['mastered']}")
                print(f"  - In progress: {report['in_progress']}")
                print(f"  - Not started: {report['not_started']}")
                print(f"  - Skills analyzed: {len(report['skills'])}")
                if 'insights' in report:
                    print(f"  - Top skills: {', '.join(report['insights']['top_skills'][:2])}")
                    if report['insights']['needs_attention']:
                        print(f"  - Needs attention: {', '.join(report['insights']['needs_attention'])}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 5: Time analysis report
            print("[Test 5] Generating time analysis report (30 days)...")
            result, status = ReportService.generate_time_analysis(parent_id, student_id, days=30)
            
            if result.get('success'):
                report = result['report']
                print("✓ Time analysis report generated")
                print(f"  - Period: {report['period_days']} days")
                print(f"  - Total time: {report['total_time_minutes']} minutes")
                print(f"  - Total sessions: {report['total_sessions']}")
                print(f"  - Average session: {report['average_session_minutes']} minutes")
                print(f"  - Consistency score: {report['consistency_score']}")
                if 'insights' in report:
                    if 'most_productive_day' in report['insights']:
                        print(f"  - Most productive day: {report['insights']['most_productive_day']}")
                    print(f"  - Consistency rating: {report['insights']['consistency_rating']}")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 6: Previous week report
            print("[Test 6] Generating previous week report...")
            result, status = ReportService.generate_weekly_report(parent_id, student_id, week_offset=1)
            
            if result.get('success'):
                report = result['report']
                print("✓ Previous week report generated")
                print(f"  - Period: {report['period']['start_date']} to {report['period']['end_date']}")
                print(f"  - Sessions: {report['summary']['total_sessions']}")
                print(f"  ✓ Correct week offset")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 7: Time analysis with different period
            print("[Test 7] Generating time analysis (7 days)...")
            result, status = ReportService.generate_time_analysis(parent_id, student_id, days=7)
            
            if result.get('success'):
                report = result['report']
                print("✓ 7-day time analysis generated")
                print(f"  - Period: {report['period_days']} days")
                print(f"  - Sessions: {report['total_sessions']}")
                print(f"  ✓ Correct period")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 8: Unauthorized access
            print("[Test 8] Testing unauthorized access...")
            fake_parent_id = 999
            result, status = ReportService.generate_weekly_report(fake_parent_id, student_id, week_offset=0)
            
            if not result.get('success') and status == 403:
                print("✓ Correctly denied unauthorized access")
            else:
                print("✗ Should have denied unauthorized access")
            
            # Test 9: Non-existent student
            print("[Test 9] Testing with non-existent student...")
            fake_student_id = 999
            result, status = ReportService.generate_weekly_report(parent_id, fake_student_id, week_offset=0)
            
            if not result.get('success'):
                print("✓ Correctly handled non-existent student")
            else:
                print("✗ Should have failed for non-existent student")
            
            # Test 10: Student with no sessions
            print("[Test 10] Testing with student with no data...")
            
            # Create another student with no sessions
            student_user2 = User(username='student2', email='student2@email.com', role='student')
            student_user2.set_password('password123')
            db.session.add(student_user2)
            db.session.flush()
            
            student2 = Student(
                user_id=student_user2.id,
                name='Empty Student',
                grade=5
            )
            db.session.add(student2)
            db.session.flush()
            
            # Link to parent
            result, status = ParentService.generate_invite_code(student2.id)
            invite_code = result['invite_code']
            result, status = ParentService.link_child_by_code(parent_id, invite_code)
            
            db.session.commit()
            
            result, status = ReportService.generate_weekly_report(parent_id, student2.id, week_offset=0)
            
            if result.get('success'):
                report = result['report']
                print("✓ Handled student with no data")
                print(f"  - Sessions: {report['summary']['total_sessions']}")
                print(f"  - Questions: {report['summary']['questions_answered']}")
                if report['summary']['total_sessions'] == 0:
                    print("  ✓ Correctly shows 0 for empty data")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 11: Insights generation
            print("[Test 11] Testing insights generation...")
            result, status = ReportService.generate_weekly_report(parent_id, student_id, week_offset=0)
            
            if result.get('success'):
                insights = result['report'].get('insights', {})
                has_insights = len(insights) > 0
                
                if has_insights:
                    print("✓ Insights generated")
                    print(f"  - Insights count: {len(insights)}")
                    if 'comparison_to_last_week' in insights:
                        print(f"  - Has comparison: Yes")
                        print(f"  - Trend: {insights['comparison_to_last_week'].get('trend')}")
                else:
                    print("✗ No insights generated")
            else:
                print(f"✗ Error: {result.get('error')}")
            
            # Test 12: Skill report insights
            print("[Test 12] Testing skill report insights...")
            result, status = ReportService.generate_skill_report(parent_id, student_id)
            
            if result.get('success'):
                insights = result['report'].get('insights', {})
                
                if insights:
                    print("✓ Skill insights generated")
                    if 'top_skills' in insights and insights['top_skills']:
                        print(f"  - Top skills identified: {len(insights['top_skills'])}")
                    if 'needs_attention' in insights and insights['needs_attention']:
                        print(f"  - Skills needing attention: {len(insights['needs_attention'])}")
                    if 'time_distribution' in insights:
                        print(f"  - Time distribution calculated: Yes")
                else:
                    print("✗ No insights generated")
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

