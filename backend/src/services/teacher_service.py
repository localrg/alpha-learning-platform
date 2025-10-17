"""
Teacher Service
Business logic for teacher dashboard and class management
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from src.database import db
from src.models.teacher import Teacher
from src.models.user import User
from src.models.student import Student
from src.models.class_group import ClassGroup, ClassMembership
from src.models.learning_path import LearningPath
from src.models.gamification import StudentProgress


class TeacherService:
    """Service for teacher dashboard and management"""
    
    @staticmethod
    def get_dashboard_data(user_id):
        """Get comprehensive dashboard data for teacher"""
        try:
            # Get teacher profile
            teacher = Teacher.query.filter_by(user_id=user_id).first()
            if not teacher:
                # Create teacher profile if doesn't exist
                user = User.query.get(user_id)
                if not user or user.role != 'teacher':
                    return {'error': 'Not a teacher account'}, 403
                
                teacher = Teacher(
                    user_id=user_id,
                    name=user.username,
                    email=user.email or f'{user.username}@school.edu'
                )
                db.session.add(teacher)
                db.session.commit()
            
            # Get all classes for this teacher
            classes = ClassGroup.query.filter_by(teacher_id=user_id).all()
            
            # Calculate stats
            stats = TeacherService.get_teacher_stats(user_id)
            
            # Get alerts
            alerts = TeacherService.get_alerts(user_id)
            
            # Format classes
            class_list = []
            for class_group in classes:
                class_metrics = TeacherService.get_class_metrics(class_group.id)
                class_list.append({
                    'id': class_group.id,
                    'name': class_group.name,
                    'student_count': class_metrics['student_count'],
                    'avg_accuracy': class_metrics['avg_accuracy'],
                    'active_students': class_metrics['active_students'],
                    'struggling_students': len(class_metrics['struggling_students']),
                    'recent_activity': class_metrics['recent_activity']
                })
            
            return {
                'success': True,
                'teacher': teacher.to_dict(),
                'stats': stats,
                'classes': class_list,
                'alerts': alerts
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_class_overview(class_id, user_id):
        """Get detailed overview of a specific class"""
        try:
            # Verify teacher owns class
            class_group = ClassGroup.query.get(class_id)
            if not class_group:
                return {'error': 'Class not found'}, 404
            
            if class_group.teacher_id != user_id:
                return {'error': 'Not authorized'}, 403
            
            # Get class metrics
            metrics = TeacherService.get_class_metrics(class_id)
            
            # Get students with performance data
            students = []
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            
            for membership in memberships:
                student = Student.query.get(membership.student_id)
                if student:
                    student_data = TeacherService._get_student_performance(student.id)
                    students.append(student_data)
            
            # Sort students by performance
            students.sort(key=lambda x: x.get('avg_accuracy', 0), reverse=True)
            
            # Get skill performance
            skill_performance = TeacherService._get_class_skill_performance(class_id)
            
            return {
                'success': True,
                'class': class_group.to_dict(),
                'metrics': {
                    'avg_accuracy': metrics['avg_accuracy'],
                    'avg_questions_per_student': metrics['avg_questions'],
                    'mastery_rate': metrics['mastery_rate'],
                    'engagement_rate': metrics['engagement_rate']
                },
                'students': students,
                'skill_performance': skill_performance
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_student_summary(student_id, user_id):
        """Get detailed summary of a specific student"""
        try:
            # Verify teacher has access to student (via class membership)
            student = Student.query.get(student_id)
            if not student:
                return {'error': 'Student not found'}, 404
            
            # Check if student is in any of teacher's classes
            teacher_classes = ClassGroup.query.filter_by(teacher_id=user_id).all()
            teacher_class_ids = [c.id for c in teacher_classes]
            
            student_memberships = ClassMembership.query.filter_by(student_id=student_id).all()
            student_class_ids = [m.class_id for m in student_memberships]
            
            if not any(cid in teacher_class_ids for cid in student_class_ids):
                return {'error': 'Not authorized to view this student'}, 403
            
            # Get student performance data
            performance = TeacherService._get_student_performance(student_id)
            
            # Get recent activity
            recent_activity = TeacherService._get_student_recent_activity(student_id, days=7)
            
            # Get struggling skills
            struggling_skills = TeacherService._get_student_struggling_skills(student_id)
            
            # Get mastered skills
            mastered_skills = TeacherService._get_student_mastered_skills(student_id)
            
            return {
                'success': True,
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'grade': student.grade,
                    'avatar': student.avatar
                },
                'performance': {
                    'avg_accuracy': performance.get('avg_accuracy', 0),
                    'questions_answered': performance.get('questions_answered', 0),
                    'skills_mastered': len(mastered_skills),
                    'current_streak': performance.get('current_streak', 0),
                    'level': performance.get('level', 1),
                    'total_xp': performance.get('total_xp', 0)
                },
                'recent_activity': recent_activity,
                'struggling_skills': struggling_skills,
                'mastered_skills': mastered_skills
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_class_metrics(class_id):
        """Calculate metrics for a class"""
        try:
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return {
                    'student_count': 0,
                    'avg_accuracy': 0,
                    'avg_questions': 0,
                    'active_students': 0,
                    'struggling_students': [],
                    'recent_activity': 0,
                    'mastery_rate': 0,
                    'engagement_rate': 0
                }
            
            # Get learning paths for all students
            paths = LearningPath.query.filter(LearningPath.student_id.in_(student_ids)).all()
            
            # Calculate averages
            total_accuracy = 0
            total_questions = 0
            mastered_count = 0
            active_count = 0
            struggling_students = []
            
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            for student_id in student_ids:
                student_paths = [p for p in paths if p.student_id == student_id]
                
                if student_paths:
                    student_accuracy = sum(p.current_accuracy for p in student_paths) / len(student_paths)
                    student_questions = sum(p.questions_answered for p in student_paths)
                    
                    total_accuracy += student_accuracy
                    total_questions += student_questions
                    
                    # Check if mastered (accuracy > 0.9)
                    if student_accuracy > 0.9:
                        mastered_count += 1
                    
                    # Check if struggling (accuracy < 0.7)
                    if student_accuracy < 0.7:
                        student = Student.query.get(student_id)
                        struggling_students.append({
                            'id': student_id,
                            'name': student.name if student else 'Unknown',
                            'accuracy': student_accuracy
                        })
                    
                    # Check if active (practiced in last 7 days)
                    recent_paths = [p for p in student_paths if p.updated_at and p.updated_at > seven_days_ago]
                    if recent_paths:
                        active_count += 1
            
            student_count = len(student_ids)
            avg_accuracy = total_accuracy / student_count if student_count > 0 else 0
            avg_questions = total_questions / student_count if student_count > 0 else 0
            mastery_rate = mastered_count / student_count if student_count > 0 else 0
            engagement_rate = active_count / student_count if student_count > 0 else 0
            
            # Count recent activity (questions in last 7 days)
            recent_activity = sum(1 for p in paths if p.updated_at and p.updated_at > seven_days_ago)
            
            return {
                'student_count': student_count,
                'avg_accuracy': round(avg_accuracy, 2),
                'avg_questions': round(avg_questions, 0),
                'active_students': active_count,
                'struggling_students': struggling_students,
                'recent_activity': recent_activity,
                'mastery_rate': round(mastery_rate, 2),
                'engagement_rate': round(engagement_rate, 2)
            }
            
        except Exception as e:
            print(f"Error calculating class metrics: {e}")
            return {
                'student_count': 0,
                'avg_accuracy': 0,
                'avg_questions': 0,
                'active_students': 0,
                'struggling_students': [],
                'recent_activity': 0,
                'mastery_rate': 0,
                'engagement_rate': 0
            }
    
    @staticmethod
    def get_struggling_students(class_id, threshold=0.7):
        """Get list of struggling students in class"""
        metrics = TeacherService.get_class_metrics(class_id)
        return metrics['struggling_students']
    
    @staticmethod
    def get_top_performers(class_id, limit=5):
        """Get top performing students in class"""
        try:
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            students_performance = []
            for student_id in student_ids:
                perf = TeacherService._get_student_performance(student_id)
                students_performance.append(perf)
            
            # Sort by accuracy
            students_performance.sort(key=lambda x: x.get('avg_accuracy', 0), reverse=True)
            
            return students_performance[:limit]
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_teacher_stats(user_id):
        """Get overall statistics for teacher"""
        try:
            classes = ClassGroup.query.filter_by(teacher_id=user_id).all()
            
            total_students = 0
            total_questions = 0
            total_accuracy = 0
            class_count = 0
            
            for class_group in classes:
                metrics = TeacherService.get_class_metrics(class_group.id)
                total_students += metrics['student_count']
                total_questions += metrics['avg_questions'] * metrics['student_count']
                total_accuracy += metrics['avg_accuracy']
                class_count += 1
            
            avg_class_performance = total_accuracy / class_count if class_count > 0 else 0
            
            return {
                'total_students': total_students,
                'total_classes': class_count,
                'avg_class_performance': round(avg_class_performance, 2),
                'total_questions_answered': int(total_questions)
            }
            
        except Exception as e:
            return {
                'total_students': 0,
                'total_classes': 0,
                'avg_class_performance': 0,
                'total_questions_answered': 0
            }
    
    @staticmethod
    def get_alerts(user_id):
        """Get alerts and notifications for teacher"""
        try:
            alerts = []
            classes = ClassGroup.query.filter_by(teacher_id=user_id).all()
            
            for class_group in classes:
                metrics = TeacherService.get_class_metrics(class_group.id)
                
                # Alert for struggling students
                if metrics['struggling_students']:
                    count = len(metrics['struggling_students'])
                    alerts.append({
                        'type': 'struggling_students',
                        'class_name': class_group.name,
                        'class_id': class_group.id,
                        'message': f'{count} student{"s" if count > 1 else ""} need{"" if count > 1 else "s"} attention',
                        'severity': 'medium',
                        'count': count
                    })
                
                # Alert for low engagement
                if metrics['engagement_rate'] < 0.5:
                    alerts.append({
                        'type': 'low_engagement',
                        'class_name': class_group.name,
                        'class_id': class_group.id,
                        'message': f'Low engagement: {int(metrics["engagement_rate"] * 100)}% active',
                        'severity': 'high'
                    })
            
            return alerts
            
        except Exception as e:
            return []
    
    # Helper methods
    
    @staticmethod
    def _get_student_performance(student_id):
        """Get performance data for a student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {}
            
            # Get learning paths
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            
            if not paths:
                return {
                    'id': student_id,
                    'name': student.name,
                    'avatar': student.avatar,
                    'avg_accuracy': 0,
                    'questions_answered': 0,
                    'level': 1,
                    'total_xp': 0,
                    'current_streak': 0,
                    'last_active': None,
                    'status': 'inactive'
                }
            
            # Calculate metrics
            total_accuracy = sum(p.current_accuracy for p in paths)
            avg_accuracy = total_accuracy / len(paths)
            total_questions = sum(p.questions_answered for p in paths)
            
            # Get progress data
            progress = StudentProgress.query.filter_by(student_id=student_id).first()
            level = progress.current_level if progress else 1
            total_xp = progress.total_xp if progress else 0
            
            # Get streak data
            from src.models.streak import StreakTracking
            streak = StreakTracking.query.filter_by(student_id=student_id).first()
            current_streak = streak.practice_streak if streak else 0
            
            # Determine last active
            last_updated = max((p.updated_at for p in paths if p.updated_at), default=None)
            if last_updated:
                time_diff = datetime.utcnow() - last_updated
                if time_diff.days == 0:
                    last_active = f'{time_diff.seconds // 3600} hours ago'
                else:
                    last_active = f'{time_diff.days} days ago'
            else:
                last_active = 'Never'
            
            # Determine status
            if avg_accuracy >= 0.8:
                status = 'on_track'
            elif avg_accuracy >= 0.7:
                status = 'needs_practice'
            else:
                status = 'needs_help'
            
            return {
                'id': student_id,
                'name': student.name,
                'avatar': student.avatar,
                'avg_accuracy': round(avg_accuracy, 2),
                'questions_answered': total_questions,
                'level': level,
                'total_xp': total_xp,
                'current_streak': current_streak,
                'last_active': last_active,
                'status': status
            }
            
        except Exception as e:
            print(f"Error getting student performance: {e}")
            return {}
    
    @staticmethod
    def _get_student_recent_activity(student_id, days=7):
        """Get recent activity for student"""
        try:
            # For now, return empty list
            # In future, this would query a session/activity log table
            return []
        except Exception as e:
            return []
    
    @staticmethod
    def _get_student_struggling_skills(student_id, threshold=0.7):
        """Get skills student is struggling with"""
        try:
            paths = LearningPath.query.filter_by(student_id=student_id).filter(
                LearningPath.current_accuracy < threshold
            ).all()
            
            struggling = []
            for path in paths:
                skill = path.skill
                struggling.append({
                    'skill_name': skill.name if skill else 'Unknown',
                    'accuracy': round(path.current_accuracy, 2),
                    'attempts': path.questions_answered
                })
            
            return struggling
            
        except Exception as e:
            return []
    
    @staticmethod
    def _get_student_mastered_skills(student_id, threshold=0.9):
        """Get skills student has mastered"""
        try:
            paths = LearningPath.query.filter_by(student_id=student_id).filter(
                LearningPath.current_accuracy >= threshold
            ).all()
            
            mastered = []
            for path in paths:
                skill = path.skill
                mastered.append({
                    'skill_name': skill.name if skill else 'Unknown',
                    'accuracy': round(path.current_accuracy, 2)
                })
            
            return mastered
            
        except Exception as e:
            return []
    
    @staticmethod
    def _get_class_skill_performance(class_id):
        """Get skill performance across class"""
        try:
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return []
            
            # Get all learning paths for class students
            paths = LearningPath.query.filter(LearningPath.student_id.in_(student_ids)).all()
            
            # Group by skill
            skill_data = {}
            for path in paths:
                skill = path.skill
                skill_name = skill.name if skill else 'Unknown'
                if skill_name not in skill_data:
                    skill_data[skill_name] = {
                        'accuracies': [],
                        'mastered': 0
                    }
                
                skill_data[skill_name]['accuracies'].append(path.current_accuracy)
                if path.current_accuracy >= 0.9:
                    skill_data[skill_name]['mastered'] += 1
            
            # Calculate averages
            skill_performance = []
            for skill_name, data in skill_data.items():
                avg_accuracy = sum(data['accuracies']) / len(data['accuracies'])
                struggling = sum(1 for acc in data['accuracies'] if acc < 0.7)
                
                skill_performance.append({
                    'skill_name': skill_name,
                    'avg_accuracy': round(avg_accuracy, 2),
                    'students_mastered': data['mastered'],
                    'students_struggling': struggling
                })
            
            # Sort by accuracy
            skill_performance.sort(key=lambda x: x['avg_accuracy'], reverse=True)
            
            return skill_performance
            
        except Exception as e:
            print(f"Error getting class skill performance: {e}")
            return []

