"""
Authentication middleware for protecting routes.
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from src.database import db
from src.models.user import User


def token_required(f):
    """
    Decorator to require a valid JWT token for a route.
    Adds the current user to the function arguments.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = db.session.get(User, current_user_id)
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 404
            
            return f(current_user=current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token'}), 401
    
    return decorated


def role_required(*roles):
    """
    Decorator to require specific user roles for a route.
    Usage: @role_required('admin', 'teacher')
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                current_user = db.session.get(User, current_user_id)
                
                if not current_user:
                    return jsonify({'error': 'User not found'}), 404
                
                if current_user.role not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(current_user=current_user, *args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Invalid or expired token'}), 401
        
        return decorated
    return decorator

