"""
API routes for student profiles.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.profile_service import ProfileService

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profiles')


@profile_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required(optional=True)
def get_profile(student_id):
    """Get student profile."""
    try:
        # Get viewer ID if authenticated
        viewer_id = None
        try:
            viewer_id = get_jwt_identity()
        except:
            pass
        
        profile = ProfileService.get_profile(student_id, viewer_id)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        if 'error' in profile:
            return jsonify(profile), 403
        
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Get own profile."""
    try:
        user_id = get_jwt_identity()
        student_id = user_id  # Assume user_id == student_id
        
        profile = ProfileService.get_profile(student_id, student_id)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    """Update own profile."""
    try:
        user_id = get_jwt_identity()
        student_id = user_id
        
        data = request.get_json()
        
        profile = ProfileService.update_profile(student_id, **data)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

