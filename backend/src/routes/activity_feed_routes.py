"""
Activity Feed Routes
API endpoints for social activity feed
"""

from flask import Blueprint, request, jsonify
from src.services.activity_feed_service import ActivityFeedService
from src.middleware.auth import token_required

activity_feed_bp = Blueprint('activity_feed', __name__)


@activity_feed_bp.route('/api/feed', methods=['GET'])
@token_required
def get_feed(current_user, current_student):
    """Get personalized activity feed"""
    filter_type = request.args.get('type')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    result, status = ActivityFeedService.get_feed(
        current_student.id,
        filter_type,
        limit,
        offset
    )
    return jsonify(result), status


@activity_feed_bp.route('/api/feed/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_activities(current_user, current_student, student_id):
    """Get specific student's activities"""
    limit = int(request.args.get('limit', 20))
    
    result, status = ActivityFeedService.get_student_activities(
        student_id,
        current_student.id,
        limit
    )
    return jsonify(result), status


@activity_feed_bp.route('/api/feed/<int:activity_id>', methods=['DELETE'])
@token_required
def delete_activity(current_user, current_student, activity_id):
    """Delete activity (owner only)"""
    result, status = ActivityFeedService.delete_activity(
        activity_id,
        current_student.id
    )
    return jsonify(result), status


@activity_feed_bp.route('/api/feed/stats', methods=['GET'])
@token_required
def get_activity_stats(current_user, current_student):
    """Get activity statistics"""
    result, status = ActivityFeedService.get_activity_stats(current_student.id)
    return jsonify(result), status

