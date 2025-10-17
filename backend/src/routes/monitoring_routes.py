"""
Monitoring Routes
API endpoints for student monitoring and real-time tracking
"""
from flask import Blueprint, request, jsonify
from src.middleware.auth import token_required
from src.services.monitoring_service import MonitoringService

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')


@monitoring_bp.route('/class/<int:class_id>', methods=['GET'])
@token_required
def get_class_monitoring(current_user, class_id):
    """Get class monitoring dashboard"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can monitor classes'}), 403
    
    result, status = MonitoringService.get_class_monitoring_data(class_id, current_user.id)
    return jsonify(result), status


@monitoring_bp.route('/class/<int:class_id>/active', methods=['GET'])
@token_required
def get_active_students(current_user, class_id):
    """Get currently active students"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view active students'}), 403
    
    active_students = MonitoringService.get_active_students(class_id)
    return jsonify({'success': True, 'active_students': active_students}), 200


@monitoring_bp.route('/class/<int:class_id>/struggling', methods=['GET'])
@token_required
def get_struggling_students(current_user, class_id):
    """Get struggling students"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view struggling students'}), 403
    
    threshold = request.args.get('threshold', 0.7, type=float)
    struggling = MonitoringService.get_struggling_students(class_id, threshold)
    return jsonify({'success': True, 'struggling_students': struggling}), 200


@monitoring_bp.route('/class/<int:class_id>/inactive', methods=['GET'])
@token_required
def get_inactive_students(current_user, class_id):
    """Get inactive students"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view inactive students'}), 403
    
    days = request.args.get('days', 7, type=int)
    inactive = MonitoringService.get_inactive_students(class_id, days)
    return jsonify({'success': True, 'inactive_students': inactive}), 200


@monitoring_bp.route('/class/<int:class_id>/alerts', methods=['GET'])
@token_required
def get_class_alerts(current_user, class_id):
    """Get class alerts"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view alerts'}), 403
    
    alerts = MonitoringService.get_class_alerts(class_id, current_user.id)
    return jsonify({'success': True, 'alerts': alerts}), 200


@monitoring_bp.route('/class/<int:class_id>/compliance', methods=['GET'])
@token_required
def get_assignment_compliance(current_user, class_id):
    """Get assignment compliance"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view compliance'}), 403
    
    compliance = MonitoringService.get_assignment_compliance(class_id)
    return jsonify({'success': True, 'compliance': compliance}), 200


@monitoring_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_monitoring(current_user, student_id):
    """Get student monitoring details"""
    # Teachers can view any student, students can only view themselves
    if current_user.role == 'student':
        if not hasattr(current_user, 'student') or not current_user.student:
            return jsonify({'error': 'Student not found'}), 404
        if current_user.student[0].id != student_id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    status_data = MonitoringService.get_student_status(student_id)
    timeline = MonitoringService.get_student_activity_timeline(student_id)
    current_session = MonitoringService.get_student_current_session(student_id)
    
    return jsonify({
        'success': True,
        'status': status_data,
        'timeline': timeline,
        'current_session': current_session
    }), 200


@monitoring_bp.route('/student/<int:student_id>/timeline', methods=['GET'])
@token_required
def get_student_timeline(current_user, student_id):
    """Get student activity timeline"""
    days = request.args.get('days', 7, type=int)
    timeline = MonitoringService.get_student_activity_timeline(student_id, days)
    return jsonify({'success': True, 'timeline': timeline}), 200


@monitoring_bp.route('/session/start', methods=['POST'])
@token_required
def start_session(current_user):
    """Start practice session"""
    if current_user.role == 'teacher':
        return jsonify({'error': 'Teachers cannot start practice sessions'}), 403
    
    # Find student ID
    if not hasattr(current_user, 'student') or not current_user.student:
        return jsonify({'error': 'Student not found'}), 404
    
    student_id = current_user.student[0].id
    data = request.get_json() or {}
    skill_id = data.get('skill_id')
    
    result, status = MonitoringService.start_session(student_id, skill_id)
    return jsonify(result), status


@monitoring_bp.route('/session/activity', methods=['POST'])
@token_required
def track_activity(current_user):
    """Track session activity"""
    if current_user.role == 'teacher':
        return jsonify({'error': 'Teachers cannot track activity'}), 403
    
    # Find student ID
    if not hasattr(current_user, 'student') or not current_user.student:
        return jsonify({'error': 'Student not found'}), 404
    
    student_id = current_user.student[0].id
    data = request.get_json()
    
    if not data or 'question_id' not in data or 'correct' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    skill_id = data.get('skill_id')
    question_id = data['question_id']
    correct = data['correct']
    
    result, status = MonitoringService.track_session_activity(student_id, skill_id, question_id, correct)
    return jsonify(result), status


@monitoring_bp.route('/session/<int:session_id>/end', methods=['POST'])
@token_required
def end_session(current_user, session_id):
    """End practice session"""
    if current_user.role == 'teacher':
        return jsonify({'error': 'Teachers cannot end sessions'}), 403
    
    result, status = MonitoringService.end_session(session_id)
    return jsonify(result), status

