"""
Predictive Analytics Service for forecasting student outcomes.
"""
from src.database import db
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.class_group import ClassMembership
from src.services.analytics_dashboard_service import AnalyticsDashboardService
from datetime import datetime, timedelta
from sqlalchemy import func


class PredictiveAnalyticsService:
    """Service for predictive analytics and forecasting"""
    
    @staticmethod
    def predict_skill_mastery(student_id, skill_id):
        """Predict if/when student will master a skill"""
        try:
            # Get learning path
            path = LearningPath.query.filter_by(
                student_id=student_id,
                skill_id=skill_id
            ).first()
            
            if not path:
                return {'success': False, 'error': 'Learning path not found'}, 404
            
            # If already mastered
            if path.mastery_achieved:
                return {
                    'success': True,
                    'prediction': {
                        'will_master': True,
                        'probability': 100.0,
                        'days_to_mastery': 0,
                        'already_mastered': True
                    }
                }, 200
            
            # Get recent sessions for this skill (last 30 days)
            start_date = datetime.utcnow() - timedelta(days=30)
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_date
            ).all()
            
            if not sessions:
                return {
                    'success': True,
                    'prediction': {
                        'will_master': False,
                        'probability': 0.0,
                        'days_to_mastery': None,
                        'reason': 'No recent practice'
                    }
                }, 200
            
            # Calculate trend
            current_accuracy = path.current_accuracy
            practice_frequency = len(sessions) / 30  # sessions per day
            
            # Simple prediction model
            # Probability based on current accuracy and practice frequency
            accuracy_factor = current_accuracy * 100  # 0-100
            frequency_factor = min(practice_frequency * 50, 50)  # 0-50
            probability = min(accuracy_factor + frequency_factor, 100)
            
            # Estimate days to mastery (90% accuracy threshold)
            if current_accuracy >= 0.90:
                days_to_mastery = 0
                will_master = True
            elif current_accuracy >= 0.70 and practice_frequency > 0.2:
                # Estimate based on improvement rate
                improvement_needed = 0.90 - current_accuracy
                # Assume 1% improvement per 3 days of practice
                days_to_mastery = int(improvement_needed * 100 * 3 / practice_frequency)
                will_master = True
            else:
                days_to_mastery = None
                will_master = probability > 50
            
            prediction = {
                'will_master': will_master,
                'probability': round(probability, 1),
                'days_to_mastery': days_to_mastery,
                'current_accuracy': round(current_accuracy * 100, 1),
                'practice_frequency': round(practice_frequency, 2),
                'recommendation': 'Keep practicing!' if will_master else 'Increase practice frequency'
            }
            
            return {'success': True, 'prediction': prediction}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def predict_assignment_completion(student_id, assignment_id):
        """Predict if student will complete assignment on time"""
        try:
            # Get assignment
            assignment = Assignment.query.get(assignment_id)
            if not assignment:
                return {'success': False, 'error': 'Assignment not found'}, 404
            
            # Get student assignment
            student_assignment = AssignmentStudent.query.filter_by(
                assignment_id=assignment_id,
                student_id=student_id
            ).first()
            
            if not student_assignment:
                return {'success': False, 'error': 'Student not assigned'}, 404
            
            # If already completed
            if student_assignment.status == 'completed':
                return {
                    'success': True,
                    'prediction': {
                        'will_complete': True,
                        'probability': 100.0,
                        'on_time': student_assignment.completed_at <= assignment.due_date if assignment.due_date else True,
                        'already_completed': True
                    }
                }, 200
            
            # Calculate completion probability
            # Factors: historical completion rate, time remaining, difficulty
            
            # Historical completion rate
            past_assignments = AssignmentStudent.query.filter_by(
                student_id=student_id,
                status='completed'
            ).count()
            
            total_assignments = AssignmentStudent.query.filter_by(
                student_id=student_id
            ).count()
            
            completion_rate = (past_assignments / total_assignments) if total_assignments > 0 else 0.5
            
            # Time remaining factor
            if assignment.due_date:
                time_remaining = (assignment.due_date - datetime.utcnow()).total_seconds() / 86400  # days
                time_factor = min(time_remaining / 7, 1.0)  # Normalize to 0-1 (7 days = 1.0)
            else:
                time_factor = 1.0  # No deadline
            
            # Difficulty factor (based on question count)
            difficulty_factor = max(1.0 - (assignment.question_count / 50), 0.5)  # Harder = lower probability
            
            # Combined probability
            probability = (completion_rate * 0.5 + time_factor * 0.3 + difficulty_factor * 0.2) * 100
            
            # Recommendation
            if probability < 50:
                recommendation = 'Start immediately - assignment at risk'
            elif probability < 75:
                recommendation = 'Begin soon to ensure completion'
            else:
                recommendation = 'On track for completion'
            
            prediction = {
                'will_complete': probability > 50,
                'probability': round(probability, 1),
                'days_remaining': round(time_remaining, 1) if assignment.due_date else None,
                'historical_completion_rate': round(completion_rate * 100, 1),
                'recommendation': recommendation
            }
            
            return {'success': True, 'prediction': prediction}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def detect_at_risk_students(class_id):
        """Identify students at risk of falling behind"""
        try:
            # Get class memberships
            memberships = ClassMembership.query.filter_by(class_id=class_id).all()
            student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return {'success': True, 'at_risk_students': []}, 200
            
            at_risk = []
            
            for student_id in student_ids:
                # Calculate risk factors
                risk_score = 0
                risk_factors = []
                
                # Factor 1: Low engagement (30 points)
                engagement = AnalyticsDashboardService.calculate_engagement_score(student_id, 30)
                if engagement < 30:
                    risk_score += 30
                    risk_factors.append('Very low engagement')
                elif engagement < 50:
                    risk_score += 15
                    risk_factors.append('Low engagement')
                
                # Factor 2: Low accuracy (30 points)
                sessions = StudentSession.query.filter_by(student_id=student_id).limit(20).all()
                if sessions:
                    total_q = sum(s.questions_answered or 0 for s in sessions)
                    total_c = sum(s.questions_correct or 0 for s in sessions)
                    accuracy = (total_c / total_q) if total_q > 0 else 0
                    
                    if accuracy < 0.50:
                        risk_score += 30
                        risk_factors.append('Very low accuracy')
                    elif accuracy < 0.70:
                        risk_score += 15
                        risk_factors.append('Low accuracy')
                
                # Factor 3: No recent practice (25 points)
                recent_sessions = StudentSession.query.filter(
                    StudentSession.student_id == student_id,
                    StudentSession.started_at >= datetime.utcnow() - timedelta(days=7)
                ).count()
                
                if recent_sessions == 0:
                    risk_score += 25
                    risk_factors.append('No practice in 7 days')
                elif recent_sessions < 2:
                    risk_score += 10
                    risk_factors.append('Infrequent practice')
                
                # Factor 4: Overdue assignments (15 points)
                overdue = AssignmentStudent.query.join(Assignment).filter(
                    AssignmentStudent.student_id == student_id,
                    AssignmentStudent.status != 'completed',
                    Assignment.due_date < datetime.utcnow()
                ).count()
                
                if overdue > 2:
                    risk_score += 15
                    risk_factors.append(f'{overdue} overdue assignments')
                elif overdue > 0:
                    risk_score += 7
                    risk_factors.append(f'{overdue} overdue assignment(s)')
                
                # Categorize risk level
                if risk_score >= 60:
                    risk_level = 'high'
                elif risk_score >= 30:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                # Only include medium and high risk students
                if risk_level in ['medium', 'high']:
                    student = Student.query.get(student_id)
                    at_risk.append({
                        'student_id': student_id,
                        'student_name': student.name if student else 'Unknown',
                        'risk_level': risk_level,
                        'risk_score': risk_score,
                        'risk_factors': risk_factors,
                        'engagement_score': round(engagement, 1)
                    })
            
            # Sort by risk score (highest first)
            at_risk.sort(key=lambda x: x['risk_score'], reverse=True)
            
            return {'success': True, 'at_risk_students': at_risk}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def forecast_performance(student_id, days=7):
        """Forecast student performance for next N days"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get recent sessions (last 30 days)
            start_date = datetime.utcnow() - timedelta(days=30)
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_date
            ).order_by(StudentSession.started_at).all()
            
            if len(sessions) < 3:
                return {
                    'success': True,
                    'forecast': {
                        'insufficient_data': True,
                        'message': 'Need at least 3 recent sessions for forecast'
                    }
                }, 200
            
            # Calculate weekly averages
            weekly_accuracy = []
            for week in range(4):  # Last 4 weeks
                week_start = datetime.utcnow() - timedelta(days=(week+1)*7)
                week_end = datetime.utcnow() - timedelta(days=week*7)
                
                week_sessions = [s for s in sessions if week_start <= s.started_at < week_end]
                
                if week_sessions:
                    total_q = sum(s.questions_answered or 0 for s in week_sessions)
                    total_c = sum(s.questions_correct or 0 for s in week_sessions)
                    accuracy = (total_c / total_q) if total_q > 0 else 0
                    weekly_accuracy.append(accuracy)
            
            if not weekly_accuracy:
                return {
                    'success': True,
                    'forecast': {
                        'insufficient_data': True,
                        'message': 'No weekly data available'
                    }
                }, 200
            
            # Calculate trend (simple moving average)
            current_avg = sum(weekly_accuracy) / len(weekly_accuracy)
            
            # Determine trend direction
            if len(weekly_accuracy) >= 2:
                recent_avg = sum(weekly_accuracy[:2]) / 2
                older_avg = sum(weekly_accuracy[2:]) / len(weekly_accuracy[2:]) if len(weekly_accuracy) > 2 else recent_avg
                trend = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
            else:
                trend = 'stable'
            
            # Forecast (simple projection)
            if trend == 'improving':
                forecast_accuracy = min(current_avg + 0.05, 1.0)  # +5% improvement
            elif trend == 'declining':
                forecast_accuracy = max(current_avg - 0.05, 0.0)  # -5% decline
            else:
                forecast_accuracy = current_avg
            
            forecast = {
                'forecast_days': days,
                'current_accuracy': round(current_avg * 100, 1),
                'forecast_accuracy': round(forecast_accuracy * 100, 1),
                'trend': trend,
                'confidence': 'medium' if len(weekly_accuracy) >= 3 else 'low',
                'recommendation': 'Continue current practice' if trend == 'improving' else 'Increase practice frequency' if trend == 'declining' else 'Maintain consistency'
            }
            
            return {'success': True, 'forecast': forecast}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

