"""
Parent View API Routes
Routes for parents to view child progress
"""
from flask import Blueprint, request, jsonify
from src.services.parent_view_service import ParentViewService

parent_view_bp = Blueprint('parent_view', __name__, url_prefix='/api/parents/children')


@parent_view_bp.route('/<int:student_id>/overview', methods=['GET'])
def get_child_overview(student_id):
    """Get child overview dashboard"""
    parent_id = request.args.get('parent_id', type=int)
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'Parent ID required'}), 400
    
    result, status = ParentViewService.get_child_overview(parent_id, student_id)
    return jsonify(result), status


@parent_view_bp.route('/<int:student_id>/skills', methods=['GET'])
def get_child_skills(student_id):
    """Get child skill progress"""
    parent_id = request.args.get('parent_id', type=int)
    filter_type = request.args.get('filter', 'all')
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'Parent ID required'}), 400
    
    result, status = ParentViewService.get_child_skills(parent_id, student_id, filter_type)
    return jsonify(result), status


@parent_view_bp.route('/<int:student_id>/activity', methods=['GET'])
def get_child_activity(student_id):
    """Get child activity feed"""
    parent_id = request.args.get('parent_id', type=int)
    days = request.args.get('days', 30, type=int)
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'Parent ID required'}), 400
    
    result, status = ParentViewService.get_child_activity(parent_id, student_id, days)
    return jsonify(result), status


@parent_view_bp.route('/<int:student_id>/assignments', methods=['GET'])
def get_child_assignments(student_id):
    """Get child assignments"""
    parent_id = request.args.get('parent_id', type=int)
    filter_type = request.args.get('filter', 'all')
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'Parent ID required'}), 400
    
    result, status = ParentViewService.get_child_assignments(parent_id, student_id, filter_type)
    return jsonify(result), status


@parent_view_bp.route('/<int:student_id>/achievements', methods=['GET'])
def get_child_achievements(student_id):
    """Get child achievements"""
    parent_id = request.args.get('parent_id', type=int)
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'Parent ID required'}), 400
    
    result, status = ParentViewService.get_child_achievements(parent_id, student_id)
    return jsonify(result), status

