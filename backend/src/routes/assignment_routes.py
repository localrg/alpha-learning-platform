"""
Assignment Routes
API endpoints for teacher-created assignments
"""
from flask import Blueprint, request, jsonify
from src.middleware.auth import token_required
from src.services.assignment_service import AssignmentService

assignment_routes_bp = Blueprint('assignment_routes', __name__, url_prefix='/api/assignments')


@assignment_routes_bp.route('', methods=['POST'])
@token_required
def create_assignment(current_user):
    """Create new assignment"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can create assignments'}), 403
    
    data = request.get_json()
    result, status = AssignmentService.create_assignment(current_user.id, data)
    return jsonify(result), status


@assignment_routes_bp.route('', methods=['GET'])
@token_required
def get_assignments(current_user):
    """Get assignments (filtered by role)"""
    # Get filter parameters
    filters = {
        'class_id': request.args.get('class_id', type=int),
        'status': request.args.get('status')
    }
    
    if current_user.role == 'teacher':
        # Get teacher's assignments
        assignments = AssignmentService.get_teacher_assignments(current_user.id, filters)
        return jsonify({'success': True, 'assignments': assignments}), 200
    else:
        # Get student's assignments
        # Find student ID from user
        if not hasattr(current_user, 'student') or not current_user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        student_id = current_user.student[0].id
        assignments = AssignmentService.get_student_assignments(student_id, filters)
        return jsonify({'success': True, 'assignments': assignments}), 200


@assignment_routes_bp.route('/<int:assignment_id>', methods=['GET'])
@token_required
def get_assignment(current_user, assignment_id):
    """Get assignment details"""
    result, status = AssignmentService.get_assignment(assignment_id, current_user.id, current_user.role)
    return jsonify(result), status


@assignment_routes_bp.route('/<int:assignment_id>', methods=['PUT'])
@token_required
def update_assignment(current_user, assignment_id):
    """Update assignment"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can update assignments'}), 403
    
    data = request.get_json()
    result, status = AssignmentService.update_assignment(assignment_id, current_user.id, data)
    return jsonify(result), status


@assignment_routes_bp.route('/<int:assignment_id>', methods=['DELETE'])
@token_required
def delete_assignment(current_user, assignment_id):
    """Delete assignment"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can delete assignments'}), 403
    
    result, status = AssignmentService.delete_assignment(assignment_id, current_user.id)
    return jsonify(result), status


@assignment_routes_bp.route('/<int:assignment_id>/start', methods=['POST'])
@token_required
def start_assignment(current_user, assignment_id):
    """Start assignment (student)"""
    if current_user.role == 'teacher':
        return jsonify({'error': 'Teachers cannot start assignments'}), 403
    
    # Find student ID
    if not hasattr(current_user, 'student') or not current_user.student:
        return jsonify({'error': 'Student not found'}), 404
    
    student_id = current_user.student[0].id
    result, status = AssignmentService.start_assignment(assignment_id, student_id)
    return jsonify(result), status


@assignment_routes_bp.route('/<int:assignment_id>/complete', methods=['POST'])
@token_required
def complete_assignment(current_user, assignment_id):
    """Complete assignment (student)"""
    if current_user.role == 'teacher':
        return jsonify({'error': 'Teachers cannot complete assignments'}), 403
    
    # Find student ID
    if not hasattr(current_user, 'student') or not current_user.student:
        return jsonify({'error': 'Student not found'}), 404
    
    student_id = current_user.student[0].id
    result, status = AssignmentService.complete_assignment(assignment_id, student_id)
    return jsonify(result), status


@assignment_routes_bp.route('/<int:assignment_id>/stats', methods=['GET'])
@token_required
def get_assignment_stats(current_user, assignment_id):
    """Get assignment statistics (teacher)"""
    if current_user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view stats'}), 403
    
    stats = AssignmentService.get_assignment_stats(assignment_id, current_user.id)
    return jsonify({'success': True, 'stats': stats}), 200


@assignment_routes_bp.route('/<int:assignment_id>/progress', methods=['GET'])
@token_required
def get_assignment_progress(current_user, assignment_id):
    """Get student progress (student)"""
    if current_user.role == 'teacher':
        return jsonify({'error': 'Use /stats endpoint for teacher view'}), 403
    
    # Find student ID
    if not hasattr(current_user, 'student') or not current_user.student:
        return jsonify({'error': 'Student not found'}), 404
    
    student_id = current_user.student[0].id
    result, status = AssignmentService.get_student_assignment_progress(assignment_id, student_id)
    return jsonify(result), status

