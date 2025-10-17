"""
Intervention Service
Business logic for teacher interventions and messaging
"""
from src.database import db
from src.models.intervention import TeacherMessage, MessageTemplate, Intervention, Meeting
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.assignment_model import Assignment, AssignmentStudent
from src.services.assignment_service import AssignmentService
from datetime import datetime, timedelta
import re


class InterventionService:
    """Service for teacher interventions"""
    
    @staticmethod
    def send_message(teacher_id, student_id, message, template_id=None):
        """
        Send message from teacher to student
        
        Args:
            teacher_id: Teacher user ID
            student_id: Student ID
            message: Message content
            template_id: Optional template ID
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Validate student exists
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Create message
            msg = TeacherMessage(
                teacher_id=teacher_id,
                student_id=student_id,
                message=message,
                template_id=template_id
            )
            db.session.add(msg)
            
            # Create intervention record
            intervention = Intervention(
                teacher_id=teacher_id,
                student_id=student_id,
                intervention_type='message',
                action_taken=f'Sent message: "{message[:50]}..."'
            )
            db.session.add(intervention)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': msg.to_dict(),
                'intervention_id': intervention.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def create_targeted_assignment(teacher_id, student_id, auto_fill=True):
        """
        Create targeted assignment for struggling student
        
        Args:
            teacher_id: Teacher user ID
            student_id: Student ID
            auto_fill: Whether to auto-fill with struggling skills
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            if auto_fill:
                # Get struggling skills (accuracy < 70%)
                paths = LearningPath.query.filter_by(student_id=student_id).all()
                struggling_skills = [
                    {'skill_id': p.skill_id, 'skill_name': p.skill.name, 'accuracy': p.current_accuracy}
                    for p in paths
                    if p.skill and p.current_accuracy < 0.7
                ]
                struggling_skills.sort(key=lambda x: x['accuracy'])
                
                if not struggling_skills:
                    return {'success': False, 'error': 'No struggling skills found'}, 400
                
                # Take top 3 struggling skills
                skill_ids = [s['skill_id'] for s in struggling_skills[:3]]
                skill_names = [s['skill_name'] for s in struggling_skills[:3]]
                
                # Determine difficulty based on average accuracy
                avg_accuracy = sum(s['accuracy'] for s in struggling_skills[:3]) / len(struggling_skills[:3])
                if avg_accuracy < 0.5:
                    difficulty = 'easy'
                elif avg_accuracy < 0.65:
                    difficulty = 'medium'
                else:
                    difficulty = 'adaptive'
                
                # Set question count
                question_count = 15
                
                # Set due date (3 days from now)
                due_date = datetime.utcnow() + timedelta(days=3)
                
                # Create assignment data
                assignment_data = {
                    'title': f'Targeted Practice - {", ".join(skill_names)}',
                    'description': 'Practice assignment to help improve your skills',
                    'student_ids': [student_id],
                    'skill_ids': skill_ids,
                    'question_count': question_count,
                    'difficulty': difficulty,
                    'due_date': due_date.isoformat()
                }
            else:
                return {'success': False, 'error': 'Manual assignment creation not yet implemented'}, 400
            
            # Create assignment using AssignmentService
            result, status = AssignmentService.create_assignment(teacher_id, assignment_data)
            
            if not result.get('success'):
                return result, status
            
            # Create intervention record
            intervention = Intervention(
                teacher_id=teacher_id,
                student_id=student_id,
                intervention_type='assignment',
                action_taken=f'Created targeted assignment: {assignment_data["title"]}'
            )
            db.session.add(intervention)
            db.session.commit()
            
            return {
                'success': True,
                'assignment': result['assignment'],
                'intervention_id': intervention.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def schedule_meeting(teacher_id, student_id, meeting_type, scheduled_at, duration_minutes=30, location=None, notes=None):
        """Schedule meeting with student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Parse datetime if string
            if isinstance(scheduled_at, str):
                scheduled_at = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            
            # Create meeting
            meeting = Meeting(
                teacher_id=teacher_id,
                student_id=student_id,
                meeting_type=meeting_type,
                scheduled_at=scheduled_at,
                duration_minutes=duration_minutes,
                location=location,
                notes=notes
            )
            db.session.add(meeting)
            
            # Create intervention record
            intervention = Intervention(
                teacher_id=teacher_id,
                student_id=student_id,
                intervention_type='meeting',
                action_taken=f'Scheduled {meeting_type} meeting for {scheduled_at.strftime("%Y-%m-%d %H:%M")}'
            )
            db.session.add(intervention)
            
            db.session.commit()
            
            return {
                'success': True,
                'meeting': meeting.to_dict(),
                'intervention_id': intervention.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def notify_parent(teacher_id, student_id, concern_type, message):
        """Send notification to parent (placeholder for future email integration)"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Create intervention record
            intervention = Intervention(
                teacher_id=teacher_id,
                student_id=student_id,
                intervention_type='parent_notification',
                action_taken=f'Notified parent about {concern_type}: {message[:50]}...'
            )
            db.session.add(intervention)
            db.session.commit()
            
            # TODO: Implement actual email sending
            
            return {
                'success': True,
                'message': 'Parent notification sent (placeholder)',
                'intervention_id': intervention.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def mark_intervention_resolved(intervention_id, resolution_notes, effectiveness_rating=None):
        """Mark intervention as resolved"""
        try:
            intervention = Intervention.query.get(intervention_id)
            if not intervention:
                return {'success': False, 'error': 'Intervention not found'}, 404
            
            intervention.is_resolved = True
            intervention.resolved_at = datetime.utcnow()
            intervention.resolution_notes = resolution_notes
            if effectiveness_rating:
                intervention.effectiveness_rating = effectiveness_rating
            
            db.session.commit()
            
            return {
                'success': True,
                'intervention': intervention.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_intervention_history(student_id, teacher_id=None):
        """Get intervention history for student"""
        try:
            query = Intervention.query.filter_by(student_id=student_id)
            
            if teacher_id:
                query = query.filter_by(teacher_id=teacher_id)
            
            interventions = query.order_by(Intervention.created_at.desc()).all()
            
            return {
                'success': True,
                'interventions': [i.to_dict() for i in interventions],
                'total': len(interventions),
                'resolved': sum(1 for i in interventions if i.is_resolved),
                'pending': sum(1 for i in interventions if not i.is_resolved)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_message_templates(category=None):
        """Get message templates"""
        try:
            query = MessageTemplate.query
            
            if category:
                query = query.filter_by(category=category)
            
            templates = query.all()
            
            return {
                'success': True,
                'templates': [t.to_dict() for t in templates]
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def create_default_templates():
        """Create default message templates"""
        try:
            templates = [
                # Inactive templates
                {
                    'category': 'inactive',
                    'title': 'Check In - Inactive Student',
                    'content': 'Hi {student_name}, I noticed you haven\'t practiced in {days_inactive} days. Is everything okay? Let me know if you need help!',
                    'variables': ['student_name', 'days_inactive']
                },
                {
                    'category': 'inactive',
                    'title': 'Encouragement - Come Back',
                    'content': 'Hey {student_name}, we miss you! Can you hop on and practice for a few minutes today?',
                    'variables': ['student_name']
                },
                {
                    'category': 'inactive',
                    'title': 'Class Update - Rejoin',
                    'content': 'Hi {student_name}, your class is working on {skill_name}. Can you practice 10 questions today?',
                    'variables': ['student_name', 'skill_name']
                },
                
                # Struggling templates
                {
                    'category': 'struggling',
                    'title': 'Support - Struggling with Skill',
                    'content': 'Hi {student_name}, I see you\'re working hard on {skill_name}. I created an easier assignment to help you build confidence.',
                    'variables': ['student_name', 'skill_name']
                },
                {
                    'category': 'struggling',
                    'title': 'Meeting Offer - Extra Help',
                    'content': 'Hey {student_name}, {skill_name} can be tricky! Let\'s meet tomorrow to go over it together.',
                    'variables': ['student_name', 'skill_name']
                },
                {
                    'category': 'struggling',
                    'title': 'Resource Suggestion',
                    'content': 'Hi {student_name}, I noticed you\'re struggling with {skill_name}. Try watching the video tutorial first, then practice.',
                    'variables': ['student_name', 'skill_name']
                },
                
                # Overdue templates
                {
                    'category': 'overdue',
                    'title': 'Reminder - Due Soon',
                    'content': 'Hi {student_name}, the {assignment_name} is due soon. Can you complete it today?',
                    'variables': ['student_name', 'assignment_name']
                },
                {
                    'category': 'overdue',
                    'title': 'Check - Not Started',
                    'content': 'Hey {student_name}, I see you haven\'t started {assignment_name} yet. Do you need help getting started?',
                    'variables': ['student_name', 'assignment_name']
                },
                {
                    'category': 'overdue',
                    'title': 'Follow Up - Overdue',
                    'content': 'Hi {student_name}, {assignment_name} was due yesterday. Please complete it as soon as possible.',
                    'variables': ['student_name', 'assignment_name']
                },
                
                # Encouragement templates
                {
                    'category': 'encouragement',
                    'title': 'Praise - Great Work',
                    'content': 'Great job on {assignment_name}, {student_name}! Keep up the excellent work!',
                    'variables': ['student_name', 'assignment_name']
                },
                {
                    'category': 'encouragement',
                    'title': 'Celebrate - Improvement',
                    'content': 'Wow, {student_name}! Your accuracy on {skill_name} improved to {accuracy}%. Awesome progress!',
                    'variables': ['student_name', 'skill_name', 'accuracy']
                },
                {
                    'category': 'encouragement',
                    'title': 'Streak - Keep Going',
                    'content': 'Hi {student_name}, you\'re on a {streak_days}-day streak! Keep it going!',
                    'variables': ['student_name', 'streak_days']
                }
            ]
            
            for template_data in templates:
                # Check if template already exists
                existing = MessageTemplate.query.filter_by(
                    category=template_data['category'],
                    title=template_data['title']
                ).first()
                
                if not existing:
                    template = MessageTemplate(**template_data)
                    db.session.add(template)
            
            db.session.commit()
            
            return {'success': True, 'message': 'Default templates created'}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def fill_template(template_id, variables):
        """Fill template with variables"""
        try:
            template = MessageTemplate.query.get(template_id)
            if not template:
                return {'success': False, 'error': 'Template not found'}, 404
            
            message = template.content
            
            # Replace variables
            for key, value in variables.items():
                placeholder = '{' + key + '}'
                message = message.replace(placeholder, str(value))
            
            return {
                'success': True,
                'message': message,
                'template_id': template_id
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

