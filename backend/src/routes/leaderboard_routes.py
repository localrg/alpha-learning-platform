"""
Leaderboard API routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.leaderboard_service import LeaderboardService
from src.models.user import User

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboards')


@leaderboard_bp.route('/global', methods=['GET'])
@jwt_required()
def get_global_leaderboard():
    """Get global XP leaderboard."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    leaderboard = LeaderboardService.get_global_xp_leaderboard(limit, offset)
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard,
        'type': 'global_xp',
        'limit': limit,
        'offset': offset
    }), 200


@leaderboard_bp.route('/grade/<int:grade>', methods=['GET'])
@jwt_required()
def get_grade_leaderboard(grade):
    """Get grade-level leaderboard."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    leaderboard = LeaderboardService.get_grade_leaderboard(grade, limit, offset)
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard,
        'type': 'grade_xp',
        'grade': grade,
        'limit': limit,
        'offset': offset
    }), 200


@leaderboard_bp.route('/skills', methods=['GET'])
@jwt_required()
def get_skills_leaderboard():
    """Get skills mastered leaderboard."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    leaderboard = LeaderboardService.get_skills_leaderboard(limit, offset)
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard,
        'type': 'skills',
        'limit': limit,
        'offset': offset
    }), 200


@leaderboard_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_achievements_leaderboard():
    """Get achievements unlocked leaderboard."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    leaderboard = LeaderboardService.get_achievements_leaderboard(limit, offset)
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard,
        'type': 'achievements',
        'limit': limit,
        'offset': offset
    }), 200


@leaderboard_bp.route('/my-rank/<leaderboard_type>', methods=['GET'])
@jwt_required()
def get_my_rank(leaderboard_type):
    """Get current user's rank in specified leaderboard."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    rank_info = LeaderboardService.get_student_rank(user.student.id, leaderboard_type)
    
    if not rank_info:
        return jsonify({'success': False, 'message': 'Rank not found'}), 404
    
    return jsonify({
        'success': True,
        'rank_info': rank_info,
        'leaderboard_type': leaderboard_type
    }), 200


@leaderboard_bp.route('/nearby/<leaderboard_type>', methods=['GET'])
@jwt_required()
def get_nearby_students(leaderboard_type):
    """Get students near current user's rank."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    range_size = request.args.get('range', 5, type=int)
    nearby = LeaderboardService.get_nearby_students(
        user.student.id,
        leaderboard_type,
        range_size
    )
    
    return jsonify({
        'success': True,
        'nearby_students': nearby,
        'leaderboard_type': leaderboard_type,
        'range_size': range_size
    }), 200


@leaderboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_leaderboard_summary():
    """Get summary of user's ranks across all leaderboards."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    summary = LeaderboardService.get_leaderboard_summary(user.student.id)
    
    return jsonify({
        'success': True,
        'summary': summary
    }), 200

