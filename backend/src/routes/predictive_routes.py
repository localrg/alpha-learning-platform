"""
API routes for predictive analytics.
"""
from flask import Blueprint, request, jsonify
from src.services.predictive_analytics_service import PredictiveAnalyticsService

predictive_bp = Blueprint('predictive', __name__, url_prefix='/api/predictive')


@predictive_bp.route('/skill-mastery/<int:student_id>/<int:skill_id>', methods=['GET'])
def predict_skill_mastery(student_id, skill_id):
    """Predict if/when student will master a skill"""
    result, status = PredictiveAnalyticsService.predict_skill_mastery(student_id, skill_id)
    return jsonify(result), status


@predictive_bp.route('/assignment-completion/<int:student_id>/<int:assignment_id>', methods=['GET'])
def predict_assignment_completion(student_id, assignment_id):
    """Predict if student will complete assignment on time"""
    result, status = PredictiveAnalyticsService.predict_assignment_completion(student_id, assignment_id)
    return jsonify(result), status


@predictive_bp.route('/at-risk/<int:class_id>', methods=['GET'])
def detect_at_risk_students(class_id):
    """Identify students at risk in a class"""
    result, status = PredictiveAnalyticsService.detect_at_risk_students(class_id)
    return jsonify(result), status


@predictive_bp.route('/forecast/<int:student_id>', methods=['GET'])
def forecast_performance(student_id):
    """Forecast student performance"""
    days = request.args.get('days', default=7, type=int)
    result, status = PredictiveAnalyticsService.forecast_performance(student_id, days)
    return jsonify(result), status

