"""
Solution API routes for managing and viewing worked solutions.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.models.user import User
from src.models.assessment import Question
from src.services.solution_service import SolutionService

solution_bp = Blueprint('solution', __name__, url_prefix='/api/solutions')


@solution_bp.route('/question/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_solution(question_id):
    """Get the worked solution for a question."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        student = current_user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Check eligibility
        eligible, attempts_made, attempts_required = SolutionService.is_eligible_for_solution(
            student.id, 
            question_id
        )
        
        # Get solution
        solution = SolutionService.get_solution_for_question(question_id)
        
        if not solution:
            return jsonify({'error': 'No solution available for this question'}), 404
        
        return jsonify({
            'solution': solution,
            'eligible': eligible,
            'attempts_made': attempts_made,
            'attempts_required': attempts_required
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@solution_bp.route('/view', methods=['POST'])
@jwt_required()
def record_view():
    """Record that a student viewed a solution."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        solution_id = data.get('solution_id')
        time_spent = data.get('time_spent_seconds')
        steps_viewed = data.get('steps_viewed', [])
        
        if not question_id or not solution_id:
            return jsonify({'error': 'question_id and solution_id are required'}), 400
        
        student = current_user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Record view
        view = SolutionService.record_solution_view(
            student_id=student.id,
            question_id=question_id,
            solution_id=solution_id,
            time_spent=time_spent,
            steps_viewed=steps_viewed
        )
        
        return jsonify({
            'view_id': view.id,
            'message': 'Solution view recorded'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@solution_bp.route('/view/<int:view_id>/feedback', methods=['PUT'])
@jwt_required()
def update_feedback(view_id):
    """Update feedback for a solution view."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        data = request.get_json()
        helpful = data.get('helpful')
        understood = data.get('understood')
        
        # Update feedback
        view = SolutionService.update_solution_feedback(
            view_id=view_id,
            helpful=helpful,
            understood=understood
        )
        
        if not view:
            return jsonify({'error': 'Solution view not found'}), 404
        
        return jsonify({
            'message': 'Feedback recorded',
            'view': view.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@solution_bp.route('/generate/<int:question_id>', methods=['POST'])
@jwt_required()
def generate_solution(question_id):
    """Generate a worked solution for a question."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Generate solution
        solution_data = SolutionService.generate_solution_for_question(question)
        
        # Create solution in database
        solution = SolutionService.create_solution(question_id, solution_data)
        
        return jsonify({
            'message': 'Solution generated successfully',
            'solution': solution.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@solution_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_student_stats():
    """Get solution viewing statistics for the current student."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        student = current_user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        stats = SolutionService.get_student_solution_stats(student.id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@solution_bp.route('/question/<int:question_id>/stats', methods=['GET'])
@jwt_required()
def get_question_stats(question_id):
    """Get solution viewing statistics for a question."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        stats = SolutionService.get_question_solution_stats(question_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

