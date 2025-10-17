"""
Resource API routes for managing and downloading educational resources.
"""
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.models.user import User
from src.services.resource_service import ResourceService
import os

resource_bp = Blueprint('resource', __name__, url_prefix='/api/resources')


@resource_bp.route('', methods=['GET'])
def get_resources():
    """Get all resources with optional filters."""
    try:
        # Get filter parameters
        filters = {
            'resource_type': request.args.get('type'),
            'skill_id': request.args.get('skill_id', type=int),
            'grade_level': request.args.get('grade', type=int),
            'difficulty': request.args.get('difficulty'),
            'search': request.args.get('search')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Get resources
        resources = ResourceService.get_all_resources(filters)
        
        # Get available filters
        available_filters = ResourceService.get_available_filters()
        
        return jsonify({
            'resources': [r.to_dict() for r in resources],
            'total': len(resources),
            'filters': available_filters
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resource_bp.route('/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get a specific resource by ID."""
    try:
        resource = ResourceService.get_resource_by_id(resource_id)
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Get related resources
        related = ResourceService.get_related_resources(resource_id)
        
        return jsonify({
            'resource': resource,
            'related_resources': related
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resource_bp.route('/<int:resource_id>/download', methods=['POST'])
@jwt_required()
def download_resource(resource_id):
    """Record a resource download."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        data = request.get_json() or {}
        download_method = data.get('download_method', 'direct')
        
        student = current_user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get resource
        resource = ResourceService.get_resource_by_id(resource_id)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Record download
        download = ResourceService.record_download(
            student_id=student.id,
            resource_id=resource_id,
            download_method=download_method
        )
        
        return jsonify({
            'download_url': resource['file_url'],
            'message': 'Download recorded',
            'download_id': download.id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resource_bp.route('/downloads', methods=['GET'])
@jwt_required()
def get_student_downloads():
    """Get download history for the current student."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        student = current_user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        limit = request.args.get('limit', type=int)
        
        downloads = ResourceService.get_student_downloads(student.id, limit)
        
        return jsonify({
            'downloads': downloads,
            'total': len(downloads)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resource_bp.route('/<int:resource_id>/stats', methods=['GET'])
def get_resource_stats(resource_id):
    """Get statistics for a resource."""
    try:
        stats = ResourceService.get_resource_stats(resource_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resource_bp.route('/popular', methods=['GET'])
def get_popular_resources():
    """Get most popular resources."""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        resources = ResourceService.get_popular_resources(limit)
        
        return jsonify({
            'resources': resources,
            'total': len(resources)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resource_bp.route('/recent', methods=['GET'])
def get_recent_resources():
    """Get recently added resources."""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        resources = ResourceService.get_recent_resources(limit)
        
        return jsonify({
            'resources': resources,
            'total': len(resources)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resource_bp.route('/create', methods=['POST'])
@jwt_required()
def create_resource():
    """Create a new resource (admin/teacher only)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'resource_type', 'grade_level', 'file_url', 'file_type', 'file_size_kb']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create resource
        resource = ResourceService.create_resource(data)
        
        return jsonify({
            'message': 'Resource created successfully',
            'resource': resource.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

