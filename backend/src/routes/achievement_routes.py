"""
Achievement API routes.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.achievement_service import AchievementService
from src.models.user import User
from src.models.achievement import Achievement

achievement_routes_bp = Blueprint('achievement_routes', __name__, url_prefix='/api/achievements')


@achievement_routes_bp.route('', methods=['GET'])
@jwt_required()
def get_all_achievements():
    """Get all achievement definitions."""
    try:
        category = request.args.get('category')
        
        query = Achievement.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        
        achievements = query.all()
        
        return jsonify({
            'achievements': [a.to_dict() for a in achievements],
            'total': len(achievements)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievement_routes_bp.route('/student', methods=['GET'])
@jwt_required()
def get_student_achievements():
    """Get student's achievements with progress."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        category = request.args.get('category')
        unlocked_only = request.args.get('unlocked_only', 'false').lower() == 'true'
        
        achievements = AchievementService.get_student_achievements(
            student_id=user.student.id,
            category=category,
            unlocked_only=unlocked_only
        )
        
        return jsonify({
            'achievements': achievements,
            'total': len(achievements)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievement_routes_bp.route('/unlocked', methods=['GET'])
@jwt_required()
def get_unlocked():
    """Get student's unlocked achievements."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        achievements = AchievementService.get_unlocked_achievements(user.student.id)
        
        return jsonify({
            'achievements': achievements,
            'total': len(achievements)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievement_routes_bp.route('/in-progress', methods=['GET'])
@jwt_required()
def get_in_progress():
    """Get achievements close to unlocking."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        limit = request.args.get('limit', 5, type=int)
        achievements = AchievementService.get_in_progress_achievements(user.student.id, limit)
        
        return jsonify({
            'achievements': achievements,
            'total': len(achievements)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievement_routes_bp.route('/displayed', methods=['GET'])
@jwt_required()
def get_displayed():
    """Get student's displayed badges."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        achievements = AchievementService.get_displayed_achievements(user.student.id)
        
        return jsonify({
            'achievements': achievements,
            'total': len(achievements)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievement_routes_bp.route('/<int:achievement_id>/display', methods=['POST'])
@jwt_required()
def toggle_display(achievement_id):
    """Toggle badge display on profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        student_achievement = AchievementService.toggle_display(user.student.id, achievement_id)
        
        if not student_achievement:
            return jsonify({'error': 'Achievement not found or not unlocked'}), 404
        
        return jsonify({
            'achievement': student_achievement.to_dict(),
            'is_displayed': student_achievement.is_displayed
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievement_routes_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get achievement statistics."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        stats = AchievementService.get_achievement_stats(user.student.id)
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievement_routes_bp.route('/seed', methods=['POST'])
def seed_achievements():
    """Seed achievement definitions (admin only for now)."""
    try:
        count = AchievementService.seed_achievements()
        return jsonify({
            'message': f'Successfully seeded {count} achievements',
            'count': count
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

