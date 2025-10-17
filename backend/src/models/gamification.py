"""
Gamification models for points, levels, and rewards system.
"""
from datetime import datetime
from src.database import db
import math


class StudentProgress(db.Model):
    """
    Tracks student's overall gamification progress.
    Stores XP, level, and progression data.
    """
    __tablename__ = 'student_progress'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    total_xp = db.Column(db.Integer, nullable=False, default=0)
    current_level = db.Column(db.Integer, nullable=False, default=1)
    xp_to_next_level = db.Column(db.Integer, nullable=False, default=100)
    level_title = db.Column(db.String(50), nullable=False, default='Novice')
    xp_multiplier = db.Column(db.Float, nullable=False, default=1.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('progress', uselist=False))

    def __repr__(self):
        return f'<StudentProgress Student{self.student_id} Level{self.current_level}>'

    def to_dict(self):
        """Convert progress to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'total_xp': self.total_xp,
            'current_level': self.current_level,
            'xp_to_next_level': self.xp_to_next_level,
            'level_title': self.level_title,
            'xp_multiplier': self.xp_multiplier,
            'progress_percentage': self.get_progress_percentage(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_progress_percentage(self):
        """Calculate percentage progress to next level."""
        xp_for_current_level = self.calculate_xp_for_level(self.current_level)
        xp_for_next_level = self.calculate_xp_for_level(self.current_level + 1)
        xp_in_current_level = self.total_xp - xp_for_current_level
        xp_needed_for_level = xp_for_next_level - xp_for_current_level
        
        if xp_needed_for_level == 0:
            return 100.0
        
        return round((xp_in_current_level / xp_needed_for_level) * 100, 1)

    @staticmethod
    def calculate_xp_for_level(level):
        """Calculate cumulative XP required to reach a level."""
        if level <= 1:
            return 0
        
        total_xp = 0
        for l in range(2, level + 1):
            total_xp += int(100 * (l ** 1.5))
        
        return total_xp

    @staticmethod
    def get_level_title(level):
        """Get title for a given level."""
        if level < 5:
            return 'Novice'
        elif level < 10:
            return 'Apprentice'
        elif level < 15:
            return 'Practitioner'
        elif level < 20:
            return 'Expert'
        elif level < 25:
            return 'Master'
        elif level < 30:
            return 'Grandmaster'
        elif level < 50:
            return 'Legend'
        else:
            return 'Mythic'


class XPTransaction(db.Model):
    """
    Records individual XP transactions.
    Tracks when and how XP was earned.
    """
    __tablename__ = 'xp_transactions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # question, assessment, review, etc.
    base_xp = db.Column(db.Integer, nullable=False)
    multiplier = db.Column(db.Float, nullable=False, default=1.0)
    bonus_xp = db.Column(db.Integer, nullable=False, default=0)
    total_xp = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)  # Additional context
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('xp_transactions', lazy=True))

    def __repr__(self):
        return f'<XPTransaction {self.id} - {self.total_xp}XP>'

    def to_dict(self):
        """Convert transaction to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'action_type': self.action_type,
            'base_xp': self.base_xp,
            'multiplier': self.multiplier,
            'bonus_xp': self.bonus_xp,
            'total_xp': self.total_xp,
            'description': self.description,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LevelReward(db.Model):
    """
    Defines rewards available at each level.
    Rewards can be titles, badges, avatars, etc.
    """
    __tablename__ = 'level_rewards'

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # title, badge, avatar, multiplier
    reward_value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f'<LevelReward Level{self.level} {self.reward_type}>'

    def to_dict(self):
        """Convert reward to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'level': self.level,
            'reward_type': self.reward_type,
            'reward_value': self.reward_value,
            'description': self.description,
            'is_active': self.is_active
        }


class StudentReward(db.Model):
    """
    Tracks which rewards students have unlocked.
    Links students to their earned rewards.
    """
    __tablename__ = 'student_rewards'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('level_rewards.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_equipped = db.Column(db.Boolean, nullable=False, default=False)  # For cosmetics

    # Relationships
    student = db.relationship('Student', backref=db.backref('rewards', lazy=True))
    reward = db.relationship('LevelReward', backref=db.backref('student_unlocks', lazy=True))

    def __repr__(self):
        return f'<StudentReward Student{self.student_id} Reward{self.reward_id}>'

    def to_dict(self):
        """Convert student reward to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'reward_id': self.reward_id,
            'reward': self.reward.to_dict() if self.reward else None,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'is_equipped': self.is_equipped
        }

