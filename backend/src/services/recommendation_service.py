"""
Recommendation Service for personalized learning recommendations.
"""
from src.database import db
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.assessment import Skill
from datetime import datetime, timedelta
from sqlalchemy import func


class RecommendationService:
    """Service for personalized recommendations"""
    
    @staticmethod
    def get_skill_recommendations(student_id, count=5):
        """Get recommended skills to practice next"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get student's learning paths
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            mastered_skill_ids = [p.skill_id for p in paths if p.mastery_achieved]
            in_progress_skill_ids = [p.skill_id for p in paths if not p.mastery_achieved]
            
            recommendations = []
            
            # Priority 1: Skills in progress with low accuracy (needs attention)
            for path in paths:
                if not path.mastery_achieved and path.current_accuracy < 0.70:
                    recommendations.append({
                        'skill_id': path.skill_id,
                        'skill_name': path.skill.name if path.skill else 'Unknown',
                        'reason': 'Needs attention - low accuracy',
                        'priority': 'high',
                        'current_accuracy': round(path.current_accuracy * 100, 1)
                    })
            
            # Priority 2: Skills in progress with good accuracy (close to mastery)
            for path in paths:
                if not path.mastery_achieved and 0.70 <= path.current_accuracy < 0.90:
                    recommendations.append({
                        'skill_id': path.skill_id,
                        'skill_name': path.skill.name if path.skill else 'Unknown',
                        'reason': 'Close to mastery - keep practicing',
                        'priority': 'medium',
                        'current_accuracy': round(path.current_accuracy * 100, 1)
                    })
            
            # Priority 3: New skills at appropriate level
            if len(recommendations) < count:
                # Get skills at student's grade level not yet started
                available_skills = Skill.query.filter(
                    Skill.grade_level == student.grade,
                    ~Skill.id.in_(mastered_skill_ids + in_progress_skill_ids)
                ).limit(count - len(recommendations)).all()
                
                for skill in available_skills:
                    recommendations.append({
                        'skill_id': skill.id,
                        'skill_name': skill.name,
                        'reason': 'New skill at your grade level',
                        'priority': 'low',
                        'current_accuracy': 0
                    })
            
            # Sort by priority and limit
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            recommendations.sort(key=lambda x: priority_order[x['priority']])
            recommendations = recommendations[:count]
            
            return {'success': True, 'recommendations': recommendations}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_practice_time_recommendations(student_id):
        """Get optimal practice time recommendations"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get recent sessions
            sessions = StudentSession.query.filter_by(student_id=student_id).all()
            
            if not sessions:
                return {
                    'success': True,
                    'recommendations': {
                        'best_time': 'afternoon',
                        'optimal_duration': 20,
                        'frequency': 'daily',
                        'reason': 'Default recommendations - no data yet'
                    }
                }, 200
            
            # Analyze performance by time of day
            morning_sessions = []  # 6-12
            afternoon_sessions = []  # 12-18
            evening_sessions = []  # 18-24
            
            for session in sessions:
                hour = session.started_at.hour
                accuracy = (session.questions_correct / session.questions_answered) if session.questions_answered > 0 else 0
                
                if 6 <= hour < 12:
                    morning_sessions.append(accuracy)
                elif 12 <= hour < 18:
                    afternoon_sessions.append(accuracy)
                elif 18 <= hour < 24:
                    evening_sessions.append(accuracy)
            
            # Calculate average accuracy by time
            morning_avg = sum(morning_sessions) / len(morning_sessions) if morning_sessions else 0
            afternoon_avg = sum(afternoon_sessions) / len(afternoon_sessions) if afternoon_sessions else 0
            evening_avg = sum(evening_sessions) / len(evening_sessions) if evening_sessions else 0
            
            # Determine best time
            time_scores = {
                'morning': morning_avg,
                'afternoon': afternoon_avg,
                'evening': evening_avg
            }
            best_time = max(time_scores, key=time_scores.get)
            
            # Calculate optimal duration
            durations = []
            for session in sessions:
                if session.ended_at:
                    duration = (session.ended_at - session.started_at).total_seconds() / 60
                    durations.append(duration)
            
            optimal_duration = int(sum(durations) / len(durations)) if durations else 20
            optimal_duration = max(min(optimal_duration, 45), 15)  # Clamp to 15-45 minutes
            
            # Calculate frequency
            days_with_practice = len(set(s.started_at.date() for s in sessions))
            total_days = (datetime.utcnow() - min(s.started_at for s in sessions)).days or 1
            practice_rate = days_with_practice / total_days
            
            if practice_rate > 0.8:
                frequency = 'daily'
            elif practice_rate > 0.5:
                frequency = '4-5 times per week'
            else:
                frequency = '3 times per week'
            
            recommendations = {
                'best_time': best_time,
                'best_time_accuracy': round(time_scores[best_time] * 100, 1),
                'optimal_duration': optimal_duration,
                'frequency': frequency,
                'current_practice_rate': round(practice_rate * 100, 1),
                'reason': f'You perform best in the {best_time}'
            }
            
            return {'success': True, 'recommendations': recommendations}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_study_strategies(student_id):
        """Get personalized study strategy recommendations"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get recent sessions
            sessions = StudentSession.query.filter_by(student_id=student_id).limit(20).all()
            
            strategies = []
            
            if not sessions:
                strategies.append({
                    'strategy': 'Start with short sessions',
                    'reason': 'Build a consistent practice habit',
                    'priority': 'high'
                })
                return {'success': True, 'strategies': strategies}, 200
            
            # Analyze session patterns
            
            # Check session length
            durations = []
            for session in sessions:
                if session.ended_at:
                    duration = (session.ended_at - session.started_at).total_seconds() / 60
                    durations.append(duration)
            
            if durations:
                avg_duration = sum(durations) / len(durations)
                
                if avg_duration > 40:
                    strategies.append({
                        'strategy': 'Try shorter, more frequent sessions',
                        'reason': 'Long sessions can reduce focus',
                        'priority': 'medium'
                    })
                elif avg_duration < 10:
                    strategies.append({
                        'strategy': 'Extend your practice sessions',
                        'reason': 'Longer sessions allow deeper learning',
                        'priority': 'medium'
                    })
            
            # Check accuracy
            total_q = sum(s.questions_answered or 0 for s in sessions)
            total_c = sum(s.questions_correct or 0 for s in sessions)
            accuracy = (total_c / total_q) if total_q > 0 else 0
            
            if accuracy < 0.60:
                strategies.append({
                    'strategy': 'Review fundamentals before advancing',
                    'reason': 'Low accuracy suggests gaps in understanding',
                    'priority': 'high'
                })
            elif accuracy > 0.90:
                strategies.append({
                    'strategy': 'Challenge yourself with harder skills',
                    'reason': 'High accuracy shows readiness for advancement',
                    'priority': 'medium'
                })
            
            # Check consistency
            days_with_practice = len(set(s.started_at.date() for s in sessions))
            if days_with_practice < 5:
                strategies.append({
                    'strategy': 'Practice more consistently',
                    'reason': 'Regular practice improves retention',
                    'priority': 'high'
                })
            
            # Check question count
            avg_questions = total_q / len(sessions) if sessions else 0
            if avg_questions < 10:
                strategies.append({
                    'strategy': 'Answer more questions per session',
                    'reason': 'More practice leads to better mastery',
                    'priority': 'low'
                })
            
            # If no specific strategies, add general ones
            if not strategies:
                strategies.append({
                    'strategy': 'Keep up the great work!',
                    'reason': 'Your practice patterns are effective',
                    'priority': 'low'
                })
            
            # Sort by priority
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            strategies.sort(key=lambda x: priority_order[x['priority']])
            
            return {'success': True, 'strategies': strategies}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def analyze_skill_gaps(student_id):
        """Identify missing prerequisite skills"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get student's mastered skills
            paths = LearningPath.query.filter_by(
                student_id=student_id,
                mastery_achieved=True
            ).all()
            
            mastered_skill_ids = [p.skill_id for p in paths]
            
            # Get all skills at or below student's grade
            all_skills = Skill.query.filter(
                Skill.grade_level <= student.grade
            ).all()
            
            # Identify gaps (skills not mastered at lower grades)
            gaps = []
            for skill in all_skills:
                if skill.id not in mastered_skill_ids and skill.grade_level < student.grade:
                    gaps.append({
                        'skill_id': skill.id,
                        'skill_name': skill.name,
                        'grade_level': skill.grade_level,
                        'subject_area': skill.subject_area,
                        'gap_type': 'prerequisite',
                        'priority': 'high' if skill.grade_level < student.grade - 1 else 'medium'
                    })
            
            # Sort by grade level (lowest first) and priority
            gaps.sort(key=lambda x: (x['grade_level'], x['priority']))
            
            return {'success': True, 'gaps': gaps, 'gap_count': len(gaps)}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

