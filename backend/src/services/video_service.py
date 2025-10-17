"""
Video Service for managing video tutorials and tracking viewing progress.
"""
from src.database import db
from src.models.video import VideoTutorial, VideoView
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs


class VideoService:
    """Service for managing video tutorials."""
    
    @staticmethod
    def parse_video_url(url):
        """
        Parse video URL and extract platform and video ID.
        
        Args:
            url: Video URL (YouTube, Vimeo, or direct)
            
        Returns:
            dict: {'platform': str, 'video_id': str, 'thumbnail_url': str}
        """
        # YouTube patterns
        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return {
                    'platform': 'youtube',
                    'video_id': video_id,
                    'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
                }
        
        # Vimeo patterns
        vimeo_patterns = [
            r'vimeo\.com\/(\d+)',
            r'player\.vimeo\.com\/video\/(\d+)',
        ]
        
        for pattern in vimeo_patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return {
                    'platform': 'vimeo',
                    'video_id': video_id,
                    'thumbnail_url': None  # Vimeo requires API call for thumbnail
                }
        
        # Direct video (MP4, WebM, etc.)
        if url.endswith(('.mp4', '.webm', '.ogg', '.mov')):
            return {
                'platform': 'direct',
                'video_id': url.split('/')[-1],  # Use filename as ID
                'thumbnail_url': None
            }
        
        # Unknown format
        raise ValueError(f"Unsupported video URL format: {url}")
    
    @staticmethod
    def create_video_tutorial(skill_id, title, video_url, description=None, 
                             difficulty='beginner', duration=0, sequence_order=0):
        """
        Create a new video tutorial.
        
        Args:
            skill_id: ID of the skill
            title: Video title
            video_url: Video URL
            description: Video description
            difficulty: Difficulty level
            duration: Duration in seconds
            sequence_order: Order within skill
            
        Returns:
            VideoTutorial: Created video tutorial
        """
        # Parse video URL
        try:
            parsed = VideoService.parse_video_url(video_url)
        except ValueError as e:
            raise ValueError(f"Invalid video URL: {str(e)}")
        
        # Create video tutorial
        video = VideoTutorial(
            skill_id=skill_id,
            title=title,
            description=description,
            video_url=video_url,
            video_platform=parsed['platform'],
            video_id=parsed['video_id'],
            thumbnail_url=parsed['thumbnail_url'],
            difficulty_level=difficulty,
            duration_seconds=duration,
            sequence_order=sequence_order
        )
        
        db.session.add(video)
        db.session.commit()
        
        return video
    
    @staticmethod
    def get_videos_for_skill(skill_id, student_id=None):
        """
        Get all active videos for a skill.
        
        Args:
            skill_id: ID of the skill
            student_id: Optional student ID to include viewing data
            
        Returns:
            list: List of VideoTutorial objects
        """
        videos = VideoTutorial.query.filter_by(
            skill_id=skill_id,
            is_active=True
        ).order_by(VideoTutorial.sequence_order).all()
        
        return [video.to_dict(student_id=student_id) for video in videos]
    
    @staticmethod
    def get_video_by_id(video_id, student_id=None):
        """
        Get a specific video by ID.
        
        Args:
            video_id: ID of the video
            student_id: Optional student ID to include viewing data
            
        Returns:
            dict: Video data
        """
        video = VideoTutorial.query.get(video_id)
        if not video:
            return None
        
        return video.to_dict(student_id=student_id)
    
    @staticmethod
    def start_video_view(video_id, student_id):
        """
        Record that a student started watching a video.
        
        Args:
            video_id: ID of the video
            student_id: ID of the student
            
        Returns:
            VideoView: Video view record
        """
        # Check if view already exists
        view = VideoView.query.filter_by(
            video_id=video_id,
            student_id=student_id
        ).first()
        
        if view:
            # Increment view count and update timestamp
            view.view_count += 1
            view.last_watched_at = datetime.utcnow()
        else:
            # Create new view record
            view = VideoView(
                video_id=video_id,
                student_id=student_id,
                view_count=1
            )
            db.session.add(view)
        
        db.session.commit()
        return view
    
    @staticmethod
    def update_video_progress(video_id, student_id, watch_time, percentage):
        """
        Update viewing progress for a video.
        
        Args:
            video_id: ID of the video
            student_id: ID of the student
            watch_time: Total watch time in seconds
            percentage: Completion percentage (0-100)
            
        Returns:
            VideoView: Updated view record
        """
        view = VideoView.query.filter_by(
            video_id=video_id,
            student_id=student_id
        ).first()
        
        if not view:
            # Create view if doesn't exist
            view = VideoService.start_video_view(video_id, student_id)
        
        view.update_progress(watch_time, percentage)
        db.session.commit()
        
        return view
    
    @staticmethod
    def complete_video(video_id, student_id):
        """
        Mark a video as completed.
        
        Args:
            video_id: ID of the video
            student_id: ID of the student
            
        Returns:
            VideoView: Updated view record
        """
        view = VideoView.query.filter_by(
            video_id=video_id,
            student_id=student_id
        ).first()
        
        if not view:
            view = VideoService.start_video_view(video_id, student_id)
        
        if not view.completed:
            view.completed = True
            view.completed_at = datetime.utcnow()
            view.completion_percentage = 100.0
            db.session.commit()
        
        return view
    
    @staticmethod
    def get_student_video_stats(student_id):
        """
        Get video viewing statistics for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            dict: Video statistics
        """
        views = VideoView.query.filter_by(student_id=student_id).all()
        
        total_videos_watched = len(views)
        total_videos_completed = len([v for v in views if v.completed])
        total_watch_time = sum(v.watch_time_seconds for v in views)
        
        return {
            'total_videos_watched': total_videos_watched,
            'total_videos_completed': total_videos_completed,
            'total_watch_time_seconds': total_watch_time,
            'total_watch_time_minutes': round(total_watch_time / 60, 1),
            'completion_rate': round((total_videos_completed / total_videos_watched * 100), 1) if total_videos_watched > 0 else 0
        }
    
    @staticmethod
    def get_recent_videos(student_id, limit=5):
        """
        Get recently watched videos for a student.
        
        Args:
            student_id: ID of the student
            limit: Maximum number of videos to return
            
        Returns:
            list: List of recently watched videos
        """
        views = VideoView.query.filter_by(
            student_id=student_id
        ).order_by(VideoView.last_watched_at.desc()).limit(limit).all()
        
        result = []
        for view in views:
            video = VideoTutorial.query.get(view.video_id)
            if video:
                video_data = video.to_dict(student_id=student_id)
                result.append(video_data)
        
        return result
    
    @staticmethod
    def get_recommended_videos(student_id, limit=5):
        """
        Get recommended videos for a student based on their learning path.
        
        Args:
            student_id: ID of the student
            limit: Maximum number of videos to return
            
        Returns:
            list: List of recommended videos
        """
        from src.models.learning_path import LearningPath
        
        # Get student's current learning path (non-mastered skills)
        learning_path = LearningPath.query.filter_by(
            student_id=student_id,
            mastery_achieved=False
        ).order_by(LearningPath.sequence_order).limit(limit).all()
        
        recommended = []
        for item in learning_path:
            # Get videos for this skill that student hasn't watched
            videos = VideoTutorial.query.filter_by(
                skill_id=item.skill_id,
                is_active=True
            ).order_by(VideoTutorial.sequence_order).all()
            
            for video in videos:
                # Check if student has watched this video
                view = VideoView.query.filter_by(
                    video_id=video.id,
                    student_id=student_id
                ).first()
                
                if not view or not view.completed:
                    recommended.append(video.to_dict(student_id=student_id))
                    if len(recommended) >= limit:
                        return recommended
        
        return recommended

