"""
Analytics API Routes
"""
from flask import Blueprint, request, jsonify
from src.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/student/<int:student_id>/report', methods=['GET'])
def get_student_report(student_id):
    """Get student performance report"""
    days = request.args.get('days', 30, type=int)
    report = AnalyticsService.get_student_performance_report(student_id, days)
    
    if not report:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    return jsonify({'success': True, 'report': report}), 200


@analytics_bp.route('/class/<int:class_id>/report', methods=['GET'])
def get_class_report(class_id):
    """Get class performance report"""
    days = request.args.get('days', 30, type=int)
    report = AnalyticsService.get_class_performance_report(class_id, days)
    
    if not report:
        return jsonify({'success': False, 'error': 'Class not found'}), 404
    
    return jsonify({'success': True, 'report': report}), 200


@analytics_bp.route('/student/<int:student_id>/trends', methods=['GET'])
def get_student_trends(student_id):
    """Get student trend data"""
    metric = request.args.get('metric', 'accuracy')
    days = request.args.get('days', 30, type=int)
    
    trends = AnalyticsService.get_student_trend_data(student_id, metric, days)
    
    return jsonify({'success': True, 'trends': trends}), 200


@analytics_bp.route('/class/<int:class_id>/trends', methods=['GET'])
def get_class_trends(class_id):
    """Get class trend data"""
    metric = request.args.get('metric', 'accuracy')
    days = request.args.get('days', 30, type=int)
    
    trends = AnalyticsService.get_class_trend_data(class_id, metric, days)
    
    return jsonify({'success': True, 'trends': trends}), 200


@analytics_bp.route('/student/<int:student_id>/comparison', methods=['GET'])
def get_student_comparison(student_id):
    """Get student vs class comparison"""
    comparison = AnalyticsService.get_student_comparison(student_id)
    
    if not comparison:
        return jsonify({'success': False, 'error': 'Student not found or not in a class'}), 404
    
    return jsonify({'success': True, 'comparison': comparison}), 200

