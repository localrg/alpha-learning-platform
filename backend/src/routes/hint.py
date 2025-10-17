"""
Hint API routes for managing and requesting hints.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.models.user import User
from src.services.hint_service import HintService
from src.models.assessment import Question

hint_bp = Blueprint('hint', __name__, url_prefix='/api/hints')


@hint_bp.route('/question/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_hints(question_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    """Get all hints for a question."""
    try:
        hints = HintService.get_hints_for_question(question_id)
        
        return jsonify({
            'hints': hints,
            'total_hints': len(hints)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hint_bp.route('/request', methods=['POST'])
@jwt_required()
def request_hint():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    """Request the next hint for a question."""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        current_level = data.get('current_level', 0)
        attempt_number = data.get('attempt_number', 1)
        time_before_hint = data.get('time_before_hint')
        
        if not question_id:
            return jsonify({'error': 'question_id is required'}), 400
        
        # Get next hint
        hint_data = HintService.get_next_hint(question_id, current_level)
        
        if not hint_data:
            return jsonify({'error': 'No more hints available'}), 404
        
        # Record hint usage
        student = current_user.student
        if student:
            usage = HintService.record_hint_usage(
                student_id=student.id,
                question_id=question_id,
                hint_id=hint_data['hint']['id'],
                hint_level=hint_data['hint']['hint_level'],
                attempt_number=attempt_number,
                time_before_hint=time_before_hint
            )
            hint_data['usage_id'] = usage.id
        
        return jsonify(hint_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hint_bp.route('/usage/<int:usage_id>/feedback', methods=['PUT'])
@jwt_required()
def update_hint_feedback(usage_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    """Update hint usage with feedback."""
    try:
        data = request.get_json()
        helpful = data.get('helpful')
        answered_correctly = data.get('answered_correctly')
        attempts_after_hint = data.get('attempts_after_hint')
        
        usage = HintService.update_hint_feedback(
            usage_id=usage_id,
            helpful=helpful,
            answered_correctly=answered_correctly,
            attempts_after_hint=attempts_after_hint
        )
        
        if not usage:
            return jsonify({'error': 'Hint usage not found'}), 404
        
        return jsonify({
            'message': 'Feedback recorded',
            'usage': usage.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hint_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_student_stats():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    """Get hint usage statistics for the current student."""
    try:
        student = current_user.student
        if not student:
            return jsonify({'error': 'No student profile found'}), 404
        
        stats = HintService.get_student_hint_stats(student.id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hint_bp.route('/question/<int:question_id>/stats', methods=['GET'])
@jwt_required()
def get_question_stats(question_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    """Get hint usage statistics for a question."""
    try:
        stats = HintService.get_question_hint_stats(question_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hint_bp.route('/generate/<int:question_id>', methods=['POST'])
@jwt_required()
def generate_hints(question_id):
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    """
    Generate hints for a question automatically.
    This is typically used by teachers/admins.
    """
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Generate hints
        hints_data = HintService.generate_hints_for_question(question)
        
        # Create hints in database
        created_hints = HintService.create_hints_for_question(question_id, hints_data)
        
        return jsonify({
            'message': f'Generated {len(created_hints)} hints',
            'hints': [hint.to_dict() for hint in created_hints]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hint_bp.route('/create', methods=['POST'])
@jwt_required()
def create_custom_hint():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    """
    Create a custom hint for a question.
    This is typically used by teachers/admins.
    """
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        hints_data = data.get('hints', [])
        
        if not question_id or not hints_data:
            return jsonify({'error': 'question_id and hints are required'}), 400
        
        # Create hints
        created_hints = HintService.create_hints_for_question(question_id, hints_data)
        
        return jsonify({
            'message': f'Created {len(created_hints)} hints',
            'hints': [hint.to_dict() for hint in created_hints]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

