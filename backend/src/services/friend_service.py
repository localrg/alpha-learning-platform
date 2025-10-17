"""
Friend service for managing friendships and friend requests.
"""
from src.database import db
from src.models.friendship import Friendship
from src.models.student import Student
from src.models.gamification import StudentProgress
from sqlalchemy import or_, and_


class FriendService:
    """Service for friend operations."""
    
    @staticmethod
    def send_request(requester_id, addressee_id):
        """Send a friend request."""
        # Validate
        if requester_id == addressee_id:
            raise ValueError("Cannot send friend request to yourself")
        
        # Check if already exists
        existing = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == requester_id, Friendship.addressee_id == addressee_id),
                and_(Friendship.requester_id == addressee_id, Friendship.addressee_id == requester_id)
            )
        ).first()
        
        if existing:
            if existing.status == 'accepted':
                raise ValueError("Already friends")
            elif existing.status == 'pending':
                raise ValueError("Friend request already pending")
        
        # Create request
        friendship = Friendship(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status='pending'
        )
        db.session.add(friendship)
        db.session.commit()
        
        return friendship
    
    @staticmethod
    def accept_request(friendship_id, student_id):
        """Accept a friend request."""
        friendship = Friendship.query.get(friendship_id)
        if not friendship:
            raise ValueError("Friend request not found")
        
        # Verify this student is the addressee
        if friendship.addressee_id != student_id:
            raise ValueError("Not authorized to accept this request")
        
        if friendship.status != 'pending':
            raise ValueError("Request is not pending")
        
        friendship.status = 'accepted'
        db.session.commit()
        
        return friendship
    
    @staticmethod
    def reject_request(friendship_id, student_id):
        """Reject a friend request."""
        friendship = Friendship.query.get(friendship_id)
        if not friendship:
            raise ValueError("Friend request not found")
        
        # Verify this student is the addressee
        if friendship.addressee_id != student_id:
            raise ValueError("Not authorized to reject this request")
        
        if friendship.status != 'pending':
            raise ValueError("Request is not pending")
        
        # Delete rejected requests
        db.session.delete(friendship)
        db.session.commit()
        
        return True
    
    @staticmethod
    def cancel_request(friendship_id, student_id):
        """Cancel a sent friend request."""
        friendship = Friendship.query.get(friendship_id)
        if not friendship:
            raise ValueError("Friend request not found")
        
        # Verify this student is the requester
        if friendship.requester_id != student_id:
            raise ValueError("Not authorized to cancel this request")
        
        if friendship.status != 'pending':
            raise ValueError("Request is not pending")
        
        db.session.delete(friendship)
        db.session.commit()
        
        return True
    
    @staticmethod
    def remove_friend(student_id, friend_id):
        """Remove a friend."""
        friendship = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == student_id, Friendship.addressee_id == friend_id),
                and_(Friendship.requester_id == friend_id, Friendship.addressee_id == student_id)
            ),
            Friendship.status == 'accepted'
        ).first()
        
        if not friendship:
            raise ValueError("Friendship not found")
        
        db.session.delete(friendship)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_friends(student_id):
        """Get all friends for a student."""
        friendships = Friendship.query.filter(
            or_(
                Friendship.requester_id == student_id,
                Friendship.addressee_id == student_id
            ),
            Friendship.status == 'accepted'
        ).all()
        
        friends = []
        for friendship in friendships:
            friend_id = friendship.addressee_id if friendship.requester_id == student_id else friendship.requester_id
            student = Student.query.get(friend_id)
            if student:
                # Get friend's progress
                progress = StudentProgress.query.filter_by(student_id=friend_id).first()
                name_parts = student.name.split(' ', 1)
                friends.append({
                    'id': student.id,
                    'first_name': name_parts[0] if name_parts else student.name,
                    'last_name': name_parts[1] if len(name_parts) > 1 else '',
                    'grade': student.grade,
                    'avatar': student.avatar if hasattr(student, 'avatar') else '😊',
                    'level': progress.current_level if progress else 1,
                    'xp': progress.total_xp if progress else 0,
                    'friendship_id': friendship.id,
                    'friend_since': friendship.updated_at.isoformat() if friendship.updated_at else None
                })
        
        return friends
    
    @staticmethod
    def get_received_requests(student_id):
        """Get pending friend requests received by this student."""
        requests = Friendship.query.filter_by(
            addressee_id=student_id,
            status='pending'
        ).all()
        
        result = []
        for request in requests:
            requester = Student.query.get(request.requester_id)
            if requester:
                progress = StudentProgress.query.filter_by(student_id=requester.id).first()
                name_parts = requester.name.split(' ', 1)
                result.append({
                    'id': request.id,
                    'requester': {
                        'id': requester.id,
                        'first_name': name_parts[0] if name_parts else requester.name,
                        'last_name': name_parts[1] if len(name_parts) > 1 else '',
                        'grade': requester.grade,
                        'avatar': requester.avatar if hasattr(requester, 'avatar') else '😊',
                        'level': progress.current_level if progress else 1
                    },
                    'created_at': request.created_at.isoformat() if request.created_at else None
                })
        
        return result
    
    @staticmethod
    def get_sent_requests(student_id):
        """Get pending friend requests sent by this student."""
        requests = Friendship.query.filter_by(
            requester_id=student_id,
            status='pending'
        ).all()
        
        result = []
        for request in requests:
            addressee = Student.query.get(request.addressee_id)
            if addressee:
                progress = StudentProgress.query.filter_by(student_id=addressee.id).first()
                name_parts = addressee.name.split(' ', 1)
                result.append({
                    'id': request.id,
                    'addressee': {
                        'id': addressee.id,
                        'first_name': name_parts[0] if name_parts else addressee.name,
                        'last_name': name_parts[1] if len(name_parts) > 1 else '',
                        'grade': addressee.grade,
                        'avatar': addressee.avatar if hasattr(addressee, 'avatar') else '😊',
                        'level': progress.current_level if progress else 1
                    },
                    'created_at': request.created_at.isoformat() if request.created_at else None
                })
        
        return result
    
    @staticmethod
    def search_students(query, current_student_id, limit=20):
        """Search for students by name."""
        students = Student.query.filter(
            Student.name.ilike(f'%{query}%'),
            Student.id != current_student_id
        ).limit(limit).all()
        
        result = []
        for student in students:
            # Check friendship status
            friendship = Friendship.query.filter(
                or_(
                    and_(Friendship.requester_id == current_student_id, Friendship.addressee_id == student.id),
                    and_(Friendship.requester_id == student.id, Friendship.addressee_id == current_student_id)
                )
            ).first()
            
            status = 'none'
            if friendship:
                if friendship.status == 'accepted':
                    status = 'friends'
                elif friendship.status == 'pending':
                    if friendship.requester_id == current_student_id:
                        status = 'request_sent'
                    else:
                        status = 'request_received'
            
            progress = StudentProgress.query.filter_by(student_id=student.id).first()
            name_parts = student.name.split(' ', 1)
            result.append({
                'id': student.id,
                'first_name': name_parts[0] if name_parts else student.name,
                'last_name': name_parts[1] if len(name_parts) > 1 else '',
                'grade': student.grade,
                'avatar': student.avatar if hasattr(student, 'avatar') else '😊',
                'level': progress.current_level if progress else 1,
                'friendship_status': status
            })
        
        return result
    
    @staticmethod
    def get_friend_count(student_id):
        """Get count of friends."""
        count = Friendship.query.filter(
            or_(
                Friendship.requester_id == student_id,
                Friendship.addressee_id == student_id
            ),
            Friendship.status == 'accepted'
        ).count()
        
        return count
    
    @staticmethod
    def are_friends(student_id1, student_id2):
        """Check if two students are friends."""
        friendship = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == student_id1, Friendship.addressee_id == student_id2),
                and_(Friendship.requester_id == student_id2, Friendship.addressee_id == student_id1)
            ),
            Friendship.status == 'accepted'
        ).first()
        
        return friendship is not None

