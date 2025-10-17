"""
Shared Challenge Routes
API endpoints for shared challenges
"""

from flask import Blueprint, request, jsonify
from src.services.shared_challenge_service import SharedChallengeService
from src.middleware.auth import token_required

shared_challenge_bp = Blueprint('shared_challenges', __name__)


@shared_challenge_bp.route('/api/shared-challenges', methods=['POST'])
@token_required
def create_challenge(current_user, current_student):
    """Create a new shared challenge"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'challenge_type', 'mode', 'skill_id', 
                      'target_questions', 'target_accuracy']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate values
    if data['target_questions'] < 5 or data['target_questions'] > 50:
        return jsonify({'error': 'Target questions must be between 5 and 50'}), 400
    
    if data['target_accuracy'] < 0.7 or data['target_accuracy'] > 1.0:
        return jsonify({'error': 'Target accuracy must be between 0.7 and 1.0'}), 400
    
    result, status = SharedChallengeService.create_challenge(current_student.id, data)
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges', methods=['GET'])
@token_required
def get_my_challenges(current_user, current_student):
    """Get all challenges for current student"""
    filter_status = request.args.get('status')
    
    result, status = SharedChallengeService.get_student_challenges(
        current_student.id,
        filter_status
    )
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges/<int:challenge_id>', methods=['GET'])
@token_required
def get_challenge(current_user, current_student, challenge_id):
    """Get challenge details"""
    result, status = SharedChallengeService.get_challenge(
        challenge_id,
        current_student.id
    )
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges/<int:challenge_id>', methods=['DELETE'])
@token_required
def delete_challenge(current_user, current_student, challenge_id):
    """Delete a challenge (creator only)"""
    result, status = SharedChallengeService.delete_challenge(
        challenge_id,
        current_student.id
    )
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges/<int:challenge_id>/accept', methods=['POST'])
@token_required
def accept_challenge(current_user, current_student, challenge_id):
    """Accept a challenge invitation"""
    result, status = SharedChallengeService.accept_challenge(
        challenge_id,
        current_student.id
    )
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges/<int:challenge_id>/decline', methods=['POST'])
@token_required
def decline_challenge(current_user, current_student, challenge_id):
    """Decline a challenge invitation"""
    result, status = SharedChallengeService.decline_challenge(
        challenge_id,
        current_student.id
    )
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges/<int:challenge_id>/progress', methods=['POST'])
@token_required
def update_progress(current_user, current_student, challenge_id):
    """Update challenge progress"""
    data = request.get_json()
    
    if 'correct' not in data:
        return jsonify({'error': 'Missing required field: correct'}), 400
    
    result, status = SharedChallengeService.update_progress(
        challenge_id,
        current_student.id,
        data
    )
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges/<int:challenge_id>/leaderboard', methods=['GET'])
@token_required
def get_leaderboard(current_user, current_student, challenge_id):
    """Get challenge leaderboard"""
    result, status = SharedChallengeService.get_challenge_leaderboard(challenge_id)
    return jsonify(result), status


@shared_challenge_bp.route('/api/shared-challenges/<int:challenge_id>/complete', methods=['POST'])
@token_required
def complete_challenge(current_user, current_student, challenge_id):
    """Complete a challenge and award final rewards"""
    result, status = SharedChallengeService.complete_challenge(challenge_id)
    return jsonify(result), status

