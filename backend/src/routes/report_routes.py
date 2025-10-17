"""
API routes for parent activity reports.
"""
from flask import Blueprint, request, jsonify
from src.services.report_service import ReportService

report_bp = Blueprint('reports', __name__, url_prefix='/api/parent/children')


@report_bp.route('/<int:student_id>/reports/weekly', methods=['GET'])
def get_weekly_report(student_id):
    """
    Get weekly progress report for a child.
    Query params: week_offset (default: 0 for current week)
    """
    parent_id = request.args.get('parent_id', type=int)
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    week_offset = request.args.get('week_offset', default=0, type=int)
    
    result, status = ReportService.generate_weekly_report(parent_id, student_id, week_offset)
    return jsonify(result), status


@report_bp.route('/<int:student_id>/reports/monthly', methods=['GET'])
def get_monthly_report(student_id):
    """
    Get monthly progress report for a child.
    Query params: month_offset (default: 0 for current month)
    """
    parent_id = request.args.get('parent_id', type=int)
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    month_offset = request.args.get('month_offset', default=0, type=int)
    
    result, status = ReportService.generate_monthly_report(parent_id, student_id, month_offset)
    return jsonify(result), status


@report_bp.route('/<int:student_id>/reports/skills', methods=['GET'])
def get_skill_report(student_id):
    """Get skill performance report for a child."""
    parent_id = request.args.get('parent_id', type=int)
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    result, status = ReportService.generate_skill_report(parent_id, student_id)
    return jsonify(result), status


@report_bp.route('/<int:student_id>/reports/time-analysis', methods=['GET'])
def get_time_analysis(student_id):
    """
    Get time analysis report for a child.
    Query params: days (default: 30)
    """
    parent_id = request.args.get('parent_id', type=int)
    if not parent_id:
        return jsonify({'success': False, 'error': 'parent_id required'}), 400
    
    days = request.args.get('days', default=30, type=int)
    
    result, status = ReportService.generate_time_analysis(parent_id, student_id, days)
    return jsonify(result), status

