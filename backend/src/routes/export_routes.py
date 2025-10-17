"""
API routes for data export and reporting.
"""
from flask import Blueprint, request, jsonify, Response
from src.services.export_service import ExportService

export_bp = Blueprint('export', __name__, url_prefix='/api/export')


@export_bp.route('/student/<int:student_id>', methods=['GET'])
def export_student_data(student_id):
    """Export student data"""
    format = request.args.get('format', default='json')
    result, status = ExportService.export_student_data(student_id, format)
    
    if result.get('success'):
        if format == 'csv':
            return Response(
                result['data'],
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=student_{student_id}.csv'}
            )
        else:
            return jsonify(result), status
    else:
        return jsonify(result), status


@export_bp.route('/class/<int:class_id>', methods=['GET'])
def export_class_data(class_id):
    """Export class data"""
    format = request.args.get('format', default='json')
    result, status = ExportService.export_class_data(class_id, format)
    
    if result.get('success'):
        if format == 'csv':
            return Response(
                result['data'],
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=class_{class_id}.csv'}
            )
        else:
            return jsonify(result), status
    else:
        return jsonify(result), status


@export_bp.route('/report/<report_type>/<int:entity_id>', methods=['GET'])
def generate_report(report_type, entity_id):
    """Generate a specific type of report"""
    format = request.args.get('format', default='json')
    result, status = ExportService.generate_report(report_type, entity_id, format)
    
    if result.get('success'):
        if format == 'csv':
            return Response(
                result['data'],
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename={report_type}_{entity_id}.csv'}
            )
        else:
            return jsonify(result), status
    else:
        return jsonify(result), status

