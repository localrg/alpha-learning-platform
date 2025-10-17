"""
Daily Challenge models for time-limited practice challenges.
"""
from datetime import datetime, timedelta
from src.database import db


class DailyChallenge(db.Model):
    """
    Represents a daily challenge for a student.
    Challenges reset every 24 hours and provide bonus XP.
    """
    __tablename__ = 'daily_challenges'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Challenge details
    challenge_type = db.Column(db.String(50), nullable=False)  # question_marathon, skill_focus, perfect_streak, etc.
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    description = db.Column(db.String(200), nullable=False)
    
    # Target and progress
    target_value = db.Column(db.Integer, nullable=False)  # Number to achieve
    current_progress = db.Column(db.Integer, nullable=False, default=0)
    target_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)  # For skill_focus type
    time_limit_minutes = db.Column(db.Integer, nullable=True)  # For speed_challenge type
    
    # Rewards
    bonus_xp = db.Column(db.Integer, nullable=False)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='active')  # active, completed, expired
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)  # When student first made progress
    
    # Relationships
    student = db.relationship('Student', backref='daily_challenges')
    target_skill = db.relationship('Skill', foreign_keys=[target_skill_id])

    def __repr__(self):
        return f'<DailyChallenge {self.challenge_type} for Student{self.student_id}>'

    def to_dict(self):
        """Convert challenge to dictionary for JSON serialization."""
        time_remaining = None
        if self.status == 'active' and self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            if delta.total_seconds() > 0:
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                time_remaining = f"{hours}h {minutes}m"
        
        return {
            'id': self.id,
            'type': self.challenge_type,
            'difficulty': self.difficulty,
            'description': self.description,
            'target': self.target_value,
            'progress': self.current_progress,
            'bonus_xp': self.bonus_xp,
            'status': self.status,
            'completion_percentage': int((self.current_progress / self.target_value) * 100) if self.target_value > 0 else 0,
            'time_remaining': time_remaining,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'target_skill_id': self.target_skill_id,
            'time_limit_minutes': self.time_limit_minutes
        }

    @property
    def is_expired(self):
        """Check if challenge has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_completed(self):
        """Check if challenge is completed."""
        return self.status == 'completed'

    @property
    def progress_percentage(self):
        """Get progress as percentage."""
        if self.target_value == 0:
            return 0
        return int((self.current_progress / self.target_value) * 100)

