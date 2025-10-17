"""
Parent Service
Business logic for parent accounts and child linking
"""
from src.database import db
from src.models.parent import Parent, ParentChildLink, LinkRequest
from src.models.student import Student
from src.models.user import User
from datetime import datetime, timedelta
import random
import string


# Default notification preferences
DEFAULT_NOTIFICATION_PREFS = {
    'daily_summary': {'enabled': True, 'method': 'email'},
    'weekly_report': {'enabled': True, 'method': 'email'},
    'assignment_due': {'enabled': True, 'method': 'email'},
    'low_performance': {'enabled': True, 'method': 'email'},
    'inactivity_alert': {'enabled': True, 'method': 'email'},
    'achievements': {'enabled': False, 'method': 'email'},
    'quiet_hours': {'start': '22:00', 'end': '08:00'}
}


class ParentService:
    """Service for parent account management"""
    
    @staticmethod
    def create_parent_account(user_id, name, email, phone=None, notification_prefs=None):
        """
        Create parent profile
        
        Args:
            user_id: User ID
            name: Parent name
            email: Parent email
            phone: Phone number (optional)
            notification_prefs: Notification preferences (optional)
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Check if parent already exists
            existing = Parent.query.filter_by(user_id=user_id).first()
            if existing:
                return {'success': False, 'error': 'Parent profile already exists'}, 400
            
            # Check email uniqueness
            existing_email = Parent.query.filter_by(email=email).first()
            if existing_email:
                return {'success': False, 'error': 'Email already in use'}, 400
            
            # Create parent
            parent = Parent(
                user_id=user_id,
                name=name,
                email=email,
                phone=phone,
                notification_preferences=notification_prefs or DEFAULT_NOTIFICATION_PREFS
            )
            db.session.add(parent)
            db.session.commit()
            
            return {
                'success': True,
                'parent': parent.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_parent_by_user_id(user_id):
        """Get parent profile by user ID"""
        try:
            parent = Parent.query.filter_by(user_id=user_id).first()
            
            if not parent:
                return {'success': False, 'error': 'Parent not found'}, 404
            
            return {
                'success': True,
                'parent': parent.to_dict()
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def update_parent_profile(parent_id, name=None, phone=None):
        """Update parent profile"""
        try:
            parent = Parent.query.get(parent_id)
            if not parent:
                return {'success': False, 'error': 'Parent not found'}, 404
            
            if name:
                parent.name = name
            if phone is not None:
                parent.phone = phone
            
            parent.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'parent': parent.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def update_notification_preferences(parent_id, preferences):
        """Update notification preferences"""
        try:
            parent = Parent.query.get(parent_id)
            if not parent:
                return {'success': False, 'error': 'Parent not found'}, 404
            
            # Merge with existing preferences
            current_prefs = parent.notification_preferences or DEFAULT_NOTIFICATION_PREFS
            current_prefs.update(preferences)
            
            parent.notification_preferences = current_prefs
            parent.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'preferences': parent.notification_preferences
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def generate_invite_code(student_id):
        """
        Generate parent invite code for student
        
        Args:
            student_id: Student ID
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Check if student exists
            student = Student.query.get(student_id)
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Generate random 8-character code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Check if code already exists
            while LinkRequest.query.filter_by(invite_code=code).first():
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Create link request
            request = LinkRequest(
                student_id=student_id,
                request_type='invite_code',
                invite_code=code,
                expires_at=datetime.utcnow() + timedelta(days=7),
                status='pending'
            )
            db.session.add(request)
            db.session.commit()
            
            return {
                'success': True,
                'invite_code': code,
                'expires_at': request.expires_at.isoformat(),
                'request_id': request.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def link_child_by_code(parent_id, invite_code):
        """
        Link child using invite code
        
        Args:
            parent_id: Parent ID
            invite_code: Invite code from student
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Find link request
            request = LinkRequest.query.filter_by(
                invite_code=invite_code,
                request_type='invite_code'
            ).first()
            
            if not request:
                return {'success': False, 'error': 'Invalid invite code'}, 404
            
            # Check if already used
            if request.status != 'pending':
                return {'success': False, 'error': 'Invite code already used or expired'}, 400
            
            # Check expiration
            if request.expires_at < datetime.utcnow():
                request.status = 'expired'
                db.session.commit()
                return {'success': False, 'error': 'Invite code has expired'}, 400
            
            # Check if link already exists
            existing_link = ParentChildLink.query.filter_by(
                parent_id=parent_id,
                student_id=request.student_id,
                status='active'
            ).first()
            
            if existing_link:
                return {'success': False, 'error': 'Child already linked'}, 400
            
            # Create link
            link = ParentChildLink(
                parent_id=parent_id,
                student_id=request.student_id,
                status='active'
            )
            db.session.add(link)
            
            # Update request
            request.status = 'approved'
            request.approved_at = datetime.utcnow()
            request.parent_id = parent_id
            
            db.session.commit()
            
            return {
                'success': True,
                'link': link.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def request_child_link(parent_id, student_email):
        """
        Request link to child by email
        
        Args:
            parent_id: Parent ID
            student_email: Student email address
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            # Find student by email
            user = User.query.filter_by(email=student_email).first()
            if not user:
                return {'success': False, 'error': 'Student not found'}, 404
            
            student = Student.query.filter_by(user_id=user.id).first()
            if not student:
                return {'success': False, 'error': 'Student not found'}, 404
            
            # Check if link already exists
            existing_link = ParentChildLink.query.filter_by(
                parent_id=parent_id,
                student_id=student.id,
                status='active'
            ).first()
            
            if existing_link:
                return {'success': False, 'error': 'Child already linked'}, 400
            
            # Check if request already exists
            existing_request = LinkRequest.query.filter_by(
                parent_id=parent_id,
                student_id=student.id,
                status='pending'
            ).first()
            
            if existing_request:
                return {'success': False, 'error': 'Link request already pending'}, 400
            
            # Create link request
            request = LinkRequest(
                parent_id=parent_id,
                student_id=student.id,
                request_type='email_request',
                status='pending'
            )
            db.session.add(request)
            db.session.commit()
            
            # TODO: Send notification to student
            
            return {
                'success': True,
                'request': request.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def approve_link_request(request_id, student_id):
        """
        Approve link request (student action)
        
        Args:
            request_id: Link request ID
            student_id: Student ID (for authorization)
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            request = LinkRequest.query.get(request_id)
            if not request:
                return {'success': False, 'error': 'Request not found'}, 404
            
            # Verify request belongs to student
            if request.student_id != student_id:
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Check if already processed
            if request.status != 'pending':
                return {'success': False, 'error': 'Request already processed'}, 400
            
            # Create link
            link = ParentChildLink(
                parent_id=request.parent_id,
                student_id=student_id,
                status='active'
            )
            db.session.add(link)
            
            # Update request
            request.status = 'approved'
            request.approved_at = datetime.utcnow()
            
            db.session.commit()
            
            # TODO: Send notification to parent
            
            return {
                'success': True,
                'link': link.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def reject_link_request(request_id, student_id):
        """
        Reject link request (student action)
        
        Args:
            request_id: Link request ID
            student_id: Student ID (for authorization)
        
        Returns:
            Tuple of (result dict, status code)
        """
        try:
            request = LinkRequest.query.get(request_id)
            if not request:
                return {'success': False, 'error': 'Request not found'}, 404
            
            # Verify request belongs to student
            if request.student_id != student_id:
                return {'success': False, 'error': 'Unauthorized'}, 403
            
            # Check if already processed
            if request.status != 'pending':
                return {'success': False, 'error': 'Request already processed'}, 400
            
            # Update request
            request.status = 'rejected'
            request.rejected_at = datetime.utcnow()
            
            db.session.commit()
            
            # TODO: Send notification to parent
            
            return {
                'success': True,
                'message': 'Link request rejected'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_linked_children(parent_id):
        """Get all linked children for parent"""
        try:
            links = ParentChildLink.query.filter_by(
                parent_id=parent_id,
                status='active'
            ).all()
            
            return {
                'success': True,
                'children': [link.to_dict() for link in links],
                'count': len(links)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def remove_child_link(parent_id, student_id):
        """Remove child link (parent-initiated)"""
        try:
            link = ParentChildLink.query.filter_by(
                parent_id=parent_id,
                student_id=student_id,
                status='active'
            ).first()
            
            if not link:
                return {'success': False, 'error': 'Link not found'}, 404
            
            # Update status instead of deleting
            link.status = 'removed'
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Child link removed'
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_pending_requests(student_id):
        """Get pending link requests for student"""
        try:
            requests = LinkRequest.query.filter_by(
                student_id=student_id,
                status='pending'
            ).all()
            
            return {
                'success': True,
                'requests': [req.to_dict() for req in requests],
                'count': len(requests)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

