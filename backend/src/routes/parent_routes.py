"""
Parent API Routes
"""
from flask import Blueprint, request, jsonify
from src.services.parent_service import ParentService

parent_bp = Blueprint('parents', __name__, url_prefix='/api/parents')


@parent_bp.route('/register', methods=['POST'])
def register_parent():
    """Create parent account"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    notification_prefs = data.get('notification_preferences')
    
    if not all([user_id, name, email]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = ParentService.create_parent_account(
        user_id, name, email, phone, notification_prefs
    )
    return jsonify(result), status


@parent_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get parent profile"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'success': False, 'error': 'User ID required'}), 400
    
    result, status = ParentService.get_parent_by_user_id(user_id)
    return jsonify(result), status


@parent_bp.route('/profile/<int:parent_id>', methods=['PUT'])
def update_profile(parent_id):
    """Update parent profile"""
    data = request.get_json()
    
    name = data.get('name')
    phone = data.get('phone')
    
    result, status = ParentService.update_parent_profile(parent_id, name, phone)
    return jsonify(result), status


@parent_bp.route('/notifications/<int:parent_id>', methods=['PUT'])
def update_notifications(parent_id):
    """Update notification preferences"""
    data = request.get_json()
    
    preferences = data.get('preferences')
    
    if not preferences:
        return jsonify({'success': False, 'error': 'Preferences required'}), 400
    
    result, status = ParentService.update_notification_preferences(parent_id, preferences)
    return jsonify(result), status


@parent_bp.route('/link-child', methods=['POST'])
def link_child():
    """Link child by invite code"""
    data = request.get_json()
    
    parent_id = data.get('parent_id')
    invite_code = data.get('invite_code')
    
    if not all([parent_id, invite_code]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = ParentService.link_child_by_code(parent_id, invite_code)
    return jsonify(result), status


@parent_bp.route('/request-link', methods=['POST'])
def request_link():
    """Request link to child by email"""
    data = request.get_json()
    
    parent_id = data.get('parent_id')
    student_email = data.get('student_email')
    
    if not all([parent_id, student_email]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = ParentService.request_child_link(parent_id, student_email)
    return jsonify(result), status


@parent_bp.route('/children', methods=['GET'])
def get_children():
    """Get all linked children"""
    parent_id = request.args.get('parent_id', type=int)
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'Parent ID required'}), 400
    
    result, status = ParentService.get_linked_children(parent_id)
    return jsonify(result), status


@parent_bp.route('/children/<int:student_id>', methods=['DELETE'])
def remove_child(student_id):
    """Remove child link"""
    parent_id = request.args.get('parent_id', type=int)
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'Parent ID required'}), 400
    
    result, status = ParentService.remove_child_link(parent_id, student_id)
    return jsonify(result), status


@parent_bp.route('/link-requests', methods=['GET'])
def get_link_requests():
    """Get pending link requests (for students)"""
    student_id = request.args.get('student_id', type=int)
    
    if not student_id:
        return jsonify({'success': False, 'error': 'Student ID required'}), 400
    
    result, status = ParentService.get_pending_requests(student_id)
    return jsonify(result), status


@parent_bp.route('/link-requests/<int:request_id>/approve', methods=['POST'])
def approve_request(request_id):
    """Approve link request"""
    data = request.get_json()
    
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'success': False, 'error': 'Student ID required'}), 400
    
    result, status = ParentService.approve_link_request(request_id, student_id)
    return jsonify(result), status


@parent_bp.route('/link-requests/<int:request_id>/reject', methods=['POST'])
def reject_request(request_id):
    """Reject link request"""
    data = request.get_json()
    
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'success': False, 'error': 'Student ID required'}), 400
    
    result, status = ParentService.reject_link_request(request_id, student_id)
    return jsonify(result), status


@parent_bp.route('/generate-invite', methods=['POST'])
def generate_invite():
    """Generate parent invite code (for students)"""
    data = request.get_json()
    
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'success': False, 'error': 'Student ID required'}), 400
    
    result, status = ParentService.generate_invite_code(student_id)
    return jsonify(result), status

