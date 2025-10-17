"""
Daily Challenge API routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.challenge_service import ChallengeService
from src.models.user import User

challenge_bp = Blueprint('challenges', __name__, url_prefix='/api/challenges')


@challenge_bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_challenges():
    """Get today's active challenges for the current student."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    challenges = ChallengeService.get_active_challenges(user.student.id)
    
    return jsonify({
        'success': True,
        'challenges': [c.to_dict() for c in challenges]
    }), 200


@challenge_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_challenges():
    """Generate new daily challenges (manually triggered)."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    challenges = ChallengeService.generate_daily_challenges(user.student.id)
    
    if not challenges:
        return jsonify({
            'success': False,
            'message': 'Challenges already exist for today'
        }), 400
    
    return jsonify({
        'success': True,
        'challenges': [c.to_dict() for c in challenges],
        'message': f'{len(challenges)} new challenges generated!'
    }), 200


@challenge_bp.route('/<int:challenge_id>/progress', methods=['POST'])
@jwt_required()
def update_challenge_progress(challenge_id):
    """Update progress for a specific challenge."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    data = request.get_json()
    increment = data.get('increment', 1)
    
    challenge = ChallengeService.update_progress(challenge_id, increment)
    
    if not challenge:
        return jsonify({
            'success': False,
            'message': 'Challenge not found or already completed'
        }), 404
    
    return jsonify({
        'success': True,
        'challenge': challenge.to_dict(),
        'completed': challenge.is_completed,
        'xp_awarded': challenge.bonus_xp if challenge.is_completed else 0
    }), 200


@challenge_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_challenge_stats():
    """Get challenge completion statistics."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    stats = ChallengeService.get_challenge_stats(user.student.id)
    
    return jsonify({
        'success': True,
        'stats': stats
    }), 200


@challenge_bp.route('/history', methods=['GET'])
@jwt_required()
def get_challenge_history():
    """Get challenge completion history."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    limit = request.args.get('limit', 30, type=int)
    history = ChallengeService.get_challenge_history(user.student.id, limit)
    
    return jsonify({
        'success': True,
        'history': history
    }), 200

