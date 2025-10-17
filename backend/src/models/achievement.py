"""
Achievement and badge models for gamification.
"""
from datetime import datetime
from src.database import db


class Achievement(db.Model):
    """Achievement definition model."""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'practice', 'mastery', 'accuracy', etc.
    tier = db.Column(db.String(20), nullable=False)  # 'bronze', 'silver', 'gold', 'platinum', 'diamond'
    requirement_type = db.Column(db.String(50), nullable=False)  # 'count', 'streak', 'percentage', 'time'
    requirement_value = db.Column(db.Integer, nullable=False)  # Target value
    icon_emoji = db.Column(db.String(10), nullable=False)
    xp_reward = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student_achievements = db.relationship('StudentAchievement', backref='achievement', lazy=True)
    
    def to_dict(self):
        """Convert achievement to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'tier': self.tier,
            'requirement_type': self.requirement_type,
            'requirement_value': self.requirement_value,
            'icon_emoji': self.icon_emoji,
            'xp_reward': self.xp_reward,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StudentAchievement(db.Model):
    """Student progress toward achievements."""
    __tablename__ = 'student_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    progress = db.Column(db.Integer, nullable=False, default=0)
    unlocked_at = db.Column(db.DateTime, nullable=True)
    is_displayed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('achievements', lazy=True))
    progress_logs = db.relationship('AchievementProgressLog', backref='student_achievement', lazy=True)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('student_id', 'achievement_id', name='unique_student_achievement'),
    )
    
    def to_dict(self, include_achievement=True):
        """Convert student achievement to dictionary."""
        result = {
            'id': self.id,
            'student_id': self.student_id,
            'achievement_id': self.achievement_id,
            'progress': self.progress,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'is_displayed': self.is_displayed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_achievement and self.achievement:
            result['achievement'] = self.achievement.to_dict()
            result['progress_percentage'] = (self.progress / self.achievement.requirement_value * 100) if self.achievement.requirement_value > 0 else 0
            result['is_unlocked'] = self.unlocked_at is not None
        
        return result


class AchievementProgressLog(db.Model):
    """Log of achievement progress changes."""
    __tablename__ = 'achievement_progress_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    student_achievement_id = db.Column(db.Integer, db.ForeignKey('student_achievements.id'), nullable=True)
    progress_delta = db.Column(db.Integer, nullable=False)
    new_progress = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('achievement_logs', lazy=True))
    achievement = db.relationship('Achievement', backref=db.backref('progress_logs', lazy=True))
    
    def to_dict(self):
        """Convert log to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'achievement_id': self.achievement_id,
            'progress_delta': self.progress_delta,
            'new_progress': self.new_progress,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

