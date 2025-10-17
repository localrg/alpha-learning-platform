"""
Admin Service for platform administration dashboard.
"""
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.student_session import StudentSession
from src.models.learning_path import LearningPath
from src.models.assignment_model import Assignment
from src.models.admin_models import AuditLog
from datetime import datetime, timedelta
from sqlalchemy import func


class AdminService:
    """Service for admin dashboard and platform metrics"""
    
    @staticmethod
    def get_platform_metrics():
        """Get platform-wide metrics for admin dashboard"""
        try:
            # User counts by role
            total_users = User.query.count()
            students_count = User.query.filter_by(role='student').count()
            teachers_count = User.query.filter_by(role='teacher').count()
            parents_count = User.query.filter_by(role='parent').count()
            admins_count = User.query.filter_by(role='admin').count()
            
            # Active users (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_sessions = StudentSession.query.filter(
                StudentSession.started_at >= week_ago
            ).all()
            active_student_ids = set(s.student_id for s in active_sessions)
            active_users_week = len(active_student_ids)
            
            # Active users (last 30 days)
            month_ago = datetime.utcnow() - timedelta(days=30)
            active_sessions_month = StudentSession.query.filter(
                StudentSession.started_at >= month_ago
            ).all()
            active_student_ids_month = set(s.student_id for s in active_sessions_month)
            active_users_month = len(active_student_ids_month)
            
            # Session metrics
            total_sessions = StudentSession.query.count()
            total_time = db.session.query(
                func.sum(
                    func.julianday(StudentSession.ended_at) - 
                    func.julianday(StudentSession.started_at)
                ) * 24 * 60
            ).filter(StudentSession.ended_at.isnot(None)).scalar() or 0
            
            # Question metrics
            total_questions = db.session.query(
                func.sum(StudentSession.questions_answered)
            ).scalar() or 0
            
            total_correct = db.session.query(
                func.sum(StudentSession.questions_correct)
            ).scalar() or 0
            
            platform_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            # Skills mastered
            skills_mastered = LearningPath.query.filter_by(mastery_achieved=True).count()
            
            # Assignments
            total_assignments = Assignment.query.count()
            
            metrics = {
                'users': {
                    'total': total_users,
                    'students': students_count,
                    'teachers': teachers_count,
                    'parents': parents_count,
                    'admins': admins_count
                },
                'activity': {
                    'active_users_week': active_users_week,
                    'active_users_month': active_users_month,
                    'total_sessions': total_sessions,
                    'total_time_minutes': round(total_time, 1),
                    'total_questions': int(total_questions),
                    'total_correct': int(total_correct),
                    'platform_accuracy': round(platform_accuracy, 1)
                },
                'learning': {
                    'skills_mastered': skills_mastered,
                    'total_assignments': total_assignments
                }
            }
            
            return {'success': True, 'metrics': metrics}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_user_growth(days=30):
        """Get user growth trends"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get users created in the period
            new_users = User.query.filter(
                User.created_at >= start_date
            ).all()
            
            # Group by date
            daily_signups = {}
            for user in new_users:
                date_key = user.created_at.date().isoformat()
                if date_key not in daily_signups:
                    daily_signups[date_key] = {'total': 0, 'students': 0, 'teachers': 0, 'parents': 0}
                
                daily_signups[date_key]['total'] += 1
                if user.role == 'student':
                    daily_signups[date_key]['students'] += 1
                elif user.role == 'teacher':
                    daily_signups[date_key]['teachers'] += 1
                elif user.role == 'parent':
                    daily_signups[date_key]['parents'] += 1
            
            # Convert to list sorted by date
            growth_data = [
                {'date': date, **counts}
                for date, counts in sorted(daily_signups.items())
            ]
            
            # Calculate totals
            total_new_users = len(new_users)
            new_students = sum(1 for u in new_users if u.role == 'student')
            new_teachers = sum(1 for u in new_users if u.role == 'teacher')
            new_parents = sum(1 for u in new_users if u.role == 'parent')
            
            return {
                'success': True,
                'growth': {
                    'period_days': days,
                    'total_new_users': total_new_users,
                    'new_students': new_students,
                    'new_teachers': new_teachers,
                    'new_parents': new_parents,
                    'daily_data': growth_data
                }
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_system_health():
        """Get system health metrics"""
        try:
            # Database size (approximate)
            table_counts = {
                'users': User.query.count(),
                'students': Student.query.count(),
                'sessions': StudentSession.query.count(),
                'learning_paths': LearningPath.query.count(),
                'assignments': Assignment.query.count(),
                'audit_logs': AuditLog.query.count()
            }
            
            # Recent errors from audit logs (if any)
            recent_errors = AuditLog.query.filter(
                AuditLog.action_type == 'error',
                AuditLog.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            # Active sessions (last hour)
            hour_ago = datetime.utcnow() - timedelta(hours=1)
            active_sessions = StudentSession.query.filter(
                StudentSession.started_at >= hour_ago
            ).count()
            
            health = {
                'database': {
                    'table_counts': table_counts,
                    'total_records': sum(table_counts.values())
                },
                'activity': {
                    'active_sessions_last_hour': active_sessions,
                    'errors_last_24h': recent_errors
                },
                'status': 'healthy' if recent_errors < 10 else 'degraded'
            }
            
            return {'success': True, 'health': health}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_recent_activity(limit=20):
        """Get recent platform activity"""
        try:
            # Get recent audit logs
            recent_logs = AuditLog.query.order_by(
                AuditLog.created_at.desc()
            ).limit(limit).all()
            
            activity = [log.to_dict() for log in recent_logs]
            
            return {'success': True, 'activity': activity}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

