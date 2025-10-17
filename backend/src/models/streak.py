"""
Streak Tracking models for login and practice consistency.
"""
from datetime import datetime, date
from src.database import db


class StreakTracking(db.Model):
    """
    Tracks login and practice streaks for students.
    """
    __tablename__ = 'streak_tracking'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    
    # Login streak
    login_streak = db.Column(db.Integer, nullable=False, default=0)
    login_streak_best = db.Column(db.Integer, nullable=False, default=0)
    last_login_date = db.Column(db.Date, nullable=True)
    
    # Practice streak
    practice_streak = db.Column(db.Integer, nullable=False, default=0)
    practice_streak_best = db.Column(db.Integer, nullable=False, default=0)
    last_practice_date = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='streak_tracking')

    def __repr__(self):
        return f'<StreakTracking Student{self.student_id} Login:{self.login_streak} Practice:{self.practice_streak}>'

    def to_dict(self):
        """Convert streak tracking to dictionary for JSON serialization."""
        return {
            'student_id': self.student_id,
            'login_streak': self.login_streak,
            'login_streak_best': self.login_streak_best,
            'last_login_date': self.last_login_date.isoformat() if self.last_login_date else None,
            'practice_streak': self.practice_streak,
            'practice_streak_best': self.practice_streak_best,
            'last_practice_date': self.last_practice_date.isoformat() if self.last_practice_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

