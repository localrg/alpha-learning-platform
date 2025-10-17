"""
Review Session model for tracking skill review sessions (spaced repetition).
"""
from src.database import db
from datetime import datetime


class ReviewSession(db.Model):
    """
    Represents a review session for a previously mastered skill.
    Used for spaced repetition to maintain long-term retention.
    """
    __tablename__ = 'review_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    
    # Session details
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)  # Percentage
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Review tracking
    review_number = db.Column(db.Integer, default=1)  # 1st review, 2nd review, etc.
    passed = db.Column(db.Boolean, default=False)  # Did they maintain mastery (>= 80%)?
    
    # Relationships
    student = db.relationship('Student', backref='review_sessions')
    learning_path = db.relationship('LearningPath', backref='review_sessions')
    skill = db.relationship('Skill', backref='review_sessions')
    
    def complete_review(self, correct, total):
        """Complete the review session and calculate results."""
        self.questions_answered = total
        self.correct_answers = correct
        
        if total > 0:
            self.accuracy = (correct / total) * 100
        
        # Pass threshold is 80% for reviews (lower than 90% for initial mastery)
        self.passed = self.accuracy >= 80.0
        self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'learning_path_id': self.learning_path_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy': round(self.accuracy, 1),
            'review_number': self.review_number,
            'passed': self.passed,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

