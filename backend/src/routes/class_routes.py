"""
API routes for class groups.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.class_service import ClassService
from src.models.user import User
from src.models.student import Student

class_bp = Blueprint('class', __name__, url_prefix='/api/classes')


@class_bp.route('', methods=['POST'])
@jwt_required()
def create_class():
    """Create a new class (teacher/user)."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        name = data.get('name')
        description = data.get('description', '')
        grade_level = data.get('grade_level')

        if not name or not grade_level:
            return jsonify({'error': 'Name and grade_level are required'}), 400

        class_group = ClassService.create_class(
            teacher_id=user_id,
            name=name,
            description=description,
            grade_level=grade_level
        )

        return jsonify({
            'message': 'Class created successfully',
            'class': class_group.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create class'}), 500


@class_bp.route('', methods=['GET'])
@jwt_required()
def get_my_classes():
    """Get all classes for current user (as teacher or student)."""
    try:
        user_id = get_jwt_identity()

        # Get student profile
        user = User.query.get(user_id)
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404

        student_id = user.student.id

        # Get classes as student
        classes = ClassService.get_student_classes(student_id)

        # Also get classes as teacher
        from src.models.class_group import ClassGroup
        teacher_classes = ClassGroup.query.filter_by(teacher_id=user_id).all()
        for tc in teacher_classes:
            class_dict = tc.to_dict()
            class_dict['role'] = 'teacher'
            classes.append(class_dict)

        return jsonify({'classes': classes}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get classes'}), 500


@class_bp.route('/<int:class_id>', methods=['GET'])
@jwt_required()
def get_class(class_id):
    """Get class details."""
    try:
        class_group = ClassService.get_class(class_id)
        if not class_group:
            return jsonify({'error': 'Class not found'}), 404

        return jsonify({'class': class_group.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get class'}), 500


@class_bp.route('/<int:class_id>', methods=['PUT'])
@jwt_required()
def update_class(class_id):
    """Update class (teacher only)."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        class_group = ClassService.update_class(
            class_id=class_id,
            teacher_id=user_id,
            **data
        )

        return jsonify({
            'message': 'Class updated successfully',
            'class': class_group.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to update class'}), 500


@class_bp.route('/<int:class_id>', methods=['DELETE'])
@jwt_required()
def delete_class(class_id):
    """Delete class (teacher only)."""
    try:
        user_id = get_jwt_identity()
        ClassService.delete_class(class_id, user_id)

        return jsonify({'message': 'Class deleted successfully'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to delete class'}), 500


@class_bp.route('/join', methods=['POST'])
@jwt_required()
def join_class():
    """Join a class using invite code."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        invite_code = data.get('invite_code')
        if not invite_code:
            return jsonify({'error': 'Invite code is required'}), 400

        # Get student profile
        user = User.query.get(user_id)
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404

        student_id = user.student.id

        class_group = ClassService.join_class(student_id, invite_code)

        return jsonify({
            'message': 'Joined class successfully',
            'class': class_group.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to join class'}), 500


@class_bp.route('/<int:class_id>/leave', methods=['DELETE'])
@jwt_required()
def leave_class(class_id):
    """Leave a class."""
    try:
        user_id = get_jwt_identity()

        # Get student profile
        user = User.query.get(user_id)
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404

        student_id = user.student.id

        ClassService.leave_class(class_id, student_id)

        return jsonify({'message': 'Left class successfully'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to leave class'}), 500


@class_bp.route('/<int:class_id>/members/<int:student_id>', methods=['DELETE'])
@jwt_required()
def remove_member(class_id, student_id):
    """Remove a member from class (teacher only)."""
    try:
        user_id = get_jwt_identity()
        ClassService.remove_member(class_id, student_id, user_id)

        return jsonify({'message': 'Member removed successfully'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to remove member'}), 500


@class_bp.route('/<int:class_id>/members', methods=['GET'])
@jwt_required()
def get_members(class_id):
    """Get all members of a class."""
    try:
        members = ClassService.get_class_members(class_id)
        return jsonify({'members': members}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get members'}), 500


@class_bp.route('/<int:class_id>/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard(class_id):
    """Get class leaderboard."""
    try:
        leaderboard = ClassService.get_class_leaderboard(class_id)
        return jsonify({'leaderboard': leaderboard}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get leaderboard'}), 500


@class_bp.route('/<int:class_id>/stats', methods=['GET'])
@jwt_required()
def get_stats(class_id):
    """Get class statistics."""
    try:
        stats = ClassService.get_class_stats(class_id)
        return jsonify({'stats': stats}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get stats'}), 500

