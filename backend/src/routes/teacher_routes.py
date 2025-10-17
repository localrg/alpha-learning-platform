"""
Teacher Routes
API endpoints for teacher dashboard and management
"""

from flask import Blueprint, request, jsonify
from src.middleware.auth import token_required
from src.services.teacher_service import TeacherService

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')


@teacher_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard(current_user):
    """Get teacher dashboard data"""
    # Verify user is a teacher
    if current_user.role != 'teacher':
        return jsonify({'error': 'Not authorized'}), 403
    
    result, status = TeacherService.get_dashboard_data(current_user.id)
    return jsonify(result), status


@teacher_bp.route('/class/<int:class_id>/overview', methods=['GET'])
@token_required
def get_class_overview(current_user, class_id):
    """Get detailed class overview"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Not authorized'}), 403
    
    result, status = TeacherService.get_class_overview(class_id, current_user.id)
    return jsonify(result), status


@teacher_bp.route('/student/<int:student_id>/summary', methods=['GET'])
@token_required
def get_student_summary(current_user, student_id):
    """Get detailed student summary"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Not authorized'}), 403
    
    result, status = TeacherService.get_student_summary(student_id, current_user.id)
    return jsonify(result), status


@teacher_bp.route('/class/<int:class_id>/metrics', methods=['GET'])
@token_required
def get_class_metrics(current_user, class_id):
    """Get class metrics"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Not authorized'}), 403
    
    metrics = TeacherService.get_class_metrics(class_id)
    return jsonify({'success': True, 'metrics': metrics}), 200


@teacher_bp.route('/stats', methods=['GET'])
@token_required
def get_teacher_stats(current_user):
    """Get teacher statistics"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Not authorized'}), 403
    
    stats = TeacherService.get_teacher_stats(current_user.id)
    return jsonify({'success': True, 'stats': stats}), 200

