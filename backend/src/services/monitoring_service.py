"""
Monitoring Service
Business logic for student monitoring and real-time tracking
"""
from src.database import db
from src.models.student_session import StudentSession
from src.models.student import Student
from src.models.class_group import ClassGroup, ClassMembership
from src.models.learning_path import LearningPath
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.streak import StreakTracking
from datetime import datetime, timedelta


class MonitoringService:
    """Service for monitoring student activity"""
    
    @staticmethod
    def get_active_students(class_id):
        """
        Get students currently active (last 5 minutes)
        
        Args:
            class_id: Class ID
        
        Returns:
            List of active students with current activity
        """
        try:
            # Get class students
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return []
            
            # Get active sessions (last 5 minutes)
            five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            active_sessions = StudentSession.query.filter(
                StudentSession.student_id.in_(student_ids),
                StudentSession.is_active == True,
                StudentSession.last_activity_at >= five_minutes_ago
            ).all()
            
            result = []
            for session in active_sessions:
                student = Student.query.get(session.student_id)
                if not student:
                    continue
                
                skill = session.skill
                skill_name = skill.name if skill else 'Practice'
                
                duration = int((datetime.utcnow() - session.started_at).total_seconds())
                
                result.append({
                    'student_id': student.id,
                    'student_name': student.name,
                    'student_avatar': student.avatar,
                    'skill_name': skill_name,
                    'questions_answered': session.questions_answered,
                    'accuracy': round(session.accuracy, 2),
                    'duration': duration,
                    'started_at': session.started_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_student_status(student_id):
        """
        Calculate student status
        
        Args:
            student_id: Student ID
        
        Returns:
            Status string and metrics
        """
        try:
            # Get average accuracy
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            if paths:
                avg_accuracy = sum(p.current_accuracy for p in paths) / len(paths)
            else:
                avg_accuracy = 0
            
            # Get last active
            last_session = StudentSession.query.filter_by(student_id=student_id).order_by(
                StudentSession.last_activity_at.desc()
            ).first()
            
            if last_session:
                days_inactive = (datetime.utcnow() - last_session.last_activity_at).days
            else:
                days_inactive = 999  # Never active
            
            # Get overdue assignments
            assignment_students = AssignmentStudent.query.filter_by(student_id=student_id).all()
            overdue_count = 0
            for as_record in assignment_students:
                assignment = as_record.assignment
                if assignment.due_date and assignment.due_date < datetime.utcnow() and as_record.status != 'completed':
                    overdue_count += 1
            
            # Determine status
            if days_inactive > 14:
                status = 'inactive'
            elif avg_accuracy < 0.7 or days_inactive > 7 or overdue_count >= 3:
                status = 'needs_help'
            elif avg_accuracy < 0.8 or days_inactive > 3 or overdue_count > 0:
                status = 'needs_practice'
            else:
                status = 'on_track'
            
            return {
                'status': status,
                'avg_accuracy': round(avg_accuracy, 2),
                'days_inactive': days_inactive,
                'overdue_assignments': overdue_count
            }
            
        except Exception as e:
            return {
                'status': 'unknown',
                'avg_accuracy': 0,
                'days_inactive': 999,
                'overdue_assignments': 0
            }
    
    @staticmethod
    def get_class_monitoring_data(class_id, teacher_id):
        """
        Get comprehensive monitoring data for class
        
        Args:
            class_id: Class ID
            teacher_id: Teacher ID (for authorization)
        
        Returns:
            (result_dict, status_code)
        """
        try:
            # Verify teacher owns class
            class_group = ClassGroup.query.get(class_id)
            if not class_group or class_group.teacher_id != teacher_id:
                return {'error': 'Class not found or unauthorized'}, 403
            
            # Get class students
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return {
                    'success': True,
                    'class': class_group.to_dict(),
                    'active_students': [],
                    'students': [],
                    'status_breakdown': {'on_track': 0, 'needs_practice': 0, 'needs_help': 0, 'inactive': 0},
                    'alerts': []
                }, 200
            
            # Get active students
            active_students = MonitoringService.get_active_students(class_id)
            
            # Get all students with status
            students = []
            status_counts = {'on_track': 0, 'needs_practice': 0, 'needs_help': 0, 'inactive': 0}
            
            for student_id in student_ids:
                student = Student.query.get(student_id)
                if not student:
                    continue
                
                status_data = MonitoringService.get_student_status(student_id)
                
                # Get struggling skills
                struggling_skills = MonitoringService._get_struggling_skills(student_id)
                
                # Get last active
                last_session = StudentSession.query.filter_by(student_id=student_id).order_by(
                    StudentSession.last_activity_at.desc()
                ).first()
                
                last_active = last_session.last_activity_at.isoformat() if last_session else None
                
                students.append({
                    'id': student.id,
                    'name': student.name,
                    'avatar': student.avatar,
                    'status': status_data['status'],
                    'avg_accuracy': status_data['avg_accuracy'],
                    'days_inactive': status_data['days_inactive'],
                    'overdue_assignments': status_data['overdue_assignments'],
                    'struggling_skills_count': len(struggling_skills),
                    'last_active': last_active
                })
                
                status_counts[status_data['status']] += 1
            
            # Get alerts
            alerts = MonitoringService.get_class_alerts(class_id, teacher_id)
            
            return {
                'success': True,
                'class': class_group.to_dict(),
                'active_students': active_students,
                'students': students,
                'status_breakdown': status_counts,
                'alerts': alerts
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_struggling_students(class_id, threshold=0.7):
        """Get students with accuracy below threshold"""
        try:
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            struggling = []
            for student_id in student_ids:
                paths = LearningPath.query.filter_by(student_id=student_id).all()
                if not paths:
                    continue
                
                avg_accuracy = sum(p.current_accuracy for p in paths) / len(paths)
                if avg_accuracy < threshold:
                    student = Student.query.get(student_id)
                    struggling_skills = MonitoringService._get_struggling_skills(student_id, threshold)
                    
                    struggling.append({
                        'id': student.id,
                        'name': student.name,
                        'avatar': student.avatar,
                        'avg_accuracy': round(avg_accuracy, 2),
                        'struggling_skills': struggling_skills
                    })
            
            return struggling
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_inactive_students(class_id, days=7):
        """Get students inactive for X days"""
        try:
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            inactive = []
            for student_id in student_ids:
                last_session = StudentSession.query.filter_by(student_id=student_id).order_by(
                    StudentSession.last_activity_at.desc()
                ).first()
                
                if not last_session or last_session.last_activity_at < cutoff_date:
                    student = Student.query.get(student_id)
                    days_inactive = (datetime.utcnow() - last_session.last_activity_at).days if last_session else 999
                    
                    inactive.append({
                        'id': student.id,
                        'name': student.name,
                        'avatar': student.avatar,
                        'last_active': last_session.last_activity_at.isoformat() if last_session else None,
                        'days_inactive': days_inactive
                    })
            
            return inactive
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_student_activity_timeline(student_id, days=7):
        """Get student's activity timeline"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= cutoff_date
            ).order_by(StudentSession.started_at.desc()).all()
            
            timeline = []
            for session in sessions:
                skill = session.skill
                timeline.append({
                    'date': session.started_at.isoformat(),
                    'skill_name': skill.name if skill else 'Practice',
                    'questions_answered': session.questions_answered,
                    'accuracy': round(session.accuracy, 2),
                    'duration': int((session.ended_at - session.started_at).total_seconds()) if session.ended_at else 0
                })
            
            return timeline
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_student_current_session(student_id):
        """Get student's current active session"""
        try:
            five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            session = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.is_active == True,
                StudentSession.last_activity_at >= five_minutes_ago
            ).first()
            
            if session:
                return session.to_dict()
            return None
            
        except Exception as e:
            return None
    
    @staticmethod
    def get_class_alerts(class_id, teacher_id):
        """Generate alerts for class"""
        try:
            # Verify teacher owns class
            class_group = ClassGroup.query.get(class_id)
            if not class_group or class_group.teacher_id != teacher_id:
                return []
            
            alerts = []
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            for student_id in student_ids:
                student = Student.query.get(student_id)
                if not student:
                    continue
                
                status_data = MonitoringService.get_student_status(student_id)
                
                # Inactivity alerts
                if status_data['days_inactive'] >= 7:
                    alerts.append({
                        'severity': 'high',
                        'type': 'inactive',
                        'student_id': student.id,
                        'student_name': student.name,
                        'message': f'{student.name} inactive for {status_data["days_inactive"]} days',
                        'action': 'Send reminder'
                    })
                elif status_data['days_inactive'] >= 3:
                    alerts.append({
                        'severity': 'medium',
                        'type': 'inactive',
                        'student_id': student.id,
                        'student_name': student.name,
                        'message': f'{student.name} inactive for {status_data["days_inactive"]} days',
                        'action': 'Check in'
                    })
                
                # Performance alerts
                if status_data['avg_accuracy'] < 0.6:
                    alerts.append({
                        'severity': 'high',
                        'type': 'low_performance',
                        'student_id': student.id,
                        'student_name': student.name,
                        'message': f'{student.name} accuracy at {status_data["avg_accuracy"]:.0%}',
                        'action': 'Create targeted assignment'
                    })
                elif status_data['avg_accuracy'] < 0.7:
                    alerts.append({
                        'severity': 'medium',
                        'type': 'low_performance',
                        'student_id': student.id,
                        'student_name': student.name,
                        'message': f'{student.name} accuracy at {status_data["avg_accuracy"]:.0%}',
                        'action': 'Monitor progress'
                    })
                
                # Assignment alerts
                if status_data['overdue_assignments'] >= 3:
                    alerts.append({
                        'severity': 'high',
                        'type': 'overdue_assignments',
                        'student_id': student.id,
                        'student_name': student.name,
                        'message': f'{student.name} has {status_data["overdue_assignments"]} overdue assignments',
                        'action': 'Message student'
                    })
                elif status_data['overdue_assignments'] > 0:
                    alerts.append({
                        'severity': 'medium',
                        'type': 'overdue_assignments',
                        'student_id': student.id,
                        'student_name': student.name,
                        'message': f'{student.name} has {status_data["overdue_assignments"]} overdue assignment(s)',
                        'action': 'Send reminder'
                    })
            
            # Sort by severity
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            alerts.sort(key=lambda x: priority_order[x['severity']])
            
            return alerts
            
        except Exception as e:
            return []
    
    @staticmethod
    def track_session_activity(student_id, skill_id, question_id, correct):
        """Track real-time session activity"""
        try:
            # Get or create active session
            session = StudentSession.query.filter_by(
                student_id=student_id,
                is_active=True
            ).order_by(StudentSession.started_at.desc()).first()
            
            if not session:
                session = StudentSession(
                    student_id=student_id,
                    skill_id=skill_id
                )
                db.session.add(session)
            
            # Update session
            session.questions_answered += 1
            if correct:
                session.questions_correct += 1
            session.accuracy = session.questions_correct / session.questions_answered if session.questions_answered > 0 else 0
            session.last_activity_at = datetime.utcnow()
            
            db.session.commit()
            return {'success': True, 'session': session.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def start_session(student_id, skill_id=None):
        """Start a new practice session"""
        try:
            # End any existing active sessions
            active_sessions = StudentSession.query.filter_by(
                student_id=student_id,
                is_active=True
            ).all()
            
            for session in active_sessions:
                session.is_active = False
                session.ended_at = datetime.utcnow()
            
            # Create new session
            session = StudentSession(
                student_id=student_id,
                skill_id=skill_id
            )
            db.session.add(session)
            db.session.commit()
            
            return {'success': True, 'session': session.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def end_session(session_id):
        """End a practice session"""
        try:
            session = StudentSession.query.get(session_id)
            if not session:
                return {'error': 'Session not found'}, 404
            
            session.is_active = False
            session.ended_at = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'session': session.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_assignment_compliance(class_id):
        """Get assignment completion rates"""
        try:
            # Get all assignments for class
            assignments = Assignment.query.filter_by(class_id=class_id).all()
            
            total_assignments = len(assignments)
            total_assigned = 0
            total_completed = 0
            total_on_time = 0
            
            for assignment in assignments:
                for as_record in assignment.student_assignments:
                    total_assigned += 1
                    if as_record.status == 'completed':
                        total_completed += 1
                        if assignment.due_date and as_record.completed_at <= assignment.due_date:
                            total_on_time += 1
            
            completion_rate = total_completed / total_assigned if total_assigned > 0 else 0
            on_time_rate = total_on_time / total_assigned if total_assigned > 0 else 0
            
            return {
                'total_assignments': total_assignments,
                'total_assigned': total_assigned,
                'total_completed': total_completed,
                'total_on_time': total_on_time,
                'completion_rate': round(completion_rate, 2),
                'on_time_rate': round(on_time_rate, 2)
            }
            
        except Exception as e:
            return {}
    
    # Helper methods
    
    @staticmethod
    def _get_struggling_skills(student_id, threshold=0.7):
        """Get skills student is struggling with"""
        try:
            paths = LearningPath.query.filter(
                LearningPath.student_id == student_id,
                LearningPath.current_accuracy < threshold
            ).all()
            
            struggling = []
            for path in paths:
                skill = path.skill
                if skill:
                    struggling.append({
                        'skill_name': skill.name,
                        'accuracy': round(path.current_accuracy, 2)
                    })
            
            return struggling
            
        except Exception as e:
            return []

