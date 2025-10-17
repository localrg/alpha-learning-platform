"""
API routes for personalized recommendations.
"""
from flask import Blueprint, request, jsonify
from src.services.recommendation_service import RecommendationService

recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/api/recommendations')


@recommendation_bp.route('/skills/<int:student_id>', methods=['GET'])
def get_skill_recommendations(student_id):
    """Get recommended skills for student"""
    count = request.args.get('count', default=5, type=int)
    result, status = RecommendationService.get_skill_recommendations(student_id, count)
    return jsonify(result), status


@recommendation_bp.route('/practice-time/<int:student_id>', methods=['GET'])
def get_practice_time_recommendations(student_id):
    """Get optimal practice time recommendations"""
    result, status = RecommendationService.get_practice_time_recommendations(student_id)
    return jsonify(result), status


@recommendation_bp.route('/strategies/<int:student_id>', methods=['GET'])
def get_study_strategies(student_id):
    """Get personalized study strategies"""
    result, status = RecommendationService.get_study_strategies(student_id)
    return jsonify(result), status


@recommendation_bp.route('/gaps/<int:student_id>', methods=['GET'])
def analyze_skill_gaps(student_id):
    """Analyze skill gaps for student"""
    result, status = RecommendationService.analyze_skill_gaps(student_id)
    return jsonify(result), status

