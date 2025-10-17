"""
Video Tutorial models for storing video content and tracking student viewing.
"""
from src.database import db
from datetime import datetime


class VideoTutorial(db.Model):
    """
    Represents an instructional video tutorial for a skill.
    Supports YouTube, Vimeo, and direct video URLs.
    """
    __tablename__ = 'video_tutorials'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    
    # Video information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(500), nullable=False)  # Original URL
    video_platform = db.Column(db.String(20), nullable=False)  # 'youtube', 'vimeo', 'direct'
    video_id = db.Column(db.String(100), nullable=False)  # Platform-specific ID
    duration_seconds = db.Column(db.Integer, default=0)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    
    # Metadata
    difficulty_level = db.Column(db.String(20), default='beginner')  # 'beginner', 'intermediate', 'advanced'
    sequence_order = db.Column(db.Integer, default=0)  # Order within skill
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skill = db.relationship('Skill', backref='video_tutorials')
    views = db.relationship('VideoView', backref='video', lazy=True, cascade='all, delete-orphan')
    
    def get_embed_url(self):
        """Get the embeddable URL for the video."""
        if self.video_platform == 'youtube':
            return f"https://www.youtube.com/embed/{self.video_id}"
        elif self.video_platform == 'vimeo':
            return f"https://player.vimeo.com/video/{self.video_id}"
        else:
            return self.video_url
    
    def to_dict(self, student_id=None):
        """Convert to dictionary with optional student viewing data."""
        data = {
            'id': self.id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'title': self.title,
            'description': self.description,
            'video_url': self.video_url,
            'embed_url': self.get_embed_url(),
            'platform': self.video_platform,
            'video_id': self.video_id,
            'duration': self.duration_seconds,
            'thumbnail_url': self.thumbnail_url,
            'difficulty': self.difficulty_level,
            'sequence_order': self.sequence_order,
            'created_at': self.created_at.isoformat()
        }
        
        # Add student viewing data if student_id provided
        if student_id:
            view = VideoView.query.filter_by(
                video_id=self.id,
                student_id=student_id
            ).first()
            
            if view:
                data['watched'] = True
                data['completion_percentage'] = view.completion_percentage
                data['completed'] = view.completed
                data['last_watched'] = view.last_watched_at.isoformat() if view.last_watched_at else None
            else:
                data['watched'] = False
                data['completion_percentage'] = 0
                data['completed'] = False
                data['last_watched'] = None
        
        return data


class VideoView(db.Model):
    """
    Tracks student viewing progress for video tutorials.
    """
    __tablename__ = 'video_views'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video_tutorials.id'), nullable=False)
    
    # Viewing progress
    watch_time_seconds = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Float, default=0.0)
    view_count = db.Column(db.Integer, default=0)  # Number of times started
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_watched_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='video_views')
    
    def update_progress(self, watch_time, percentage):
        """Update viewing progress."""
        self.watch_time_seconds = watch_time
        self.completion_percentage = percentage
        self.last_watched_at = datetime.utcnow()
        
        # Mark as completed if watched >= 90%
        if percentage >= 90 and not self.completed:
            self.completed = True
            self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'video_id': self.video_id,
            'watch_time_seconds': self.watch_time_seconds,
            'completed': self.completed,
            'completion_percentage': round(self.completion_percentage, 1),
            'view_count': self.view_count,
            'started_at': self.started_at.isoformat(),
            'last_watched_at': self.last_watched_at.isoformat() if self.last_watched_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

