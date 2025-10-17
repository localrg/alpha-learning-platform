"""
Hint models for storing and managing progressive hints for questions.
"""
from src.database import db
from datetime import datetime


class Hint(db.Model):
    """
    Represents a hint for a specific question.
    Hints are progressive (levels 1-4) to support scaffolded learning.
    """
    __tablename__ = 'hints'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    # Hint content
    hint_level = db.Column(db.Integer, nullable=False)  # 1-4
    hint_text = db.Column(db.Text, nullable=False)
    hint_type = db.Column(db.String(20), default='text')  # 'text', 'visual', 'example'
    
    # Optional visual hint
    image_url = db.Column(db.String(500), nullable=True)
    
    # Metadata
    sequence_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question', backref='hints')
    usages = db.relationship('HintUsage', backref='hint', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'hint_level': self.hint_level,
            'hint_text': self.hint_text,
            'hint_type': self.hint_type,
            'image_url': self.image_url,
            'sequence_order': self.sequence_order
        }


class HintUsage(db.Model):
    """
    Tracks student usage of hints for analytics and personalization.
    """
    __tablename__ = 'hint_usages'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    hint_id = db.Column(db.Integer, db.ForeignKey('hints.id'), nullable=False)
    
    # Usage tracking
    hint_level = db.Column(db.Integer, nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    helpful = db.Column(db.Boolean, nullable=True)  # Student feedback
    
    # Context
    attempt_number = db.Column(db.Integer, default=1)
    time_before_hint = db.Column(db.Integer, nullable=True)  # Seconds
    
    # Outcome
    answered_correctly = db.Column(db.Boolean, nullable=True)
    attempts_after_hint = db.Column(db.Integer, nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='hint_usages')
    question = db.relationship('Question', backref='hint_usages')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'question_id': self.question_id,
            'hint_id': self.hint_id,
            'hint_level': self.hint_level,
            'viewed_at': self.viewed_at.isoformat(),
            'helpful': self.helpful,
            'attempt_number': self.attempt_number,
            'time_before_hint': self.time_before_hint,
            'answered_correctly': self.answered_correctly,
            'attempts_after_hint': self.attempts_after_hint
        }

