"""
Video API routes for managing video tutorials and tracking viewing.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.models.video import VideoTutorial
from src.services.video_service import VideoService

bp = Blueprint('video', __name__, url_prefix='/api/videos')


@bp.route('/skill/<int:skill_id>', methods=['GET'])
@jwt_required()
def get_skill_videos(skill_id):
    """Get all videos for a specific skill."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get videos for skill
        videos = VideoService.get_videos_for_skill(skill_id, student_id=student.id)
        
        return jsonify({
            'videos': videos,
            'total_videos': len(videos)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """Get details for a specific video."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get video
        video = VideoService.get_video_by_id(video_id, student_id=student.id)
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        return jsonify(video), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:video_id>/start', methods=['POST'])
@jwt_required()
def start_video(video_id):
    """Record that a student started watching a video."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Check if video exists
        video = VideoTutorial.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Start video view
        view = VideoService.start_video_view(video_id, student.id)
        
        return jsonify({
            'message': 'Video view started',
            'view': view.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:video_id>/progress', methods=['PUT'])
@jwt_required()
def update_progress(video_id):
    """Update viewing progress for a video."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Validate input
        watch_time = data.get('watch_time_seconds', 0)
        percentage = data.get('completion_percentage', 0)
        
        if not isinstance(watch_time, (int, float)) or watch_time < 0:
            return jsonify({'error': 'Invalid watch_time_seconds'}), 400
        
        if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
            return jsonify({'error': 'Invalid completion_percentage'}), 400
        
        # Update progress
        view = VideoService.update_video_progress(
            video_id,
            student.id,
            int(watch_time),
            float(percentage)
        )
        
        return jsonify({
            'message': 'Progress updated',
            'view': view.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:video_id>/complete', methods=['POST'])
@jwt_required()
def complete_video(video_id):
    """Mark a video as completed."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Check if video exists
        video = VideoTutorial.query.get(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Complete video
        view = VideoService.complete_video(video_id, student.id)
        
        return jsonify({
            'message': 'Video completed',
            'view': view.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_video_stats():
    """Get video viewing statistics for the student."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get stats
        stats = VideoService.get_student_video_stats(student.id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_videos():
    """Get recently watched videos."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get recent videos
        limit = request.args.get('limit', 5, type=int)
        videos = VideoService.get_recent_videos(student.id, limit)
        
        return jsonify({
            'recent_videos': videos,
            'total': len(videos)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recommended', methods=['GET'])
@jwt_required()
def get_recommended_videos():
    """Get recommended videos based on learning path."""
    try:
        user_id = get_jwt_identity()
        
        # Get student
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get recommended videos
        limit = request.args.get('limit', 5, type=int)
        videos = VideoService.get_recommended_videos(student.id, limit)
        
        return jsonify({
            'recommended_videos': videos,
            'total': len(videos)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Admin routes (for creating/managing videos)
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_video():
    """Create a new video tutorial (admin only)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['skill_id', 'title', 'video_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create video
        video = VideoService.create_video_tutorial(
            skill_id=data['skill_id'],
            title=data['title'],
            video_url=data['video_url'],
            description=data.get('description'),
            difficulty=data.get('difficulty', 'beginner'),
            duration=data.get('duration_seconds', 0),
            sequence_order=data.get('sequence_order', 0)
        )
        
        return jsonify({
            'message': 'Video created successfully',
            'video': video.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

