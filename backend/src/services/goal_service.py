"""
Goal service for goal setting and tracking.
"""
from src.database import db
from src.models.parent_communication import Goal, GoalNote, GoalProgress
from src.models.parent import ParentChildLink
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.assignment_model import AssignmentStudent
from src.models.streak import StreakTracking
from datetime import datetime, timedelta


class GoalService:
    """Service for goal management and tracking"""
    
    @staticmethod
    def create_goal(student_id, created_by_id, created_by_type, goal_type, title, description, target_value, due_date=None, skill_id=None):
        """Create a new goal"""
        try:
            # Verify authorization based on creator type
            if created_by_type == 'parent':
                link = ParentChildLink.query.filter_by(
                    parent_id=created_by_id,
                    student_id=student_id,
                    status='active'
                ).first()
                if not link:
                    return {'success': False, 'error': 'Not authorized for this student'}, 403
            
            # Create goal
            goal = Goal(
                student_id=student_id,
                created_by_id=created_by_id,
                created_by_type=created_by_type,
                goal_type=goal_type,
                title=title,
                description=description,
                target_value=target_value,
                current_value=0.0,
                progress_percent=0.0,
                status='active',
                due_date=due_date,
                skill_id=skill_id
            )
            
            db.session.add(goal)
            db.session.commit()
            
            # Update progress immediately
            GoalService._update_goal_progress(goal.id)
            
            return {'success': True, 'goal': goal.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_student_goals(student_id, status='all'):
        """Get goals for a student"""
        try:
            query = Goal.query.filter_by(student_id=student_id)
            
            if status != 'all':
                query = query.filter_by(status=status)
            
            goals = query.order_by(Goal.created_at.desc()).all()
            
            return {
                'success': True,
                'goals': [g.to_dict() for g in goals]
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_goal(goal_id):
        """Get specific goal with notes and progress"""
        try:
            goal = Goal.query.get(goal_id)
            
            if not goal:
                return {'success': False, 'error': 'Goal not found'}, 404
            
            goal_dict = goal.to_dict()
            goal_dict['notes'] = [n.to_dict() for n in goal.notes]
            goal_dict['progress_history'] = [p.to_dict() for p in goal.progress_history[:10]]  # Last 10 updates
            
            return {'success': True, 'goal': goal_dict}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def update_goal(goal_id, title=None, description=None, target_value=None, due_date=None):
        """Update goal (only if not completed)"""
        try:
            goal = Goal.query.get(goal_id)
            
            if not goal:
                return {'success': False, 'error': 'Goal not found'}, 404
            
            if goal.status == 'completed':
                return {'success': False, 'error': 'Cannot update completed goal'}, 400
            
            if title:
                goal.title = title
            if description:
                goal.description = description
            if target_value:
                goal.target_value = target_value
                # Recalculate progress
                goal.progress_percent = min((goal.current_value / target_value) * 100, 100)
            if due_date is not None:
                goal.due_date = due_date
            
            db.session.commit()
            
            return {'success': True, 'goal': goal.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def delete_goal(goal_id):
        """Delete goal"""
        try:
            goal = Goal.query.get(goal_id)
            
            if not goal:
                return {'success': False, 'error': 'Goal not found'}, 404
            
            db.session.delete(goal)
            db.session.commit()
            
            return {'success': True}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def add_note(goal_id, user_id, user_type, note):
        """Add note/encouragement to goal"""
        try:
            goal = Goal.query.get(goal_id)
            
            if not goal:
                return {'success': False, 'error': 'Goal not found'}, 404
            
            goal_note = GoalNote(
                goal_id=goal_id,
                user_id=user_id,
                user_type=user_type,
                note=note
            )
            
            db.session.add(goal_note)
            db.session.commit()
            
            return {'success': True, 'note': goal_note.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def add_manual_progress(goal_id, value, note=None):
        """Add manual progress update (for custom goals)"""
        try:
            goal = Goal.query.get(goal_id)
            
            if not goal:
                return {'success': False, 'error': 'Goal not found'}, 404
            
            if goal.status != 'active':
                return {'success': False, 'error': 'Goal is not active'}, 400
            
            # Update current value
            goal.current_value = value
            goal.progress_percent = min((value / goal.target_value) * 100, 100)
            
            # Check if completed
            if goal.progress_percent >= 100:
                goal.status = 'completed'
                goal.completed_at = datetime.utcnow()
            
            # Record progress
            progress = GoalProgress(
                goal_id=goal_id,
                value=value,
                progress_percent=goal.progress_percent,
                note=note
            )
            
            db.session.add(progress)
            db.session.commit()
            
            return {'success': True, 'goal': goal.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def _update_goal_progress(goal_id):
        """Update goal progress based on type (automatic tracking)"""
        try:
            goal = Goal.query.get(goal_id)
            
            if not goal or goal.status != 'active':
                return
            
            old_value = goal.current_value
            
            if goal.goal_type == 'skill_mastery':
                # Check if skill is mastered
                if goal.skill_id:
                    path = LearningPath.query.filter_by(
                        student_id=goal.student_id,
                        skill_id=goal.skill_id
                    ).first()
                    
                    if path:
                        goal.current_value = path.current_accuracy * 100
                        goal.progress_percent = min((path.current_accuracy / 0.90) * 100, 100)
                        
                        if path.mastery_achieved:
                            goal.status = 'completed'
                            goal.completed_at = datetime.utcnow()
            
            elif goal.goal_type == 'practice_time':
                # Calculate practice time in target period
                # Assuming weekly goal, get last 7 days
                start_date = datetime.utcnow() - timedelta(days=7)
                sessions = StudentSession.query.filter(
                    StudentSession.student_id == goal.student_id,
                    StudentSession.started_at >= start_date
                ).all()
                
                total_time = sum(
                    (s.ended_at - s.started_at).total_seconds() / 60
                    if s.ended_at else 0
                    for s in sessions
                )
                
                goal.current_value = total_time
                goal.progress_percent = min((total_time / goal.target_value) * 100, 100)
                
                if goal.progress_percent >= 100:
                    goal.status = 'completed'
                    goal.completed_at = datetime.utcnow()
            
            elif goal.goal_type == 'accuracy':
                # Get overall accuracy from all sessions
                sessions = StudentSession.query.filter_by(
                    student_id=goal.student_id
                ).all()
                
                total_correct = sum(s.questions_correct or 0 for s in sessions)
                total_questions = sum(s.questions_answered or 0 for s in sessions)
                
                if total_questions > 0:
                    accuracy = (total_correct / total_questions) * 100
                    goal.current_value = accuracy
                    goal.progress_percent = min((accuracy / goal.target_value) * 100, 100)
                    
                    if goal.progress_percent >= 100:
                        goal.status = 'completed'
                        goal.completed_at = datetime.utcnow()
            
            elif goal.goal_type == 'assignments':
                # Count completed assignments
                completed = AssignmentStudent.query.filter_by(
                    student_id=goal.student_id,
                    status='completed'
                ).count()
                
                goal.current_value = completed
                goal.progress_percent = min((completed / goal.target_value) * 100, 100)
                
                if goal.progress_percent >= 100:
                    goal.status = 'completed'
                    goal.completed_at = datetime.utcnow()
            
            elif goal.goal_type == 'streak':
                # Check current streak
                streak = StreakTracking.query.filter_by(
                    student_id=goal.student_id
                ).first()
                
                if streak:
                    goal.current_value = streak.practice_streak
                    goal.progress_percent = min((streak.practice_streak / goal.target_value) * 100, 100)
                    
                    if goal.progress_percent >= 100:
                        goal.status = 'completed'
                        goal.completed_at = datetime.utcnow()
            
            # Record progress if value changed
            if goal.current_value != old_value:
                progress = GoalProgress(
                    goal_id=goal_id,
                    value=goal.current_value,
                    progress_percent=goal.progress_percent,
                    note='Automatic update'
                )
                db.session.add(progress)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating goal progress: {e}")
    
    @staticmethod
    def update_all_active_goals(student_id):
        """Update all active goals for a student (called after learning activity)"""
        try:
            active_goals = Goal.query.filter_by(
                student_id=student_id,
                status='active'
            ).all()
            
            for goal in active_goals:
                GoalService._update_goal_progress(goal.id)
            
        except Exception as e:
            print(f"Error updating active goals: {e}")

