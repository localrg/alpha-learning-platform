"""
Review API routes for spaced repetition review system.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.models.learning_path import LearningPath
from src.models.assessment import Question
from src.services.review_service import ReviewService
import random

bp = Blueprint('review', __name__, url_prefix='/api/reviews')


@bp.route('/due', methods=['GET'])
@jwt_required()
def get_reviews_due():
    """Get all skills due for review."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get reviews due
        reviews_due = ReviewService.get_reviews_due(student.id)
        
        # Format response
        reviews_data = []
        for item in reviews_due:
            days_overdue = (item.next_review_date - item.next_review_date).days if item.next_review_date else 0
            
            reviews_data.append({
                'learning_path_id': item.id,
                'skill_id': item.skill_id,
                'skill_name': item.skill.name,
                'skill_description': item.skill.description,
                'mastery_date': item.mastery_date.isoformat() if item.mastery_date else None,
                'last_reviewed_at': item.last_reviewed_at.isoformat() if item.last_reviewed_at else None,
                'next_review_date': item.next_review_date.isoformat() if item.next_review_date else None,
                'review_number': item.review_count + 1,
                'days_overdue': max(0, days_overdue)
            })
        
        return jsonify({
            'reviews_due': reviews_data,
            'total_due': len(reviews_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_reviews():
    """Get upcoming reviews in the next 7 days."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get upcoming reviews
        days_ahead = request.args.get('days', 7, type=int)
        upcoming = ReviewService.get_upcoming_reviews(student.id, days_ahead)
        
        # Format response
        upcoming_data = []
        for item in upcoming:
            from datetime import datetime
            days_until = (item.next_review_date - datetime.utcnow()).days if item.next_review_date else 0
            
            upcoming_data.append({
                'learning_path_id': item.id,
                'skill_id': item.skill_id,
                'skill_name': item.skill.name,
                'next_review_date': item.next_review_date.isoformat() if item.next_review_date else None,
                'days_until': max(0, days_until),
                'review_number': item.review_count + 1
            })
        
        return jsonify({
            'upcoming_reviews': upcoming_data,
            'total_upcoming': len(upcoming_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/start', methods=['POST'])
@jwt_required()
def start_review():
    """Start a review session."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        learning_path_id = data.get('learning_path_id')
        if not learning_path_id:
            return jsonify({'error': 'learning_path_id is required'}), 400
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Start review session
        review_session = ReviewService.start_review_session(learning_path_id, student.id)
        
        if not review_session:
            return jsonify({'error': 'Could not start review session'}), 400
        
        # Get the skill
        learning_path_item = LearningPath.query.get(learning_path_id)
        skill = learning_path_item.skill
        
        # Get 3-5 random questions for this skill
        num_questions = random.randint(3, 5)
        questions = Question.query.filter_by(skill_id=skill.id).all()
        
        if len(questions) < num_questions:
            num_questions = len(questions)
        
        selected_questions = random.sample(questions, num_questions)
        
        # Format questions
        questions_data = []
        for q in selected_questions:
            questions_data.append({
                'id': q.id,
                'question_text': q.question_text,
                'question_type': q.question_type,
                'options': q.options,
                'difficulty': q.difficulty
            })
        
        return jsonify({
            'review_session_id': review_session.id,
            'skill': {
                'id': skill.id,
                'name': skill.name,
                'description': skill.description
            },
            'questions': questions_data,
            'review_number': review_session.review_number,
            'total_questions': len(questions_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:review_session_id>/complete', methods=['PUT'])
@jwt_required()
def complete_review(review_session_id):
    """Complete a review session."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        answers = data.get('answers', [])
        if not answers:
            return jsonify({'error': 'answers are required'}), 400
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Calculate score
        correct = 0
        total = len(answers)
        
        for answer in answers:
            question_id = answer.get('question_id')
            selected_answer = answer.get('selected_answer')
            
            question = Question.query.get(question_id)
            if question and question.correct_answer == selected_answer:
                correct += 1
        
        # Complete the review session
        result = ReviewService.complete_review_session(review_session_id, correct, total)
        
        if not result:
            return jsonify({'error': 'Review session not found'}), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/history', methods=['GET'])
@jwt_required()
def get_review_history():
    """Get review history for the student."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get review history
        limit = request.args.get('limit', 10, type=int)
        history = ReviewService.get_review_history(student.id, limit)
        
        # Format response
        history_data = [session.to_dict() for session in history]
        
        return jsonify({
            'review_history': history_data,
            'total_reviews': len(history_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

