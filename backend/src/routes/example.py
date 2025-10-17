"""
Example API routes for managing interactive examples and tracking interactions.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.models.interactive_example import InteractiveExample
from src.services.example_service import ExampleService

bp = Blueprint('example', __name__, url_prefix='/api/examples')


@bp.route('/skill/<int:skill_id>', methods=['GET'])
@jwt_required()
def get_skill_examples(skill_id):
    """Get all interactive examples for a specific skill."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get examples for skill
        examples = ExampleService.get_examples_for_skill(skill_id, student_id=student.id)
        
        return jsonify({
            'examples': examples,
            'total': len(examples)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:example_id>', methods=['GET'])
@jwt_required()
def get_example(example_id):
    """Get details for a specific interactive example."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get example
        example = ExampleService.get_example_by_id(example_id, student_id=student.id)
        
        if not example:
            return jsonify({'error': 'Example not found'}), 404
        
        return jsonify(example), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:example_id>/start', methods=['POST'])
@jwt_required()
def start_example(example_id):
    """Record that a student started an interactive example."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Check if example exists
        example = InteractiveExample.query.get(example_id)
        if not example:
            return jsonify({'error': 'Example not found'}), 404
        
        # Start interaction
        interaction = ExampleService.start_interaction(example_id, student.id)
        
        return jsonify({
            'message': 'Interaction started',
            'interaction_id': interaction.id,
            'interaction': interaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/interaction/<int:interaction_id>/log', methods=['POST'])
@jwt_required()
def log_action(interaction_id):
    """Log a student interaction action."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Validate input
        if 'action' not in data:
            return jsonify({'error': 'Missing action data'}), 400
        
        # Log interaction
        interaction = ExampleService.log_interaction(interaction_id, data['action'])
        
        if not interaction:
            return jsonify({'error': 'Interaction not found'}), 404
        
        return jsonify({
            'message': 'Action logged',
            'interaction': interaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/interaction/<int:interaction_id>/time', methods=['PUT'])
@jwt_required()
def update_time(interaction_id):
    """Update time spent on an example."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Validate input
        time_spent = data.get('time_spent_seconds', 0)
        if not isinstance(time_spent, (int, float)) or time_spent < 0:
            return jsonify({'error': 'Invalid time_spent_seconds'}), 400
        
        # Update time
        interaction = ExampleService.update_time_spent(interaction_id, int(time_spent))
        
        if not interaction:
            return jsonify({'error': 'Interaction not found'}), 404
        
        return jsonify({
            'message': 'Time updated',
            'interaction': interaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/interaction/<int:interaction_id>/complete', methods=['POST'])
@jwt_required()
def complete_example(interaction_id):
    """Mark an interaction as completed."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Complete interaction
        interaction = ExampleService.complete_interaction(interaction_id)
        
        if not interaction:
            return jsonify({'error': 'Interaction not found'}), 404
        
        return jsonify({
            'message': 'Example completed',
            'interaction': interaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_example_stats():
    """Get example interaction statistics for the student."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get stats
        stats = ExampleService.get_student_stats(student.id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_examples():
    """Get recently interacted examples."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get recent examples
        limit = request.args.get('limit', 5, type=int)
        examples = ExampleService.get_recent_examples(student.id, limit)
        
        return jsonify({
            'recent_examples': examples,
            'total': len(examples)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recommended', methods=['GET'])
@jwt_required()
def get_recommended_examples():
    """Get recommended examples based on learning path."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get recommended examples
        limit = request.args.get('limit', 5, type=int)
        examples = ExampleService.get_recommended_examples(student.id, limit)
        
        return jsonify({
            'recommended_examples': examples,
            'total': len(examples)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/types', methods=['GET'])
def get_example_types():
    """Get available example types (no auth required)."""
    try:
        types = ExampleService.get_example_types()
        return jsonify(types), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Admin routes (for creating/managing examples)
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_example():
    """Create a new interactive example (admin only)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['skill_id', 'title', 'example_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create example
        example = ExampleService.create_example(
            skill_id=data['skill_id'],
            title=data['title'],
            example_type=data['example_type'],
            config=data.get('config'),
            description=data.get('description'),
            difficulty=data.get('difficulty', 'beginner'),
            sequence_order=data.get('sequence_order', 0)
        )
        
        return jsonify({
            'message': 'Example created successfully',
            'example': example.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

