"""
Report generation service for parent activity reports.
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from src.database import db
from src.models.parent import ParentChildLink
from src.models.student import Student
from src.models.student_session import StudentSession
from src.models.learning_path import LearningPath
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.achievement import Achievement, StudentAchievement
from src.models.streak import StreakTracking


class ReportService:
    """Service for generating parent activity reports"""
    
    @staticmethod
    def verify_parent_child_link(parent_id, student_id):
        """Verify parent has access to this child"""
        link = ParentChildLink.query.filter_by(
            parent_id=parent_id,
            student_id=student_id,
            status='active'
        ).first()
        return link is not None
    
    @staticmethod
    def _get_date_range(period, offset=0):
        """Get start and end dates for a period"""
        today = datetime.utcnow().date()
        
        if period == 'week':
            # Get Monday of the target week
            days_since_monday = today.weekday()
            current_monday = today - timedelta(days=days_since_monday)
            target_monday = current_monday - timedelta(weeks=offset)
            start_date = target_monday
            end_date = target_monday + timedelta(days=6)
            
        elif period == 'month':
            # Get first day of target month
            if offset == 0:
                start_date = today.replace(day=1)
            else:
                # Go back offset months
                month = today.month - offset
                year = today.year
                while month <= 0:
                    month += 12
                    year -= 1
                start_date = today.replace(year=year, month=month, day=1)
            
            # Get last day of month
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
        
        else:  # custom days
            start_date = today - timedelta(days=period - 1)
            end_date = today
        
        return start_date, end_date
    
    @staticmethod
    def _calculate_trends(current, previous):
        """Calculate trend indicators"""
        if previous == 0:
            if current > 0:
                return 'improving', 100.0
            return 'stable', 0.0
        
        change_percent = ((current - previous) / previous) * 100
        
        if change_percent > 5:
            trend = 'improving'
        elif change_percent < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return trend, round(change_percent, 1)
    
    @staticmethod
    def generate_weekly_report(parent_id, student_id, week_offset=0):
        """Generate weekly progress report"""
        try:
            # Verify authorization
            if not ReportService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get date range for this week
            start_date, end_date = ReportService._get_date_range('week', week_offset)
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get all sessions in this week
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_datetime,
                StudentSession.started_at <= end_datetime
            ).all()
            
            # Calculate summary metrics
            total_time = sum(
                (session.ended_at - session.started_at).total_seconds() / 60
                if session.ended_at else 0
                for session in sessions
            )
            total_questions = sum(session.questions_answered or 0 for session in sessions)
            total_correct = sum(session.questions_correct or 0 for session in sessions)
            accuracy = (total_correct / total_questions) if total_questions > 0 else 0
            
            # Get skills practiced
            skill_ids = set()
            for session in sessions:
                if session.skill_id:
                    skill_ids.add(session.skill_id)
            
            skills_practiced = []
            for skill_id in skill_ids:
                skill_sessions = [s for s in sessions if s.skill_id == skill_id]
                skill_time = sum(
                    (s.ended_at - s.started_at).total_seconds() / 60
                    if s.ended_at else 0
                    for s in skill_sessions
                )
                skill_questions = sum(s.questions_answered or 0 for s in skill_sessions)
                skill_correct = sum(s.questions_correct or 0 for s in skill_sessions)
                skill_accuracy = (skill_correct / skill_questions) if skill_questions > 0 else 0
                
                path = LearningPath.query.filter_by(
                    student_id=student_id,
                    skill_id=skill_id
                ).first()
                
                if path and path.skill:
                    skills_practiced.append({
                        'skill_name': path.skill.name,
                        'time_minutes': round(skill_time, 1),
                        'questions': skill_questions,
                        'accuracy': round(skill_accuracy, 2)
                    })
            
            # Get assignments completed this week
            assignments_completed = AssignmentStudent.query.filter(
                AssignmentStudent.student_id == student_id,
                AssignmentStudent.status == 'completed',
                AssignmentStudent.completed_at >= start_datetime,
                AssignmentStudent.completed_at <= end_datetime
            ).count()
            
            # Get achievements earned this week
            achievements_earned = StudentAchievement.query.filter(
                StudentAchievement.student_id == student_id,
                StudentAchievement.unlocked_at >= start_datetime,
                StudentAchievement.unlocked_at <= end_datetime
            ).count()
            
            # Check streak
            streak = StreakTracking.query.filter_by(student_id=student_id).first()
            streak_maintained = streak.practice_streak >= 7 if streak else False
            
            # Daily breakdown
            daily_breakdown = []
            current_date = start_date
            while current_date <= end_date:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                
                day_sessions = [s for s in sessions if day_start <= s.started_at <= day_end]
                day_time = sum(
                    (s.ended_at - s.started_at).total_seconds() / 60
                    if s.ended_at else 0
                    for s in day_sessions
                )
                day_questions = sum(s.questions_answered or 0 for s in day_sessions)
                day_correct = sum(s.questions_correct or 0 for s in day_sessions)
                day_accuracy = (day_correct / day_questions) if day_questions > 0 else 0
                
                daily_breakdown.append({
                    'date': current_date.isoformat(),
                    'day_name': current_date.strftime('%A'),
                    'time_minutes': round(day_time, 1),
                    'sessions': len(day_sessions),
                    'questions': day_questions,
                    'accuracy': round(day_accuracy, 2)
                })
                
                current_date += timedelta(days=1)
            
            # Generate insights
            insights = {}
            
            # Most active day
            if daily_breakdown:
                most_active = max(daily_breakdown, key=lambda x: x['time_minutes'])
                insights['most_active_day'] = most_active['day_name']
                
                # Best performance day
                days_with_activity = [d for d in daily_breakdown if d['questions'] > 0]
                if days_with_activity:
                    best_performance = max(days_with_activity, key=lambda x: x['accuracy'])
                    insights['best_performance_day'] = best_performance['day_name']
            
            # Improvement areas (skills with accuracy < 70%)
            improvement_areas = [s['skill_name'] for s in skills_practiced if s['accuracy'] < 0.70]
            insights['improvement_areas'] = improvement_areas
            
            # Comparison to last week
            prev_start, prev_end = ReportService._get_date_range('week', week_offset + 1)
            prev_start_dt = datetime.combine(prev_start, datetime.min.time())
            prev_end_dt = datetime.combine(prev_end, datetime.max.time())
            
            prev_sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= prev_start_dt,
                StudentSession.started_at <= prev_end_dt
            ).all()
            
            prev_time = sum(
                (s.ended_at - s.started_at).total_seconds() / 60
                if s.ended_at else 0
                for s in prev_sessions
            )
            prev_questions = sum(s.questions_answered or 0 for s in prev_sessions)
            prev_correct = sum(s.questions_correct or 0 for s in prev_sessions)
            prev_accuracy = (prev_correct / prev_questions) if prev_questions > 0 else 0
            
            time_trend, time_change = ReportService._calculate_trends(total_time, prev_time)
            accuracy_change = round(accuracy - prev_accuracy, 2)
            
            insights['comparison_to_last_week'] = {
                'time_change_percent': time_change,
                'accuracy_change': accuracy_change,
                'trend': time_trend
            }
            
            # Build report
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'week_number': start_date.isocalendar()[1]
                },
                'summary': {
                    'total_time_minutes': round(total_time, 1),
                    'total_sessions': len(sessions),
                    'questions_answered': total_questions,
                    'questions_correct': total_correct,
                    'accuracy': round(accuracy, 2),
                    'skills_practiced': len(skills_practiced),
                    'assignments_completed': assignments_completed,
                    'achievements_earned': achievements_earned,
                    'streak_maintained': streak_maintained
                },
                'daily_breakdown': daily_breakdown,
                'skills_practiced': skills_practiced,
                'insights': insights
            }
            
            return {'success': True, 'report': report}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def generate_monthly_report(parent_id, student_id, month_offset=0):
        """Generate monthly progress report"""
        try:
            # Verify authorization
            if not ReportService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get date range for this month
            start_date, end_date = ReportService._get_date_range('month', month_offset)
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get all sessions in this month
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_datetime,
                StudentSession.started_at <= end_datetime
            ).all()
            
            # Calculate summary metrics
            total_time = sum(
                (session.ended_at - session.started_at).total_seconds() / 60
                if session.ended_at else 0
                for session in sessions
            )
            total_questions = sum(session.questions_answered or 0 for session in sessions)
            total_correct = sum(session.questions_correct or 0 for session in sessions)
            accuracy = (total_correct / total_questions) if total_questions > 0 else 0
            
            # Skills mastered this month
            skills_mastered = LearningPath.query.filter(
                LearningPath.student_id == student_id,
                LearningPath.mastery_achieved == True,
                LearningPath.mastery_date >= start_datetime,
                LearningPath.mastery_date <= end_datetime
            ).count()
            
            # Assignment completion rate
            total_assignments = AssignmentStudent.query.filter(
                AssignmentStudent.student_id == student_id,
                AssignmentStudent.created_at <= end_datetime
            ).count()
            
            completed_assignments = AssignmentStudent.query.filter(
                AssignmentStudent.student_id == student_id,
                AssignmentStudent.status == 'completed',
                AssignmentStudent.completed_at >= start_datetime,
                AssignmentStudent.completed_at <= end_datetime
            ).count()
            
            completion_rate = (completed_assignments / total_assignments) if total_assignments > 0 else 0
            
            # Achievements earned
            achievements_earned = StudentAchievement.query.filter(
                StudentAchievement.student_id == student_id,
                StudentAchievement.unlocked_at >= start_datetime,
                StudentAchievement.unlocked_at <= end_datetime
            ).count()
            
            # Week-by-week breakdown
            weekly_breakdown = []
            current_monday = start_date
            while current_monday.weekday() != 0:  # Find first Monday
                current_monday += timedelta(days=1)
            
            while current_monday <= end_date:
                week_end = min(current_monday + timedelta(days=6), end_date)
                week_start_dt = datetime.combine(current_monday, datetime.min.time())
                week_end_dt = datetime.combine(week_end, datetime.max.time())
                
                week_sessions = [s for s in sessions if week_start_dt <= s.started_at <= week_end_dt]
                week_time = sum(
                    (s.ended_at - s.started_at).total_seconds() / 60
                    if s.ended_at else 0
                    for s in week_sessions
                )
                week_questions = sum(s.questions_answered or 0 for s in week_sessions)
                week_correct = sum(s.questions_correct or 0 for s in week_sessions)
                week_accuracy = (week_correct / week_questions) if week_questions > 0 else 0
                
                weekly_breakdown.append({
                    'week_start': current_monday.isoformat(),
                    'week_end': week_end.isoformat(),
                    'time_minutes': round(week_time, 1),
                    'sessions': len(week_sessions),
                    'questions': week_questions,
                    'accuracy': round(week_accuracy, 2)
                })
                
                current_monday += timedelta(days=7)
            
            # Calculate consistency score
            days_in_month = (end_date - start_date).days + 1
            days_with_practice = len(set(s.started_at.date() for s in sessions))
            consistency_score = days_with_practice / days_in_month if days_in_month > 0 else 0
            
            # Generate insights
            insights = {}
            
            # Progress trajectory
            if len(weekly_breakdown) >= 2:
                first_week_acc = weekly_breakdown[0]['accuracy']
                last_week_acc = weekly_breakdown[-1]['accuracy']
                if last_week_acc > first_week_acc + 0.05:
                    insights['trajectory'] = 'improving'
                elif last_week_acc < first_week_acc - 0.05:
                    insights['trajectory'] = 'declining'
                else:
                    insights['trajectory'] = 'stable'
            
            # Consistency rating
            if consistency_score >= 0.8:
                insights['consistency_rating'] = 'excellent'
            elif consistency_score >= 0.6:
                insights['consistency_rating'] = 'good'
            elif consistency_score >= 0.4:
                insights['consistency_rating'] = 'fair'
            else:
                insights['consistency_rating'] = 'needs_improvement'
            
            insights['consistency_score'] = round(consistency_score, 2)
            
            # Build report
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'month_name': start_date.strftime('%B %Y')
                },
                'summary': {
                    'total_time_minutes': round(total_time, 1),
                    'total_sessions': len(sessions),
                    'questions_answered': total_questions,
                    'accuracy': round(accuracy, 2),
                    'skills_mastered': skills_mastered,
                    'assignment_completion_rate': round(completion_rate, 2),
                    'achievements_earned': achievements_earned
                },
                'weekly_breakdown': weekly_breakdown,
                'insights': insights
            }
            
            return {'success': True, 'report': report}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def generate_skill_report(parent_id, student_id):
        """Generate skill performance report"""
        try:
            # Verify authorization
            if not ReportService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get all learning paths
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            
            skills = []
            category_time = {}
            
            for path in paths:
                if not path.skill:
                    continue
                
                # Get time spent on this skill (from sessions)
                skill_sessions = StudentSession.query.filter_by(
                    student_id=student_id,
                    skill_id=path.skill_id
                ).all()
                
                time_spent = sum(
                    (s.ended_at - s.started_at).total_seconds() / 60
                    if s.ended_at else 0
                    for s in skill_sessions
                )
                
                # Determine trend (compare recent vs overall)
                recent_sessions = [s for s in skill_sessions if s.started_at >= datetime.utcnow() - timedelta(days=14)]
                if recent_sessions:
                    recent_correct = sum(s.questions_correct or 0 for s in recent_sessions)
                    recent_total = sum(s.questions_answered or 0 for s in recent_sessions)
                    recent_accuracy = (recent_correct / recent_total) if recent_total > 0 else 0
                    
                    if recent_accuracy > path.current_accuracy + 0.05:
                        trend = 'improving'
                    elif recent_accuracy < path.current_accuracy - 0.05:
                        trend = 'declining'
                    else:
                        trend = 'stable'
                else:
                    trend = 'no_recent_activity'
                
                skills.append({
                    'skill_name': path.skill.name,
                    'category': path.skill.subject_area,
                    'accuracy': round(path.current_accuracy, 2),
                    'mastery_status': 'mastered' if path.mastery_achieved else ('in_progress' if path.questions_answered > 0 else 'not_started'),
                    'time_spent_minutes': round(time_spent, 1),
                    'questions_answered': path.questions_answered,
                    'mastered_date': path.mastery_date.isoformat() if path.mastery_date else None,
                    'trend': trend
                })
                
                # Track time by category
                category = path.skill.subject_area
                category_time[category] = category_time.get(category, 0) + time_spent
            
            # Calculate totals
            total_skills = len(skills)
            mastered = sum(1 for s in skills if s['mastery_status'] == 'mastered')
            in_progress = sum(1 for s in skills if s['mastery_status'] == 'in_progress')
            not_started = sum(1 for s in skills if s['mastery_status'] == 'not_started')
            
            # Generate insights
            top_skills = sorted(skills, key=lambda x: x['accuracy'], reverse=True)[:3]
            needs_attention = [s['skill_name'] for s in skills if s['accuracy'] < 0.70 and s['mastery_status'] != 'not_started']
            recent_mastery = [s['skill_name'] for s in skills if s['mastered_date'] and 
                            datetime.fromisoformat(s['mastered_date']) >= datetime.utcnow() - timedelta(days=30)]
            
            insights = {
                'top_skills': [s['skill_name'] for s in top_skills],
                'needs_attention': needs_attention,
                'recent_mastery': recent_mastery,
                'time_distribution': {k: round(v, 1) for k, v in category_time.items()}
            }
            
            # Build report
            report = {
                'total_skills': total_skills,
                'mastered': mastered,
                'in_progress': in_progress,
                'not_started': not_started,
                'skills': skills,
                'insights': insights
            }
            
            return {'success': True, 'report': report}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def generate_time_analysis(parent_id, student_id, days=30):
        """Generate time analysis report"""
        try:
            # Verify authorization
            if not ReportService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days - 1)
            
            # Get all sessions in period
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= start_date,
                StudentSession.started_at <= end_date
            ).all()
            
            # Calculate total time and sessions
            total_time = sum(
                (s.ended_at - s.started_at).total_seconds() / 60
                if s.ended_at else 0
                for s in sessions
            )
            total_sessions = len(sessions)
            avg_session = total_time / total_sessions if total_sessions > 0 else 0
            
            # Group by day of week
            by_day_of_week = {
                'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0,
                'Friday': 0, 'Saturday': 0, 'Sunday': 0
            }
            
            for session in sessions:
                day_name = session.started_at.strftime('%A')
                session_time = (session.ended_at - session.started_at).total_seconds() / 60 if session.ended_at else 0
                by_day_of_week[day_name] += session_time
            
            # Round values
            by_day_of_week = {k: round(v, 1) for k, v in by_day_of_week.items()}
            
            # Group by time of day
            by_time_of_day = {'morning': 0, 'afternoon': 0, 'evening': 0}
            
            for session in sessions:
                hour = session.started_at.hour
                session_time = (session.ended_at - session.started_at).total_seconds() / 60 if session.ended_at else 0
                
                if 6 <= hour < 12:
                    by_time_of_day['morning'] += session_time
                elif 12 <= hour < 18:
                    by_time_of_day['afternoon'] += session_time
                else:
                    by_time_of_day['evening'] += session_time
            
            # Round values
            by_time_of_day = {k: round(v, 1) for k, v in by_time_of_day.items()}
            
            # Session statistics
            session_durations = [
                (s.ended_at - s.started_at).total_seconds() / 60
                for s in sessions if s.ended_at
            ]
            
            if session_durations:
                session_durations.sort()
                median_idx = len(session_durations) // 2
                median_session = session_durations[median_idx]
                longest_session = max(session_durations)
                shortest_session = min(session_durations)
            else:
                median_session = 0
                longest_session = 0
                shortest_session = 0
            
            # Calculate consistency score
            days_with_practice = len(set(s.started_at.date() for s in sessions))
            consistency_score = days_with_practice / days if days > 0 else 0
            
            # Generate insights
            insights = {}
            
            # Most productive day
            if by_day_of_week:
                most_productive_day = max(by_day_of_week.items(), key=lambda x: x[1])
                insights['most_productive_day'] = most_productive_day[0]
            
            # Preferred time
            if by_time_of_day:
                preferred_time = max(by_time_of_day.items(), key=lambda x: x[1])
                insights['preferred_time'] = preferred_time[0]
            
            # Consistency rating
            if consistency_score >= 0.8:
                insights['consistency_rating'] = 'excellent'
                insights['recommendation'] = 'Current practice schedule is working well - keep it up!'
            elif consistency_score >= 0.6:
                insights['consistency_rating'] = 'good'
                insights['recommendation'] = 'Good practice habits - try to maintain consistency'
            elif consistency_score >= 0.4:
                insights['consistency_rating'] = 'fair'
                insights['recommendation'] = 'Consider practicing more regularly for better results'
            else:
                insights['consistency_rating'] = 'needs_improvement'
                insights['recommendation'] = 'More frequent practice will help improve skills faster'
            
            # Build report
            report = {
                'period_days': days,
                'total_time_minutes': round(total_time, 1),
                'total_sessions': total_sessions,
                'average_session_minutes': round(avg_session, 1),
                'by_day_of_week': by_day_of_week,
                'by_time_of_day': by_time_of_day,
                'session_stats': {
                    'longest_session_minutes': round(longest_session, 1),
                    'shortest_session_minutes': round(shortest_session, 1),
                    'median_session_minutes': round(median_session, 1)
                },
                'consistency_score': round(consistency_score, 2),
                'insights': insights
            }
            
            return {'success': True, 'report': report}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

