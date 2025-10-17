"""
Gamification API routes for XP, levels, and rewards.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.gamification_service import GamificationService
from src.models.user import User

gamification_bp = Blueprint('gamification', __name__, url_prefix='/api/gamification')


@gamification_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    """Get student's gamification progress."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        progress = GamificationService.get_student_progress(user.student.id)
        return jsonify(progress), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/award-xp', methods=['POST'])
@jwt_required()
def award_xp():
    """Award XP to current student."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        data = request.get_json()
        action_type = data.get('action_type')
        base_xp = data.get('base_xp')
        difficulty = data.get('difficulty')
        metadata = data.get('metadata', {})
        
        if not action_type:
            return jsonify({'error': 'action_type is required'}), 400
        
        result = GamificationService.award_xp(
            student_id=user.student.id,
            action_type=action_type,
            base_xp=base_xp,
            difficulty=difficulty,
            metadata=metadata
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/xp-history', methods=['GET'])
@jwt_required()
def get_xp_history():
    """Get student's XP transaction history."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        limit = request.args.get('limit', 20, type=int)
        transactions = GamificationService.get_xp_history(user.student.id, limit)
        
        return jsonify({
            'transactions': transactions,
            'total': len(transactions)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/rewards', methods=['GET'])
@jwt_required()
def get_rewards():
    """Get student's unlocked and upcoming rewards."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        rewards = GamificationService.get_student_rewards(user.student.id)
        return jsonify(rewards), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get leaderboard rankings."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        timeframe = request.args.get('timeframe', 'all')
        limit = request.args.get('limit', 10, type=int)
        
        leaderboard = GamificationService.get_leaderboard(timeframe, limit)
        
        # Find current user's rank
        current_user_rank = None
        for entry in leaderboard:
            if entry['student_id'] == user.student.id:
                current_user_rank = entry['rank']
                entry['is_current_user'] = True
            else:
                entry['is_current_user'] = False
        
        return jsonify({
            'leaderboard': leaderboard,
            'current_user_rank': current_user_rank,
            'total_students': len(leaderboard)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/seed-rewards', methods=['POST'])
def seed_rewards():
    """Seed initial level rewards (admin only for now)."""
    try:
        GamificationService.seed_level_rewards()
        return jsonify({'message': 'Level rewards seeded successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

