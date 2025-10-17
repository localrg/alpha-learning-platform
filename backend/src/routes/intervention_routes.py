"""
Intervention API Routes
"""
from flask import Blueprint, request, jsonify
from src.services.intervention_service import InterventionService

intervention_bp = Blueprint('interventions', __name__, url_prefix='/api/interventions')


@intervention_bp.route('/message', methods=['POST'])
def send_message():
    """Send message to student"""
    data = request.get_json()
    
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')
    message = data.get('message')
    template_id = data.get('template_id')
    
    if not all([teacher_id, student_id, message]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = InterventionService.send_message(teacher_id, student_id, message, template_id)
    return jsonify(result), status


@intervention_bp.route('/assignment', methods=['POST'])
def create_targeted_assignment():
    """Create targeted assignment for student"""
    data = request.get_json()
    
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')
    auto_fill = data.get('auto_fill', True)
    
    if not all([teacher_id, student_id]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = InterventionService.create_targeted_assignment(teacher_id, student_id, auto_fill)
    return jsonify(result), status


@intervention_bp.route('/meeting', methods=['POST'])
def schedule_meeting():
    """Schedule meeting with student"""
    data = request.get_json()
    
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')
    meeting_type = data.get('meeting_type')
    scheduled_at = data.get('scheduled_at')
    duration_minutes = data.get('duration_minutes', 30)
    location = data.get('location')
    notes = data.get('notes')
    
    if not all([teacher_id, student_id, meeting_type, scheduled_at]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = InterventionService.schedule_meeting(
        teacher_id, student_id, meeting_type, scheduled_at,
        duration_minutes, location, notes
    )
    return jsonify(result), status


@intervention_bp.route('/notify-parent', methods=['POST'])
def notify_parent():
    """Notify parent about student"""
    data = request.get_json()
    
    teacher_id = data.get('teacher_id')
    student_id = data.get('student_id')
    concern_type = data.get('concern_type')
    message = data.get('message')
    
    if not all([teacher_id, student_id, concern_type, message]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, status = InterventionService.notify_parent(teacher_id, student_id, concern_type, message)
    return jsonify(result), status


@intervention_bp.route('/<int:intervention_id>/resolve', methods=['PUT'])
def mark_resolved(intervention_id):
    """Mark intervention as resolved"""
    data = request.get_json()
    
    resolution_notes = data.get('resolution_notes')
    effectiveness_rating = data.get('effectiveness_rating')
    
    if not resolution_notes:
        return jsonify({'success': False, 'error': 'Resolution notes required'}), 400
    
    result, status = InterventionService.mark_intervention_resolved(
        intervention_id, resolution_notes, effectiveness_rating
    )
    return jsonify(result), status


@intervention_bp.route('/student/<int:student_id>', methods=['GET'])
def get_intervention_history(student_id):
    """Get intervention history for student"""
    teacher_id = request.args.get('teacher_id', type=int)
    
    result, status = InterventionService.get_intervention_history(student_id, teacher_id)
    return jsonify(result), status


@intervention_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get message templates"""
    category = request.args.get('category')
    
    result, status = InterventionService.get_message_templates(category)
    return jsonify(result), status


@intervention_bp.route('/templates/fill', methods=['POST'])
def fill_template():
    """Fill template with variables"""
    data = request.get_json()
    
    template_id = data.get('template_id')
    variables = data.get('variables', {})
    
    if not template_id:
        return jsonify({'success': False, 'error': 'Template ID required'}), 400
    
    result, status = InterventionService.fill_template(template_id, variables)
    return jsonify(result), status


@intervention_bp.route('/templates/create-defaults', methods=['POST'])
def create_default_templates():
    """Create default message templates"""
    result, status = InterventionService.create_default_templates()
    return jsonify(result), status

