"""
Analytics Dashboard Service for learning analytics and insights.
"""
from src.database import db
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.class_group import ClassGroup, ClassMembership
from src.models.streak import StreakTracking
from src.models.gamification import StudentProgress
from datetime import datetime, timedelta
from sqlalchemy import func, and_


class AnalyticsDashboardService:
    """Service for learning analytics and dashboard data"""
    
    @staticmethod
    def get_student_dashboard(student_id, days=30):
        """Get comprehensive analytics dashboard for student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Date range
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get sessions in period
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_date
            ).all()
            
            # Calculate metrics
            total_time = sum(
                (s.ended_at - s.started_at).total_seconds() / 60
                if s.ended_at else 0
                for s in sessions
            )
            
            total_sessions = len(sessions)
            total_questions = sum(s.questions_answered or 0 for s in sessions)
            total_correct = sum(s.questions_correct or 0 for s in sessions)
            avg_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            # Learning velocity (skills mastered in period)
            skills_mastered = LearningPath.query.filter(
                LearningPath.student_id == student_id,
                LearningPath.mastery_achieved == True,
                LearningPath.last_practiced >= start_date
            ).count()
            
            weeks = days / 7
            learning_velocity = skills_mastered / weeks if weeks > 0 else 0
            
            # Engagement score
            engagement_score = AnalyticsDashboardService.calculate_engagement_score(student_id, days)
            
            # Practice consistency
            days_with_practice = len(set(
                s.started_at.date() for s in sessions
            ))
            consistency_score = (days_with_practice / days) * 100
            
            # Trend data (daily aggregates)
            daily_data = AnalyticsDashboardService._get_daily_aggregates(student_id, days)
            
            # Subject distribution
            subject_distribution = AnalyticsDashboardService._get_subject_distribution(student_id)
            
            dashboard = {
                'student_id': student_id,
                'student_name': student.name,
                'period_days': days,
                'summary': {
                    'total_time_minutes': round(total_time, 1),
                    'total_sessions': total_sessions,
                    'total_questions': total_questions,
                    'average_accuracy': round(avg_accuracy, 1),
                    'skills_mastered': skills_mastered,
                    'learning_velocity': round(learning_velocity, 2),
                    'engagement_score': round(engagement_score, 1),
                    'consistency_score': round(consistency_score, 1),
                    'days_with_practice': days_with_practice
                },
                'trends': {
                    'daily_practice_time': daily_data['time'],
                    'daily_accuracy': daily_data['accuracy'],
                    'daily_questions': daily_data['questions']
                },
                'distribution': {
                    'by_subject': subject_distribution
                }
            }
            
            return {'success': True, 'dashboard': dashboard}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_teacher_dashboard(teacher_id, class_id=None):
        """Get analytics dashboard for teacher (optionally filtered by class)"""
        try:
            # Get classes taught by teacher
            if class_id:
                classes = ClassGroup.query.filter_by(id=class_id, teacher_id=teacher_id).all()
            else:
                classes = ClassGroup.query.filter_by(teacher_id=teacher_id).all()
            
            if not classes:
                return {'success': False, 'error': 'No classes found'}, 404
            
            # Aggregate metrics across all classes
            total_students = 0
            on_track = 0
            needs_practice = 0
            struggling = 0
            
            class_data = []
            
            for cls in classes:
                students = [m.student_id for m in cls.memberships]
                total_students += len(students)
                
                # Categorize students
                for student_id in students:
                    status = AnalyticsDashboardService._get_student_status(student_id)
                    if status == 'on_track':
                        on_track += 1
                    elif status == 'needs_practice':
                        needs_practice += 1
                    else:
                        struggling += 1
                
                # Class-level metrics
                class_avg_accuracy = AnalyticsDashboardService._get_class_average_accuracy(cls.id)
                class_engagement = AnalyticsDashboardService._get_class_engagement(cls.id)
                
                class_data.append({
                    'class_id': cls.id,
                    'class_name': cls.name,
                    'student_count': len(students),
                    'average_accuracy': round(class_avg_accuracy, 1),
                    'engagement_score': round(class_engagement, 1)
                })
            
            dashboard = {
                'teacher_id': teacher_id,
                'summary': {
                    'total_classes': len(classes),
                    'total_students': total_students,
                    'on_track': on_track,
                    'needs_practice': needs_practice,
                    'struggling': struggling,
                    'on_track_percent': round((on_track / total_students * 100) if total_students > 0 else 0, 1)
                },
                'classes': class_data,
                'student_distribution': {
                    'on_track': on_track,
                    'needs_practice': needs_practice,
                    'struggling': struggling
                }
            }
            
            return {'success': True, 'dashboard': dashboard}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_comparative_analytics(student_id, comparison_type='class'):
        """Get comparative analytics (student vs class/grade average)"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get student metrics
            student_metrics = AnalyticsDashboardService._get_student_metrics(student_id)
            
            # Get comparison group
            if comparison_type == 'class':
                # Find student's class
                membership = ClassMembership.query.filter_by(student_id=student_id).first()
                if not membership:
                    return {'success': False, 'error': 'Student not in any class'}, 404
                
                comparison_metrics = AnalyticsDashboardService._get_class_metrics(membership.class_id, exclude_student=student_id)
                comparison_label = f"Class {membership.class_group.name}"
            
            elif comparison_type == 'grade':
                comparison_metrics = AnalyticsDashboardService._get_grade_metrics(student.grade, exclude_student=student_id)
                comparison_label = f"Grade {student.grade}"
            
            else:
                return {'success': False, 'error': 'Invalid comparison type'}, 400
            
            # Calculate differences
            comparison = {
                'student_id': student_id,
                'comparison_type': comparison_type,
                'comparison_label': comparison_label,
                'student': student_metrics,
                'comparison_group': comparison_metrics,
                'differences': {
                    'accuracy': round(student_metrics['accuracy'] - comparison_metrics['accuracy'], 1),
                    'practice_time': round(student_metrics['practice_time'] - comparison_metrics['practice_time'], 1),
                    'engagement_score': round(student_metrics['engagement_score'] - comparison_metrics['engagement_score'], 1),
                    'learning_velocity': round(student_metrics['learning_velocity'] - comparison_metrics['learning_velocity'], 2)
                }
            }
            
            return {'success': True, 'comparison': comparison}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def calculate_engagement_score(student_id, days=30):
        """Calculate composite engagement score (0-100)"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get sessions
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_date
            ).all()
            
            if not sessions:
                return 0.0
            
            # Component scores (each 0-100)
            
            # 1. Session frequency (30% weight)
            session_count = len(sessions)
            expected_sessions = days * 0.5  # Expect 0.5 sessions per day
            frequency_score = min((session_count / expected_sessions) * 100, 100) if expected_sessions > 0 else 0
            
            # 2. Practice time (25% weight)
            total_time = sum(
                (s.ended_at - s.started_at).total_seconds() / 60
                if s.ended_at else 0
                for s in sessions
            )
            expected_time = days * 15  # Expect 15 min per day
            time_score = min((total_time / expected_time) * 100, 100) if expected_time > 0 else 0
            
            # 3. Accuracy (25% weight)
            total_questions = sum(s.questions_answered or 0 for s in sessions)
            total_correct = sum(s.questions_correct or 0 for s in sessions)
            accuracy_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            # 4. Consistency (20% weight)
            days_with_practice = len(set(s.started_at.date() for s in sessions))
            consistency_score = (days_with_practice / days) * 100
            
            # Weighted average
            engagement_score = (
                frequency_score * 0.30 +
                time_score * 0.25 +
                accuracy_score * 0.25 +
                consistency_score * 0.20
            )
            
            return engagement_score
            
        except Exception as e:
            return 0.0
    
    @staticmethod
    def _get_daily_aggregates(student_id, days):
        """Get daily aggregated data for trends"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = StudentSession.query.filter(
            StudentSession.student_id == student_id,
            StudentSession.started_at >= start_date
        ).all()
        
        # Group by date
        daily_data = {}
        for session in sessions:
            date_key = session.started_at.date().isoformat()
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'time': 0,
                    'questions': 0,
                    'correct': 0
                }
            
            if session.ended_at:
                daily_data[date_key]['time'] += (session.ended_at - session.started_at).total_seconds() / 60
            daily_data[date_key]['questions'] += session.questions_answered or 0
            daily_data[date_key]['correct'] += session.questions_correct or 0
        
        # Calculate accuracy for each day
        for date_key in daily_data:
            q = daily_data[date_key]['questions']
            c = daily_data[date_key]['correct']
            daily_data[date_key]['accuracy'] = (c / q * 100) if q > 0 else 0
        
        # Convert to lists for charting
        sorted_dates = sorted(daily_data.keys())
        
        return {
            'time': [{'date': d, 'value': round(daily_data[d]['time'], 1)} for d in sorted_dates],
            'accuracy': [{'date': d, 'value': round(daily_data[d]['accuracy'], 1)} for d in sorted_dates],
            'questions': [{'date': d, 'value': daily_data[d]['questions']} for d in sorted_dates]
        }
    
    @staticmethod
    def _get_subject_distribution(student_id):
        """Get practice time distribution by subject"""
        paths = LearningPath.query.filter_by(student_id=student_id).all()
        
        subject_time = {}
        for path in paths:
            if path.skill:
                subject = path.skill.subject_area
                if subject not in subject_time:
                    subject_time[subject] = 0
                # Estimate time from questions answered (assume 1 min per question)
                subject_time[subject] += path.questions_answered
        
        return [{'subject': k, 'time_estimate': v} for k, v in subject_time.items()]
    
    @staticmethod
    def _get_student_status(student_id):
        """Determine student status (on_track, needs_practice, struggling)"""
        # Get recent sessions (last 7 days)
        start_date = datetime.utcnow() - timedelta(days=7)
        sessions = StudentSession.query.filter(
            StudentSession.student_id == student_id,
            StudentSession.started_at >= start_date
        ).all()
        
        if not sessions:
            return 'struggling'  # No recent practice
        
        # Calculate average accuracy
        total_questions = sum(s.questions_answered or 0 for s in sessions)
        total_correct = sum(s.questions_correct or 0 for s in sessions)
        avg_accuracy = (total_correct / total_questions) if total_questions > 0 else 0
        
        if avg_accuracy >= 0.80:
            return 'on_track'
        elif avg_accuracy >= 0.60:
            return 'needs_practice'
        else:
            return 'struggling'
    
    @staticmethod
    def _get_class_average_accuracy(class_id):
        """Get average accuracy for class"""
        memberships = ClassMembership.query.filter_by(class_id=class_id).all()
        student_ids = [m.student_id for m in memberships]
        
        if not student_ids:
            return 0.0
        
        # Get recent sessions for all students
        start_date = datetime.utcnow() - timedelta(days=30)
        sessions = StudentSession.query.filter(
            StudentSession.student_id.in_(student_ids),
            StudentSession.started_at >= start_date
        ).all()
        
        total_questions = sum(s.questions_answered or 0 for s in sessions)
        total_correct = sum(s.questions_correct or 0 for s in sessions)
        
        return (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    @staticmethod
    def _get_class_engagement(class_id):
        """Get average engagement score for class"""
        memberships = ClassMembership.query.filter_by(class_id=class_id).all()
        student_ids = [m.student_id for m in memberships]
        
        if not student_ids:
            return 0.0
        
        scores = [AnalyticsDashboardService.calculate_engagement_score(sid, 30) for sid in student_ids]
        return sum(scores) / len(scores) if scores else 0
    
    @staticmethod
    def _get_student_metrics(student_id):
        """Get metrics for a single student"""
        sessions = StudentSession.query.filter_by(student_id=student_id).all()
        
        total_time = sum(
            (s.ended_at - s.started_at).total_seconds() / 60
            if s.ended_at else 0
            for s in sessions
        )
        
        total_questions = sum(s.questions_answered or 0 for s in sessions)
        total_correct = sum(s.questions_correct or 0 for s in sessions)
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        skills_mastered = LearningPath.query.filter_by(
            student_id=student_id,
            mastery_achieved=True
        ).count()
        
        engagement_score = AnalyticsDashboardService.calculate_engagement_score(student_id, 30)
        
        return {
            'accuracy': round(accuracy, 1),
            'practice_time': round(total_time, 1),
            'skills_mastered': skills_mastered,
            'learning_velocity': round(skills_mastered / 4, 2),  # Assume 4 weeks
            'engagement_score': round(engagement_score, 1)
        }
    
    @staticmethod
    def _get_class_metrics(class_id, exclude_student=None):
        """Get average metrics for a class"""
        memberships = ClassMembership.query.filter_by(class_id=class_id).all()
        student_ids = [m.student_id for m in memberships if m.student_id != exclude_student]
        
        if not student_ids:
            return {
                'accuracy': 0,
                'practice_time': 0,
                'skills_mastered': 0,
                'learning_velocity': 0,
                'engagement_score': 0
            }
        
        # Aggregate metrics
        metrics = [AnalyticsDashboardService._get_student_metrics(sid) for sid in student_ids]
        
        return {
            'accuracy': round(sum(m['accuracy'] for m in metrics) / len(metrics), 1),
            'practice_time': round(sum(m['practice_time'] for m in metrics) / len(metrics), 1),
            'skills_mastered': round(sum(m['skills_mastered'] for m in metrics) / len(metrics), 1),
            'learning_velocity': round(sum(m['learning_velocity'] for m in metrics) / len(metrics), 2),
            'engagement_score': round(sum(m['engagement_score'] for m in metrics) / len(metrics), 1)
        }
    
    @staticmethod
    def _get_grade_metrics(grade, exclude_student=None):
        """Get average metrics for a grade level"""
        students = Student.query.filter_by(grade=grade).all()
        student_ids = [s.id for s in students if s.id != exclude_student]
        
        if not student_ids:
            return {
                'accuracy': 0,
                'practice_time': 0,
                'skills_mastered': 0,
                'learning_velocity': 0,
                'engagement_score': 0
            }
        
        # Sample up to 50 students for performance
        if len(student_ids) > 50:
            import random
            student_ids = random.sample(student_ids, 50)
        
        metrics = [AnalyticsDashboardService._get_student_metrics(sid) for sid in student_ids]
        
        return {
            'accuracy': round(sum(m['accuracy'] for m in metrics) / len(metrics), 1),
            'practice_time': round(sum(m['practice_time'] for m in metrics) / len(metrics), 1),
            'skills_mastered': round(sum(m['skills_mastered'] for m in metrics) / len(metrics), 1),
            'learning_velocity': round(sum(m['learning_velocity'] for m in metrics) / len(metrics), 2),
            'engagement_score': round(sum(m['engagement_score'] for m in metrics) / len(metrics), 1)
        }

