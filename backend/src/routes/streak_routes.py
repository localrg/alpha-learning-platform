"""
API routes for streak tracking.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.streak_service import StreakService

streak_bp = Blueprint('streak', __name__, url_prefix='/api/streaks')


@streak_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_streaks():
    """Get current streak status for the authenticated student."""
    try:
        user_id = get_jwt_identity()
        # Assume user_id == student_id for simplicity
        student_id = user_id
        
        stats = StreakService.get_streak_stats(student_id)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@streak_bp.route('/update-login', methods=['POST'])
@jwt_required()
def update_login_streak():
    """Update login streak for the authenticated student."""
    try:
        user_id = get_jwt_identity()
        student_id = user_id
        
        result = StreakService.update_login_streak(student_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@streak_bp.route('/update-practice', methods=['POST'])
@jwt_required()
def update_practice_streak():
    """Update practice streak for the authenticated student."""
    try:
        user_id = get_jwt_identity()
        student_id = user_id
        
        result = StreakService.update_practice_streak(student_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@streak_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_streak_stats():
    """Get detailed streak statistics."""
    try:
        user_id = get_jwt_identity()
        student_id = user_id
        
        stats = StreakService.get_streak_stats(student_id)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

