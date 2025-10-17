"""
Worked Solution models for storing and tracking step-by-step solutions.
"""
from datetime import datetime
from src.database import db


class WorkedSolution(db.Model):
    """
    Represents a complete worked solution for a question.
    Contains step-by-step explanation of how to solve the problem.
    """
    __tablename__ = 'worked_solutions'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    solution_type = db.Column(db.String(50), nullable=False, default='step_by_step')  # 'step_by_step', 'visual', 'alternative'
    steps = db.Column(db.JSON, nullable=False)  # Array of solution steps
    difficulty_level = db.Column(db.String(20), nullable=False, default='beginner')  # 'beginner', 'intermediate', 'advanced'
    show_after_attempts = db.Column(db.Integer, nullable=False, default=1)  # Minimum attempts before showing
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    question = db.relationship('Question', backref=db.backref('worked_solutions', lazy=True))

    def __repr__(self):
        return f'<WorkedSolution {self.id} for Q{self.question_id}>'

    def to_dict(self):
        """Convert solution to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'solution_type': self.solution_type,
            'steps': self.steps,
            'difficulty_level': self.difficulty_level,
            'show_after_attempts': self.show_after_attempts,
            'total_steps': len(self.steps) if self.steps else 0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SolutionView(db.Model):
    """
    Tracks when students view worked solutions.
    Used for analytics and understanding solution effectiveness.
    """
    __tablename__ = 'solution_views'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    solution_id = db.Column(db.Integer, db.ForeignKey('worked_solutions.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_spent_seconds = db.Column(db.Integer, nullable=True)  # How long they viewed it
    steps_viewed = db.Column(db.JSON, nullable=True)  # Array of step numbers viewed
    helpful = db.Column(db.Boolean, nullable=True)  # Student feedback
    understood = db.Column(db.Boolean, nullable=True)  # Self-assessment

    # Relationships
    student = db.relationship('Student', backref=db.backref('solution_views', lazy=True))
    question = db.relationship('Question', backref=db.backref('solution_views', lazy=True))
    solution = db.relationship('WorkedSolution', backref=db.backref('views', lazy=True))

    def __repr__(self):
        return f'<SolutionView {self.id} - Student{self.student_id} Q{self.question_id}>'

    def to_dict(self):
        """Convert view to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'question_id': self.question_id,
            'solution_id': self.solution_id,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'time_spent_seconds': self.time_spent_seconds,
            'steps_viewed': self.steps_viewed,
            'helpful': self.helpful,
            'understood': self.understood
        }

