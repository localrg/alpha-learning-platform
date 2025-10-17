"""
API routes for goal setting and tracking.
"""
from flask import Blueprint, request, jsonify
from src.services.goal_service import GoalService
from datetime import datetime

goal_bp = Blueprint('goals', __name__, url_prefix='/api/goals')


@goal_bp.route('', methods=['POST'])
def create_goal():
    """Create a new goal"""
    data = request.get_json()
    
    student_id = data.get('student_id')
    created_by_id = data.get('created_by_id')
    created_by_type = data.get('created_by_type')
    goal_type = data.get('goal_type')
    title = data.get('title')
    description = data.get('description', '')
    target_value = data.get('target_value')
    due_date_str = data.get('due_date')
    skill_id = data.get('skill_id')
    
    if not all([student_id, created_by_id, created_by_type, goal_type, title, target_value]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Parse due_date if provided
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str)
        except:
            return jsonify({'success': False, 'error': 'Invalid due_date format'}), 400
    
    result, status = GoalService.create_goal(
        student_id, created_by_id, created_by_type, goal_type,
        title, description, target_value, due_date, skill_id
    )
    return jsonify(result), status


@goal_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_goals(student_id):
    """Get goals for a student"""
    status = request.args.get('status', default='all')
    
    result, status_code = GoalService.get_student_goals(student_id, status)
    return jsonify(result), status_code


@goal_bp.route('/<int:goal_id>', methods=['GET'])
def get_goal(goal_id):
    """Get specific goal"""
    result, status = GoalService.get_goal(goal_id)
    return jsonify(result), status


@goal_bp.route('/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    """Update goal"""
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    target_value = data.get('target_value')
    due_date_str = data.get('due_date')
    
    # Parse due_date if provided
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str)
        except:
            return jsonify({'success': False, 'error': 'Invalid due_date format'}), 400
    
    result, status = GoalService.update_goal(goal_id, title, description, target_value, due_date)
    return jsonify(result), status


@goal_bp.route('/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    """Delete goal"""
    result, status = GoalService.delete_goal(goal_id)
    return jsonify(result), status


@goal_bp.route('/<int:goal_id>/notes', methods=['POST'])
def add_note(goal_id):
    """Add note to goal"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    user_type = data.get('user_type')
    note = data.get('note')
    
    if not all([user_id, user_type, note]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = GoalService.add_note(goal_id, user_id, user_type, note)
    return jsonify(result), status


@goal_bp.route('/<int:goal_id>/progress', methods=['POST'])
def add_progress(goal_id):
    """Add manual progress update"""
    data = request.get_json()
    
    value = data.get('value')
    note = data.get('note')
    
    if value is None:
        return jsonify({'success': False, 'error': 'value required'}), 400
    
    result, status = GoalService.add_manual_progress(goal_id, value, note)
    return jsonify(result), status

