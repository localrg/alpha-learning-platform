"""
Activity Feed Models
Handles social activity feed for student updates
"""

from datetime import datetime
from src.database import db


class ActivityFeed(db.Model):
    """Model for activity feed entries"""
    __tablename__ = 'activity_feed'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Activity details
    activity_type = db.Column(db.String(50), nullable=False)
    # Types: 'skill_mastery', 'level_up', 'achievement_unlock', 'challenge_complete',
    #        'streak_milestone', 'friend_added', 'class_joined', 'practice_session'
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Related entities (optional, depends on activity type)
    skill_id = db.Column(db.Integer)
    achievement_id = db.Column(db.Integer)
    challenge_id = db.Column(db.Integer)
    class_id = db.Column(db.Integer)
    
    # Metadata
    xp_earned = db.Column(db.Integer, default=0)
    level_reached = db.Column(db.Integer)
    streak_days = db.Column(db.Integer)
    accuracy = db.Column(db.Float)
    questions_answered = db.Column(db.Integer)
    
    # Visibility
    visibility = db.Column(db.String(20), default='friends')  # 'public', 'friends', 'class', 'private'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='activities')
    
    def to_dict(self, include_student=True):
        """Convert activity to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'activity_type': self.activity_type,
            'title': self.title,
            'description': self.description,
            'skill_id': self.skill_id,
            'achievement_id': self.achievement_id,
            'challenge_id': self.challenge_id,
            'class_id': self.class_id,
            'xp_earned': self.xp_earned,
            'level_reached': self.level_reached,
            'streak_days': self.streak_days,
            'accuracy': self.accuracy,
            'questions_answered': self.questions_answered,
            'visibility': self.visibility,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'time_ago': self._get_time_ago()
        }
        
        if include_student and self.student:
            # Get progress data if available
            progress = self.student.progress if hasattr(self.student, 'progress') else None
            data['student'] = {
                'id': self.student.id,
                'name': self.student.name,
                'avatar': self.student.avatar,
                'level': progress.current_level if progress else 1,
                'total_xp': progress.total_xp if progress else 0
            }
        
        return data
    
    def _get_time_ago(self):
        """Calculate human-readable time ago"""
        if not self.created_at:
            return 'Unknown'
        
        now = datetime.utcnow()
        diff = now - self.created_at
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{days} day{"s" if days != 1 else ""} ago'
        else:
            weeks = int(seconds / 604800)
            return f'{weeks} week{"s" if weeks != 1 else ""} ago'

