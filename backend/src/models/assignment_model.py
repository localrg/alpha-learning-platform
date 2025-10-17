"""
Assignment models for teacher-created practice assignments
"""
from src.database import db
from datetime import datetime


class Assignment(db.Model):
    """Teacher-created practice assignment"""
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'), nullable=True)  # NULL for individual
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    skill_ids = db.Column(db.JSON, nullable=False)  # Array of skill IDs
    question_count = db.Column(db.Integer, nullable=False, default=10)
    difficulty = db.Column(db.String(20), default='adaptive')  # 'easy', 'medium', 'hard', 'adaptive'
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='created_assignments')
    class_group = db.relationship('ClassGroup', backref='assignments')
    student_assignments = db.relationship('AssignmentStudent', back_populates='assignment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Assignment {self.id}: {self.title}>'
    
    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'class_id': self.class_id,
            'title': self.title,
            'description': self.description,
            'skill_ids': self.skill_ids or [],
            'question_count': self.question_count,
            'difficulty': self.difficulty,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class AssignmentStudent(db.Model):
    """Student assignment tracking"""
    __tablename__ = 'assignment_students'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='assigned')  # 'assigned', 'in_progress', 'completed'
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    questions_answered = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    time_spent = db.Column(db.Integer, default=0)  # seconds
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment = db.relationship('Assignment', back_populates='student_assignments')
    student = db.relationship('Student', backref='assignments')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='unique_assignment_student'),
    )
    
    def __repr__(self):
        return f'<AssignmentStudent Assignment{self.assignment_id} Student{self.student_id} {self.status}>'
    
    def to_dict(self):
        """Convert assignment student to dictionary"""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'questions_answered': self.questions_answered,
            'questions_correct': self.questions_correct,
            'accuracy': round(self.accuracy, 2),
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

