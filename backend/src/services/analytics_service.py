"""
Analytics Service
Business logic for performance analytics and reporting
"""
from src.database import db
from src.models.student import Student
from src.models.student_session import StudentSession
from src.models.learning_path import LearningPath
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.class_group import ClassGroup, ClassMembership
from src.models.assessment import Skill
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Service for performance analytics and reporting"""
    
    @staticmethod
    def get_student_performance_report(student_id, days=30):
        """
        Get comprehensive performance report for student
        
        Args:
            student_id: Student ID
            days: Number of days to include in report
        
        Returns:
            Performance report dictionary
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                return {}
            
            # Get date range
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get sessions in date range
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_date
            ).all()
            
            # Calculate overall metrics
            total_questions = sum(s.questions_answered for s in sessions)
            total_correct = sum(s.questions_correct for s in sessions)
            total_time = sum((s.ended_at - s.started_at).total_seconds() if s.ended_at else 0 for s in sessions)
            avg_accuracy = total_correct / total_questions if total_questions > 0 else 0
            
            # Get skill breakdown
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            skill_breakdown = []
            for path in paths:
                skill = path.skill
                if skill:
                    mastery_status = 'mastered' if path.mastery_achieved else 'in_progress' if path.status == 'in_progress' else 'not_started'
                    skill_breakdown.append({
                        'skill_id': skill.id,
                        'skill_name': skill.name,
                        'accuracy': round(path.current_accuracy, 2),
                        'mastery': mastery_status,
                        'questions': path.questions_answered
                    })
            
            # Get trend data
            trend_data = AnalyticsService.get_student_trend_data(student_id, 'accuracy', days)
            
            # Get class comparison
            comparison = AnalyticsService.get_student_comparison(student_id)
            
            # Count skills mastered
            skills_mastered = sum(1 for s in skill_breakdown if s['mastery'] == 'mastered')
            
            return {
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'grade': student.grade
                },
                'overall': {
                    'accuracy': round(avg_accuracy, 2),
                    'questions': total_questions,
                    'time_hours': round(total_time / 3600, 1),
                    'skills_mastered': skills_mastered,
                    'total_skills': len(skill_breakdown),
                    'sessions': len(sessions)
                },
                'skills': skill_breakdown,
                'trends': trend_data,
                'comparison': comparison
            }
            
        except Exception as e:
            return {}
    
    @staticmethod
    def get_class_performance_report(class_id, days=30):
        """Get comprehensive performance report for class"""
        try:
            class_group = ClassGroup.query.get(class_id)
            if not class_group:
                return {}
            
            # Get class students
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return {}
            
            # Get date range
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all sessions for class students
            sessions = StudentSession.query.filter(
                StudentSession.student_id.in_(student_ids),
                StudentSession.started_at >= start_date
            ).all()
            
            # Calculate class-wide metrics
            total_questions = sum(s.questions_answered for s in sessions)
            total_correct = sum(s.questions_correct for s in sessions)
            avg_accuracy = total_correct / total_questions if total_questions > 0 else 0
            
            # Get active students (practiced in last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_student_ids = set(s.student_id for s in sessions if s.started_at >= week_ago)
            engagement_rate = len(active_student_ids) / len(student_ids) if student_ids else 0
            
            # Get student distribution
            student_accuracies = []
            for student_id in student_ids:
                paths = LearningPath.query.filter_by(student_id=student_id).all()
                if paths:
                    student_avg = sum(p.current_accuracy for p in paths) / len(paths)
                    student_accuracies.append(student_avg)
            
            # Calculate distribution
            distribution = {
                'excellent': sum(1 for a in student_accuracies if a >= 0.9),
                'good': sum(1 for a in student_accuracies if 0.8 <= a < 0.9),
                'fair': sum(1 for a in student_accuracies if 0.7 <= a < 0.8),
                'needs_improvement': sum(1 for a in student_accuracies if a < 0.7)
            }
            
            # Get skill heatmap (which skills the class struggles with)
            skill_analytics = AnalyticsService._get_class_skill_heatmap(class_id)
            
            # Get trend data
            trend_data = AnalyticsService.get_class_trend_data(class_id, 'accuracy', days)
            
            # Get top performers and struggling students
            student_rankings = []
            for student_id in student_ids:
                student = Student.query.get(student_id)
                paths = LearningPath.query.filter_by(student_id=student_id).all()
                avg_acc = sum(p.current_accuracy for p in paths) / len(paths) if paths else 0
                student_rankings.append({
                    'student_id': student_id,
                    'student_name': student.name if student else 'Unknown',
                    'accuracy': round(avg_acc, 2)
                })
            
            student_rankings.sort(key=lambda x: x['accuracy'], reverse=True)
            top_performers = student_rankings[:5]
            struggling_students = [s for s in student_rankings if s['accuracy'] < 0.7]
            
            return {
                'class': {
                    'id': class_group.id,
                    'name': class_group.name,
                    'grade_level': class_group.grade_level,
                    'student_count': len(student_ids)
                },
                'overall': {
                    'avg_accuracy': round(avg_accuracy, 2),
                    'total_questions': total_questions,
                    'engagement_rate': round(engagement_rate, 2),
                    'active_students': len(active_student_ids),
                    'total_sessions': len(sessions)
                },
                'distribution': distribution,
                'skill_heatmap': skill_analytics,
                'trends': trend_data,
                'top_performers': top_performers,
                'struggling_students': struggling_students
            }
            
        except Exception as e:
            return {}
    
    @staticmethod
    def get_student_trend_data(student_id, metric='accuracy', days=30):
        """Get trend data for student"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_date
            ).order_by(StudentSession.started_at).all()
            
            # Group by day
            daily_data = defaultdict(lambda: {'questions': 0, 'correct': 0, 'time': 0, 'sessions': 0})
            
            for session in sessions:
                day_key = session.started_at.date().isoformat()
                daily_data[day_key]['questions'] += session.questions_answered
                daily_data[day_key]['correct'] += session.questions_correct
                daily_data[day_key]['sessions'] += 1
                if session.ended_at:
                    daily_data[day_key]['time'] += (session.ended_at - session.started_at).total_seconds()
            
            # Convert to list of data points
            trend_points = []
            for day_key in sorted(daily_data.keys()):
                data = daily_data[day_key]
                accuracy = data['correct'] / data['questions'] if data['questions'] > 0 else 0
                
                point = {
                    'date': day_key,
                    'accuracy': round(accuracy, 2),
                    'questions': data['questions'],
                    'time_hours': round(data['time'] / 3600, 1),
                    'sessions': data['sessions']
                }
                trend_points.append(point)
            
            return trend_points
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_class_trend_data(class_id, metric='accuracy', days=30):
        """Get trend data for class"""
        try:
            # Get class students
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return []
            
            start_date = datetime.utcnow() - timedelta(days=days)
            sessions = StudentSession.query.filter(
                StudentSession.student_id.in_(student_ids),
                StudentSession.started_at >= start_date
            ).order_by(StudentSession.started_at).all()
            
            # Group by day
            daily_data = defaultdict(lambda: {'questions': 0, 'correct': 0, 'time': 0, 'sessions': 0, 'active_students': set()})
            
            for session in sessions:
                day_key = session.started_at.date().isoformat()
                daily_data[day_key]['questions'] += session.questions_answered
                daily_data[day_key]['correct'] += session.questions_correct
                daily_data[day_key]['sessions'] += 1
                daily_data[day_key]['active_students'].add(session.student_id)
                if session.ended_at:
                    daily_data[day_key]['time'] += (session.ended_at - session.started_at).total_seconds()
            
            # Convert to list of data points
            trend_points = []
            for day_key in sorted(daily_data.keys()):
                data = daily_data[day_key]
                accuracy = data['correct'] / data['questions'] if data['questions'] > 0 else 0
                
                point = {
                    'date': day_key,
                    'accuracy': round(accuracy, 2),
                    'questions': data['questions'],
                    'time_hours': round(data['time'] / 3600, 1),
                    'sessions': data['sessions'],
                    'active_students': len(data['active_students'])
                }
                trend_points.append(point)
            
            return trend_points
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_student_comparison(student_id):
        """Compare student to class average"""
        try:
            # Find student's class
            student = Student.query.get(student_id)
            if not student:
                return {}
            
            membership = ClassMembership.query.filter_by(student_id=student_id).first()
            if not membership:
                return {}
            
            class_id = membership.class_id
            
            # Get all students in class
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            # Calculate student's average
            student_paths = LearningPath.query.filter_by(student_id=student_id).all()
            student_avg = sum(p.current_accuracy for p in student_paths) / len(student_paths) if student_paths else 0
            
            # Calculate class average
            all_accuracies = []
            for sid in student_ids:
                paths = LearningPath.query.filter_by(student_id=sid).all()
                if paths:
                    avg = sum(p.current_accuracy for p in paths) / len(paths)
                    all_accuracies.append(avg)
            
            class_avg = sum(all_accuracies) / len(all_accuracies) if all_accuracies else 0
            
            # Calculate percentile
            below_student = sum(1 for a in all_accuracies if a < student_avg)
            percentile = (below_student / len(all_accuracies) * 100) if all_accuracies else 50
            
            return {
                'student_accuracy': round(student_avg, 2),
                'class_average': round(class_avg, 2),
                'percentile': round(percentile, 0),
                'rank': below_student + 1,
                'total_students': len(all_accuracies)
            }
            
        except Exception as e:
            return {}
    
    # Helper methods
    
    @staticmethod
    def _get_class_skill_heatmap(class_id):
        """Get skill performance heatmap for class"""
        try:
            # Get class students
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return []
            
            # Get all learning paths for class students
            paths = LearningPath.query.filter(LearningPath.student_id.in_(student_ids)).all()
            
            # Group by skill
            skill_data = defaultdict(lambda: {'accuracies': [], 'students': 0})
            
            for path in paths:
                if path.skill:
                    skill_data[path.skill.id]['accuracies'].append(path.current_accuracy)
                    skill_data[path.skill.id]['students'] += 1
                    if 'skill_name' not in skill_data[path.skill.id]:
                        skill_data[path.skill.id]['skill_name'] = path.skill.name
            
            # Calculate averages
            heatmap = []
            for skill_id, data in skill_data.items():
                avg_accuracy = sum(data['accuracies']) / len(data['accuracies']) if data['accuracies'] else 0
                heatmap.append({
                    'skill_id': skill_id,
                    'skill_name': data['skill_name'],
                    'avg_accuracy': round(avg_accuracy, 2),
                    'student_count': data['students']
                })
            
            # Sort by accuracy (struggling skills first)
            heatmap.sort(key=lambda x: x['avg_accuracy'])
            
            return heatmap
            
        except Exception as e:
            return []

