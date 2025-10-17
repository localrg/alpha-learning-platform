"""
Parent View Service
Business logic for parent viewing of child progress
"""
from src.database import db
from src.models.parent import Parent, ParentChildLink
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.student_session import StudentSession
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.gamification import StudentProgress
from src.models.achievement import Achievement, StudentAchievement
from src.models.streak import StreakTracking
from datetime import datetime, timedelta


class ParentViewService:
    """Service for parent viewing of child progress"""
    
    @staticmethod
    def verify_parent_child_link(parent_id, student_id):
        """
        Verify parent has active link to child
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
        
        Returns:
            Boolean
        """
        link = ParentChildLink.query.filter_by(
            parent_id=parent_id,
            student_id=student_id,
            status='active'
        ).first()
        
        return link is not None
    
    @staticmethod
    def get_child_overview(parent_id, student_id):
        """
        Get child overview dashboard
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Verify link
            if not ParentViewService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get student
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Get sessions (last 30 days)
            cutoff = datetime.utcnow() - timedelta(days=30)
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= cutoff
            ).all()
            
            # Calculate metrics
            total_questions = sum(s.questions_answered for s in sessions)
            total_correct = sum(s.questions_correct for s in sessions)
            accuracy = total_correct / total_questions if total_questions > 0 else 0
            
            total_time = sum(
                (s.ended_at - s.started_at).total_seconds() / 3600
                for s in sessions if s.ended_at
            )
            
            # Get skill summary
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            skills_mastered = sum(1 for p in paths if p.mastery_achieved)
            total_skills = len(paths)
            
            # Get streak
            streak = StreakTracking.query.filter_by(student_id=student_id).first()
            current_streak = streak.practice_streak if streak else 0
            
            # Get assignments
            assignments = AssignmentStudent.query.filter_by(student_id=student_id).all()
            completed_assignments = sum(1 for a in assignments if a.status == 'completed')
            total_assignments = len(assignments)
            
            # Get gamification
            progress = StudentProgress.query.filter_by(student_id=student_id).first()
            
            # Get most practiced skill (last 7 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            recent_sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= recent_cutoff
            ).all()
            
            skill_counts = {}
            for session in recent_sessions:
                if session.skill_id:
                    skill_counts[session.skill_id] = skill_counts.get(session.skill_id, 0) + session.questions_answered
            
            most_practiced_skill = None
            most_practiced_count = 0
            if skill_counts:
                most_practiced_skill_id = max(skill_counts, key=skill_counts.get)
                most_practiced_count = skill_counts[most_practiced_skill_id]
                path = LearningPath.query.filter_by(
                    student_id=student_id,
                    skill_id=most_practiced_skill_id
                ).first()
                if path and path.skill:
                    most_practiced_skill = path.skill.name
            
            # Get next assignment due
            next_assignment = AssignmentStudent.query.join(
                Assignment
            ).filter(
                AssignmentStudent.student_id == student_id,
                AssignmentStudent.status.in_(['assigned', 'in_progress']),
                Assignment.due_date.isnot(None)
            ).order_by(Assignment.due_date).first()
            
            next_due = None
            if next_assignment and next_assignment.assignment:
                next_due = {
                    'title': next_assignment.assignment.title,
                    'due_date': next_assignment.assignment.due_date.isoformat()
                }
            
            return {
                'success': True,
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'grade': student.grade
                },
                'metrics': {
                    'accuracy': round(accuracy, 2),
                    'questions_answered': total_questions,
                    'time_spent_hours': round(total_time, 1),
                    'level': progress.current_level if progress else 1,
                    'xp': progress.total_xp if progress else 0,
                    'skills_mastered': skills_mastered,
                    'total_skills': total_skills,
                    'current_streak': current_streak,
                    'assignments_completed': completed_assignments,
                    'total_assignments': total_assignments
                },
                'quick_stats': {
                    'last_practice': sessions[-1].started_at.isoformat() if sessions else None,
                    'most_practiced_skill': most_practiced_skill,
                    'most_practiced_count': most_practiced_count,
                    'next_assignment_due': next_due
                }
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_child_skills(parent_id, student_id, filter_type='all'):
        """
        Get child skill progress
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            filter_type: 'all', 'mastered', 'in_progress', 'needs_practice'
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Verify link
            if not ParentViewService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get learning paths
            paths = LearningPath.query.filter_by(student_id=student_id).all()
            
            # Filter
            if filter_type == 'mastered':
                paths = [p for p in paths if p.mastery_achieved]
            elif filter_type == 'in_progress':
                paths = [p for p in paths if not p.mastery_achieved and p.questions_answered > 0]
            elif filter_type == 'needs_practice':
                paths = [p for p in paths if p.current_accuracy < 0.7]
            
            # Build skill list
            skills = []
            for path in paths:
                if not path.skill:
                    continue
                
                skills.append({
                    'skill_id': path.skill_id,
                    'skill_name': path.skill.name,
                    'accuracy': path.current_accuracy,
                    'mastery_status': 'mastered' if path.mastery_achieved else ('in_progress' if path.questions_answered > 0 else 'not_started'),
                    'questions_answered': path.questions_answered,
                    'questions_correct': path.correct_answers,
                    'last_practiced': path.last_practiced.isoformat() if path.last_practiced else None,
                    'mastered_at': path.mastery_date.isoformat() if path.mastery_date else None
                })
            
            # Sort by mastery status and accuracy
            def sort_key(skill):
                if skill['mastery_status'] == 'mastered':
                    return (0, -skill['accuracy'])
                elif skill['mastery_status'] == 'in_progress':
                    return (1, -skill['accuracy'])
                else:
                    return (2, 0)
            
            skills.sort(key=sort_key)
            
            return {
                'success': True,
                'skills': skills,
                'count': len(skills)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_child_activity(parent_id, student_id, days=30):
        """
        Get child activity feed
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            days: Number of days to look back
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Verify link
            if not ParentViewService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            cutoff = datetime.utcnow() - timedelta(days=days)
            activities = []
            
            # Practice sessions
            sessions = StudentSession.query.filter(
                StudentSession.student_id == student_id,
                StudentSession.started_at >= cutoff
            ).all()
            
            for session in sessions:
                activities.append({
                    'type': 'practice_session',
                    'date': session.started_at.isoformat(),
                    'skill_name': session.skill.name if session.skill else 'Unknown',
                    'questions': session.questions_answered,
                    'correct': session.questions_correct,
                    'accuracy': session.accuracy,
                    'duration_minutes': round(
                        (session.ended_at - session.started_at).total_seconds() / 60
                        if session.ended_at else 0
                    )
                })
            
            # Assignment completions
            assignments = AssignmentStudent.query.filter(
                AssignmentStudent.student_id == student_id,
                AssignmentStudent.status == 'completed'
            ).all()
            
            for assignment_student in assignments:
                if assignment_student.completed_at and assignment_student.completed_at >= cutoff:
                    activities.append({
                        'type': 'assignment_completed',
                        'date': assignment_student.completed_at.isoformat(),
                        'title': assignment_student.assignment.title if assignment_student.assignment else 'Unknown',
                        'questions_correct': assignment_student.questions_correct,
                        'questions_answered': assignment_student.questions_answered,
                        'accuracy': assignment_student.accuracy
                    })       
            # Skills mastered
            paths = LearningPath.query.filter(
                LearningPath.student_id == student_id,
                LearningPath.mastery_achieved == True
            ).all()
            
            for path in paths:
                if path.mastery_date and path.mastery_date >= cutoff:
                    activities.append({
                        'type': 'skill_mastered',
                        'date': path.mastery_date.isoformat(),
                        'skill_name': path.skill.name if path.skill else 'Unknown',
                        'accuracy': path.current_accuracy
                    })
            
            # Achievements earned
            student_achievements = StudentAchievement.query.filter(
                StudentAchievement.student_id == student_id,
                StudentAchievement.unlocked_at >= cutoff
            ).all()
            
            for sa in student_achievements:
                if sa.achievement and sa.unlocked_at:
                    activities.append({
                        'type': 'achievement_earned',
                        'date': sa.unlocked_at.isoformat(),
                        'achievement_name': sa.achievement.name,
                        'achievement_description': sa.achievement.description
                    })
            
            # Sort by date (most recent first)
            activities.sort(key=lambda x: x['date'], reverse=True)
            
            return {
                'success': True,
                'activities': activities,
                'count': len(activities)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_child_assignments(parent_id, student_id, filter_type='all'):
        """
        Get child assignments
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            filter_type: 'all', 'active', 'completed', 'overdue'
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Verify link
            if not ParentViewService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get assignments
            query = AssignmentStudent.query.filter_by(student_id=student_id)
            
            # Filter
            if filter_type == 'active':
                query = query.filter(AssignmentStudent.status.in_(['assigned', 'in_progress']))
            elif filter_type == 'completed':
                query = query.filter_by(status='completed')
            elif filter_type == 'overdue':
                query = query.filter(
                    AssignmentStudent.status.in_(['assigned', 'in_progress']),
                    AssignmentStudent.assignment.has(due_date__lt=datetime.utcnow())
                )
            
            assignments = query.all()
            
            # Build assignment list
            assignment_list = []
            for assignment_student in assignments:
                if not assignment_student.assignment:
                    continue
                
                assignment = assignment_student.assignment
                
                # Check if overdue
                is_overdue = False
                if assignment.due_date and assignment_student.status in ['assigned', 'in_progress']:
                    is_overdue = assignment.due_date < datetime.utcnow()
                
                assignment_list.append({
                    'id': assignment.id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                    'status': assignment_student.status,
                    'is_overdue': is_overdue,
                    'questions_correct': assignment_student.questions_correct,
                    'accuracy': assignment_student.accuracy,
                    'questions_answered': assignment_student.questions_answered,
                    'total_questions': assignment.question_count,
                    'started_at': assignment_student.started_at.isoformat() if assignment_student.started_at else None,
                    'completed_at': assignment_student.completed_at.isoformat() if assignment_student.completed_at else None,
                    'skill_count': len(assignment.skill_ids) if assignment.skill_ids else 0
                })
            
            # Sort by due date
            assignment_list.sort(key=lambda x: x['due_date'] if x['due_date'] else '9999-12-31')
            
            return {
                'success': True,
                'assignments': assignment_list,
                'count': len(assignment_list)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_child_achievements(parent_id, student_id):
        """
        Get child achievements
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Verify link
            if not ParentViewService.verify_parent_child_link(parent_id, student_id):
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Get earned achievements
            student_achievements = StudentAchievement.query.filter_by(
                student_id=student_id
            ).all()
            
            earned = []
            for sa in student_achievements:
                if sa.achievement and sa.unlocked_at:
                    earned.append({
                        'id': sa.achievement.id,
                        'name': sa.achievement.name,
                        'description': sa.achievement.description,
                        'category': sa.achievement.category,
                        'tier': sa.achievement.tier,
                        'icon_emoji': sa.achievement.icon_emoji,
                        'xp_reward': sa.achievement.xp_reward,
                        'earned_at': sa.unlocked_at.isoformat()
                    })
            
            # Sort by earned date (most recent first)
            earned.sort(key=lambda x: x['earned_at'], reverse=True)
            
            return {
                'success': True,
                'achievements': earned,
                'count': len(earned)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

