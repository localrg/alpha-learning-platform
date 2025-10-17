"""
Friend routes for managing friendships and friend requests.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.friend_service import FriendService
from src.models.user import User

friend_bp = Blueprint('friends', __name__, url_prefix='/api/friends')


@friend_bp.route('', methods=['GET'])
@jwt_required()
def get_friends():
    """Get all friends."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        friends = FriendService.get_friends(user.student.id)
        return jsonify({'friends': friends}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/request/<int:addressee_id>', methods=['POST'])
@jwt_required()
def send_request(addressee_id):
    """Send a friend request."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        friendship = FriendService.send_request(user.student.id, addressee_id)
        return jsonify({'message': 'Friend request sent', 'friendship': friendship.to_dict()}), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/request/<int:friendship_id>/accept', methods=['PUT'])
@jwt_required()
def accept_request(friendship_id):
    """Accept a friend request."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        friendship = FriendService.accept_request(friendship_id, user.student.id)
        return jsonify({'message': 'Friend request accepted', 'friendship': friendship.to_dict()}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/request/<int:friendship_id>/reject', methods=['PUT'])
@jwt_required()
def reject_request(friendship_id):
    """Reject a friend request."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        FriendService.reject_request(friendship_id, user.student.id)
        return jsonify({'message': 'Friend request rejected'}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/request/<int:friendship_id>', methods=['DELETE'])
@jwt_required()
def cancel_request(friendship_id):
    """Cancel a sent friend request."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        FriendService.cancel_request(friendship_id, user.student.id)
        return jsonify({'message': 'Friend request cancelled'}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/<int:friend_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friend_id):
    """Remove a friend."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        FriendService.remove_friend(user.student.id, friend_id)
        return jsonify({'message': 'Friend removed'}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/requests/received', methods=['GET'])
@jwt_required()
def get_received_requests():
    """Get received friend requests."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        requests = FriendService.get_received_requests(user.student.id)
        return jsonify({'requests': requests}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/requests/sent', methods=['GET'])
@jwt_required()
def get_sent_requests():
    """Get sent friend requests."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        requests = FriendService.get_sent_requests(user.student.id)
        return jsonify({'requests': requests}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/search', methods=['GET'])
@jwt_required()
def search_students():
    """Search for students."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        query = request.args.get('q', '')
        if not query or len(query) < 2:
            return jsonify({'students': []}), 200
        
        students = FriendService.search_students(query, user.student.id)
        return jsonify({'students': students}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@friend_bp.route('/count', methods=['GET'])
@jwt_required()
def get_friend_count():
    """Get friend count."""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.student:
            return jsonify({'error': 'Student not found'}), 404
        
        count = FriendService.get_friend_count(user.student.id)
        return jsonify({'count': count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

