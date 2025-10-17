"""
Communication service for parent-teacher messaging.
"""
from src.database import db
from src.models.parent_communication import ParentTeacherMessage
from src.models.parent import ParentChildLink
from src.models.class_group import ClassMembership
from datetime import datetime


class CommunicationService:
    """Service for parent-teacher communication"""
    
    @staticmethod
    def send_message(parent_id, teacher_id, student_id, subject, message, message_type='question'):
        """Send message from parent to teacher"""
        try:
            # Verify parent-child link
            link = ParentChildLink.query.filter_by(
                parent_id=parent_id,
                student_id=student_id,
                status='active'
            ).first()
            
            if not link:
                return {'success': False, 'error': 'Not authorized for this student'}, 403
            
            # Verify student has this teacher (via class membership)
            membership = ClassMembership.query.filter_by(
                student_id=student_id
            ).first()
            
            if not membership or membership.class_group.teacher_id != teacher_id:
                return {'success': False, 'error': 'Student does not have this teacher'}, 400
            
            # Create message
            new_message = ParentTeacherMessage(
                parent_id=parent_id,
                teacher_id=teacher_id,
                student_id=student_id,
                subject=subject,
                message=message,
                message_type=message_type,
                parent_read=True,
                teacher_read=False
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            return {'success': True, 'message': new_message.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def reply_to_message(parent_id, message_id, reply_text):
        """Reply to a message"""
        try:
            # Get original message
            original = ParentTeacherMessage.query.get(message_id)
            if not original:
                return {'success': False, 'error': 'Message not found'}, 404
            
            # Verify parent owns the original message
            if original.parent_id != parent_id:
                return {'success': False, 'error': 'Not authorized'}, 403
            
            # Create reply
            reply = ParentTeacherMessage(
                parent_id=parent_id,
                teacher_id=original.teacher_id,
                student_id=original.student_id,
                subject=f"Re: {original.subject}",
                message=reply_text,
                message_type=original.message_type,
                replied_to_id=message_id,
                parent_read=True,
                teacher_read=False
            )
            
            db.session.add(reply)
            db.session.commit()
            
            return {'success': True, 'message': reply.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_messages(parent_id, filter_type='all'):
        """Get messages for parent (inbox + sent)"""
        try:
            query = ParentTeacherMessage.query.filter_by(parent_id=parent_id)
            
            if filter_type == 'unread':
                query = query.filter_by(parent_read=False)
            elif filter_type == 'sent':
                # Messages where parent is sender (no replied_to means original message)
                query = query.filter_by(replied_to_id=None)
            
            messages = query.order_by(ParentTeacherMessage.created_at.desc()).all()
            
            return {
                'success': True,
                'messages': [m.to_dict() for m in messages]
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_message(parent_id, message_id):
        """Get specific message"""
        try:
            message = ParentTeacherMessage.query.get(message_id)
            
            if not message:
                return {'success': False, 'error': 'Message not found'}, 404
            
            if message.parent_id != parent_id:
                return {'success': False, 'error': 'Not authorized'}, 403
            
            # Get conversation thread (original + replies)
            if message.replied_to_id:
                # This is a reply, get the original
                original_id = message.replied_to_id
            else:
                # This is the original
                original_id = message.id
            
            # Get all messages in thread
            thread = ParentTeacherMessage.query.filter(
                db.or_(
                    ParentTeacherMessage.id == original_id,
                    ParentTeacherMessage.replied_to_id == original_id
                )
            ).order_by(ParentTeacherMessage.created_at.asc()).all()
            
            return {
                'success': True,
                'message': message.to_dict(),
                'thread': [m.to_dict() for m in thread]
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def mark_as_read(parent_id, message_id):
        """Mark message as read"""
        try:
            message = ParentTeacherMessage.query.get(message_id)
            
            if not message:
                return {'success': False, 'error': 'Message not found'}, 404
            
            if message.parent_id != parent_id:
                return {'success': False, 'error': 'Not authorized'}, 403
            
            message.parent_read = True
            db.session.commit()
            
            return {'success': True}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_unread_count(parent_id):
        """Get count of unread messages"""
        try:
            count = ParentTeacherMessage.query.filter_by(
                parent_id=parent_id,
                parent_read=False
            ).count()
            
            return {'success': True, 'count': count}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

