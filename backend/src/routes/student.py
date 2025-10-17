"""
Student profile routes for creating and managing student information.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.user import User
from src.models.student import Student

student_bp = Blueprint('student', __name__)


@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_student_profile():
    """
    Get the current user's student profile.
    
    Returns:
        200: Student profile
        404: No student profile found
    """
    try:
        current_user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=current_user_id).first()
        
        if not student:
            return jsonify({'error': 'No student profile found'}), 404
        
        return jsonify({
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500


@student_bp.route('/profile', methods=['POST'])
@jwt_required()
def create_student_profile():
    """
    Create a student profile for the current user.
    
    Expected JSON body:
    {
        "name": "string (required, 1-100 chars)",
        "grade": "integer (required, 3-8)"
    }
    
    Returns:
        201: Student profile created
        400: Invalid input
        409: Profile already exists
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Check if profile already exists
        existing_student = Student.query.filter_by(user_id=current_user_id).first()
        if existing_student:
            return jsonify({'error': 'Student profile already exists'}), 409
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        grade = data.get('grade')
        
        # Validate name
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if len(name) < 1:
            return jsonify({'error': 'Name must be at least 1 character'}), 400
        if len(name) > 100:
            return jsonify({'error': 'Name must be at most 100 characters'}), 400
        
        # Validate grade
        if grade is None:
            return jsonify({'error': 'Grade is required'}), 400
        
        try:
            grade = int(grade)
        except (ValueError, TypeError):
            return jsonify({'error': 'Grade must be a number'}), 400
        
        if grade < 3 or grade > 8:
            return jsonify({'error': 'Grade must be between 3 and 8'}), 400
        
        # Create student profile
        student = Student(
            user_id=current_user_id,
            name=name,
            grade=grade
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student profile created successfully',
            'student': student.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create profile: {str(e)}'}), 500


@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_student_profile():
    """
    Update the current user's student profile.
    
    Expected JSON body:
    {
        "name": "string (optional, 1-100 chars)",
        "grade": "integer (optional, 3-8)"
    }
    
    Returns:
        200: Profile updated
        400: Invalid input
        404: No profile found
    """
    try:
        current_user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=current_user_id).first()
        
        if not student:
            return jsonify({'error': 'No student profile found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update name if provided
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': 'Name cannot be empty'}), 400
            if len(name) > 100:
                return jsonify({'error': 'Name must be at most 100 characters'}), 400
            student.name = name
        
        # Update grade if provided
        if 'grade' in data:
            try:
                grade = int(data['grade'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Grade must be a number'}), 400
            
            if grade < 3 or grade > 8:
                return jsonify({'error': 'Grade must be between 3 and 8'}), 400
            student.grade = grade
        
        db.session.commit()
        
        return jsonify({
            'message': 'Student profile updated successfully',
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500


@student_bp.route('/profile', methods=['DELETE'])
@jwt_required()
def delete_student_profile():
    """
    Delete the current user's student profile.
    
    Returns:
        200: Profile deleted
        404: No profile found
    """
    try:
        current_user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=current_user_id).first()
        
        if not student:
            return jsonify({'error': 'No student profile found'}), 404
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student profile deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete profile: {str(e)}'}), 500

