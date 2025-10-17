"""
API routes for parent-teacher communication.
"""
from flask import Blueprint, request, jsonify
from src.services.communication_service import CommunicationService

communication_bp = Blueprint('communication', __name__, url_prefix='/api/parent/messages')


@communication_bp.route('', methods=['POST'])
def send_message():
    """Send message from parent to teacher"""
    data = request.get_json()
    
    parent_id = data.get('parent_id')
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')
    subject = data.get('subject')
    message = data.get('message')
    message_type = data.get('message_type', 'question')
    
    if not all([parent_id, teacher_id, student_id, subject, message]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = CommunicationService.send_message(
        parent_id, teacher_id, student_id, subject, message, message_type
    )
    return jsonify(result), status


@communication_bp.route('/<int:message_id>/reply', methods=['POST'])
def reply_to_message(message_id):
    """Reply to a message"""
    data = request.get_json()
    
    parent_id = data.get('parent_id')
    reply_text = data.get('message')
    
    if not all([parent_id, reply_text]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = CommunicationService.reply_to_message(parent_id, message_id, reply_text)
    return jsonify(result), status


@communication_bp.route('', methods=['GET'])
def get_messages():
    """Get messages for parent"""
    parent_id = request.args.get('parent_id', type=int)
    filter_type = request.args.get('filter', default='all')
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    result, status = CommunicationService.get_messages(parent_id, filter_type)
    return jsonify(result), status


@communication_bp.route('/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """Get specific message with thread"""
    parent_id = request.args.get('parent_id', type=int)
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    result, status = CommunicationService.get_message(parent_id, message_id)
    return jsonify(result), status


@communication_bp.route('/<int:message_id>/read', methods=['PUT'])
def mark_as_read(message_id):
    """Mark message as read"""
    data = request.get_json()
    parent_id = data.get('parent_id')
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    result, status = CommunicationService.mark_as_read(parent_id, message_id)
    return jsonify(result), status


@communication_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """Get unread message count"""
    parent_id = request.args.get('parent_id', type=int)
    
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    result, status = CommunicationService.get_unread_count(parent_id)
    return jsonify(result), status

