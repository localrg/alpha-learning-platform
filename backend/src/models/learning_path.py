"""
Learning Path model for tracking student progress through skills.
"""
from src.database import db
from datetime import datetime


class LearningPath(db.Model):
    """
    Represents a student's personalized learning path.
    """
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    
    # Status: 'not_started', 'in_progress', 'mastered', 'needs_review'
    status = db.Column(db.String(20), default='not_started')
    
    # Progress tracking
    attempts = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    current_accuracy = db.Column(db.Float, default=0.0)  # Percentage
    
    # Mastery tracking
    mastery_achieved = db.Column(db.Boolean, default=False)
    mastery_date = db.Column(db.DateTime, nullable=True)
    
    # Priority and sequencing
    priority = db.Column(db.Integer, default=0)  # Lower number = higher priority
    sequence_order = db.Column(db.Integer, nullable=True)  # Order in learning path
    
    # Timestamps
    started_at = db.Column(db.DateTime, nullable=True)
    last_practiced = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='learning_path')
    skill = db.relationship('Skill', backref='learning_paths')
    
    def update_progress(self, correct, total):
        """Update progress after practice session."""
        self.attempts += 1
        self.correct_answers += correct
        self.total_questions += total
        
        if self.total_questions > 0:
            self.current_accuracy = (self.correct_answers / self.total_questions) * 100
        
        self.last_practiced = datetime.utcnow()
        
        # Check if mastery achieved
        if not self.mastery_achieved and self.current_accuracy >= 90 and self.total_questions >= 5:
            self.mastery_achieved = True
            self.mastery_date = datetime.utcnow()
            self.status = 'mastered'
        elif self.status == 'not_started':
            self.status = 'in_progress'
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'status': self.status,
            'attempts': self.attempts,
            'current_accuracy': round(self.current_accuracy, 1),
            'mastery_achieved': self.mastery_achieved,
            'mastery_date': self.mastery_date.isoformat() if self.mastery_date else None,
            'priority': self.priority,
            'sequence_order': self.sequence_order,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_practiced': self.last_practiced.isoformat() if self.last_practiced else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

