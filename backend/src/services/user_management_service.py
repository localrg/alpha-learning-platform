"""
User Management Service for admin user operations.
"""
from src.database import db
from src.models.user import User
from src.models.student import Student
from src.models.admin_models import AuditLog
from datetime import datetime
import json


class UserManagementService:
    """Service for managing users"""
    
    @staticmethod
    def create_user(admin_id, data):
        """Create a new user"""
        try:
            # Validate required fields
            if not data.get('username') or not data.get('email') or not data.get('password'):
                return {'success': False, 'error': 'Missing required fields'}, 400
            
            # Check if username or email already exists
            if User.query.filter_by(username=data['username']).first():
                return {'success': False, 'error': 'Username already exists'}, 400
            
            if User.query.filter_by(email=data['email']).first():
                return {'success': False, 'error': 'Email already exists'}, 400
            
            # Create user
            user = User(
                username=data['username'],
                email=data['email'],
                role=data.get('role', 'student')
            )
            user.set_password(data['password'])
            db.session.add(user)
            db.session.flush()
            
            # If student, create student profile
            if user.role == 'student' and data.get('name'):
                student = Student(
                    user_id=user.id,
                    name=data['name'],
                    grade=data.get('grade', 1)
                )
                db.session.add(student)
            
            # Log action
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type='create',
                entity_type='user',
                entity_id=user.id,
                after_value=json.dumps({'username': user.username, 'email': user.email, 'role': user.role}),
                description=f'Created user {user.username}'
            )
            db.session.add(audit_log)
            
            db.session.commit()
            
            return {'success': True, 'user_id': user.id, 'message': 'User created successfully'}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def update_user(admin_id, user_id, data):
        """Update user information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}, 404
            
            # Store before value
            before_value = {
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
            
            # Update fields
            if 'email' in data:
                # Check if email is already taken by another user
                existing = User.query.filter_by(email=data['email']).first()
                if existing and existing.id != user_id:
                    return {'success': False, 'error': 'Email already in use'}, 400
                user.email = data['email']
            
            if 'role' in data:
                user.role = data['role']
            
            # Store after value
            after_value = {
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
            
            # Log action
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type='update',
                entity_type='user',
                entity_id=user.id,
                before_value=json.dumps(before_value),
                after_value=json.dumps(after_value),
                description=f'Updated user {user.username}'
            )
            db.session.add(audit_log)
            
            db.session.commit()
            
            return {'success': True, 'message': 'User updated successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def delete_user(admin_id, user_id):
        """Delete a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}, 404
            
            # Store user info for audit log
            user_info = {
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
            
            # Log action before deletion
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type='delete',
                entity_type='user',
                entity_id=user.id,
                before_value=json.dumps(user_info),
                description=f'Deleted user {user.username}'
            )
            db.session.add(audit_log)
            
            # Delete related student record first if exists
            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    db.session.delete(student)
            
            # Delete user
            db.session.delete(user)
            db.session.commit()
            
            return {'success': True, 'message': 'User deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def search_users(query=None, role=None, limit=50):
        """Search and filter users"""
        try:
            # Start with base query
            users_query = User.query
            
            # Apply filters
            if query:
                users_query = users_query.filter(
                    (User.username.ilike(f'%{query}%')) |
                    (User.email.ilike(f'%{query}%'))
                )
            
            if role:
                users_query = users_query.filter_by(role=role)
            
            # Limit results
            users = users_query.limit(limit).all()
            
            # Convert to dict
            users_data = [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'role': u.role,
                    'created_at': u.created_at.isoformat() if u.created_at else None
                }
                for u in users
            ]
            
            return {'success': True, 'users': users_data, 'count': len(users_data)}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_user_details(user_id):
        """Get detailed user information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}, 404
            
            details = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            
            # Add role-specific details
            if user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    details['student_info'] = {
                        'name': student.name,
                        'grade': student.grade
                    }
            
            return {'success': True, 'user': details}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

