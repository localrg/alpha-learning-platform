"""
API routes for analytics dashboard.
"""
from flask import Blueprint, request, jsonify
from src.services.analytics_dashboard_service import AnalyticsDashboardService

analytics_dashboard_bp = Blueprint('analytics_dashboard', __name__, url_prefix='/api/analytics')


@analytics_dashboard_bp.route('/student/<int:student_id>/dashboard', methods=['GET'])
def get_student_dashboard(student_id):
    """Get analytics dashboard for student"""
    days = request.args.get('days', default=30, type=int)
    
    result, status = AnalyticsDashboardService.get_student_dashboard(student_id, days)
    return jsonify(result), status


@analytics_dashboard_bp.route('/teacher/<int:teacher_id>/dashboard', methods=['GET'])
def get_teacher_dashboard(teacher_id):
    """Get analytics dashboard for teacher"""
    class_id = request.args.get('class_id', type=int)
    
    result, status = AnalyticsDashboardService.get_teacher_dashboard(teacher_id, class_id)
    return jsonify(result), status


@analytics_dashboard_bp.route('/student/<int:student_id>/comparative', methods=['GET'])
def get_comparative_analytics(student_id):
    """Get comparative analytics for student"""
    comparison_type = request.args.get('type', default='class')
    
    result, status = AnalyticsDashboardService.get_comparative_analytics(student_id, comparison_type)
    return jsonify(result), status


@analytics_dashboard_bp.route('/student/<int:student_id>/engagement', methods=['GET'])
def get_engagement_score(student_id):
    """Get engagement score for student"""
    days = request.args.get('days', default=30, type=int)
    
    score = AnalyticsDashboardService.calculate_engagement_score(student_id, days)
    return jsonify({'success': True, 'engagement_score': round(score, 1)}), 200

