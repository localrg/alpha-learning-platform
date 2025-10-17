"""
Student Session model for real-time activity tracking
"""
from src.database import db
from datetime import datetime


class StudentSession(db.Model):
    """Track student practice sessions in real-time"""
    __tablename__ = 'student_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_activity_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    questions_answered = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='sessions')
    skill = db.relationship('Skill', backref='practice_sessions')
    
    def __repr__(self):
        return f'<StudentSession {self.id} Student{self.student_id} {"Active" if self.is_active else "Ended"}>'
    
    def to_dict(self):
        """Convert session to dictionary"""
        duration = 0
        if self.ended_at:
            duration = int((self.ended_at - self.started_at).total_seconds())
        elif self.is_active:
            duration = int((datetime.utcnow() - self.started_at).total_seconds())
        
        return {
            'id': self.id,
            'student_id': self.student_id,
            'skill_id': self.skill_id,
            'started_at': self.started_at.isoformat(),
            'last_activity_at': self.last_activity_at.isoformat(),
            'questions_answered': self.questions_answered,
            'questions_correct': self.questions_correct,
            'accuracy': round(self.accuracy, 2),
            'is_active': self.is_active,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration': duration
        }

