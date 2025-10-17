"""
Learning Path API routes for generating and managing personalized learning paths.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.services.learning_path_service import LearningPathService

learning_path_bp = Blueprint('learning_path', __name__, url_prefix='/api/learning-path')


@learning_path_bp.route('/generate/<int:assessment_id>', methods=['POST'])
@jwt_required()
def generate_learning_path(assessment_id):
    """
    Generate a learning path from a completed assessment.
    
    Args:
        assessment_id: ID of the completed assessment
        
    Response:
        {
            "student_id": 1,
            "student_name": "Alex Johnson",
            "assessment_score": 65.0,
            "total_skills_to_master": 3,
            "learning_path": [...],
            "skills_analysis": [...],
            "recommendations": [...]
        }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Generate learning path
        result = LearningPathService.generate_from_assessment(assessment_id)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to generate learning path: {str(e)}'}), 500


@learning_path_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_learning_path():
    """
    Get the current learning path for the authenticated student.
    
    Response:
        {
            "total_skills": 5,
            "mastered": 1,
            "in_progress": 2,
            "not_started": 2,
            "skills": [...]
        }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        learning_path = LearningPathService.get_student_learning_path(student.id)
        
        return jsonify(learning_path), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get learning path: {str(e)}'}), 500


@learning_path_bp.route('/next-skill', methods=['GET'])
@jwt_required()
def get_next_skill():
    """
    Get the next skill the student should work on.
    
    Response:
        {
            "id": 1,
            "skill_id": 3,
            "skill_name": "Introduction to Fractions",
            "status": "not_started",
            "current_accuracy": 0.0,
            ...
        }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        next_skill = LearningPathService.get_next_skill(student.id)
        
        if next_skill:
            return jsonify(next_skill), 200
        else:
            return jsonify({'message': 'No more skills to master! Great job!'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get next skill: {str(e)}'}), 500




@learning_path_bp.route('/update-progress', methods=['PUT'])
@jwt_required()
def update_progress():
    """Update progress for a skill in the learning path"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        skill_id = data.get('skill_id')
        correct_answers = data.get('correct_answers', 0)
        total_questions = data.get('total_questions', 0)
        
        if not skill_id or total_questions == 0:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get student
        student = Student.query.filter_by(user_id=current_user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get or create learning path item
        learning_path_item = LearningPath.query.filter_by(
            student_id=student.id,
            skill_id=skill_id
        ).first()
        
        if not learning_path_item:
            # Create new learning path item
            learning_path_item = LearningPath(
                student_id=student.id,
                skill_id=skill_id,
                status='in_progress'
            )
            db.session.add(learning_path_item)
        
        # Update progress
        learning_path_item.update_progress(correct_answers, total_questions)
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully',
            'learning_path_item': learning_path_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

