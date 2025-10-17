"""
Parent Communication and Goal Models
Database models for parent-teacher messaging and goal setting
"""
from src.database import db
from datetime import datetime


class ParentTeacherMessage(db.Model):
    """Parent-teacher message model"""
    __tablename__ = 'parent_teacher_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # question, inquiry, concern, meeting, appreciation
    parent_read = db.Column(db.Boolean, default=True)  # Parent always reads their sent message
    teacher_read = db.Column(db.Boolean, default=False)
    replied_to_id = db.Column(db.Integer, db.ForeignKey('parent_teacher_messages.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('Parent', backref='messages_sent')
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    student = db.relationship('Student', backref='parent_teacher_messages')
    replied_to = db.relationship('ParentTeacherMessage', remote_side=[id], backref='replies')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'subject': self.subject,
            'message': self.message,
            'message_type': self.message_type,
            'parent_read': self.parent_read,
            'teacher_read': self.teacher_read,
            'replied_to_id': self.replied_to_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'parent_name': self.parent.name if self.parent else None,
            'teacher_name': self.teacher.username if self.teacher else None,
            'student_name': self.student.name if self.student else None
        }


class Goal(db.Model):
    """Student goal model"""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by_type = db.Column(db.String(20), nullable=False)  # parent, student, teacher
    goal_type = db.Column(db.String(50), nullable=False)  # skill_mastery, practice_time, accuracy, assignments, streak, custom
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, default=0.0)
    progress_percent = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For skill_mastery goals
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='goals')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    skill = db.relationship('Skill', foreign_keys=[skill_id])
    notes = db.relationship('GoalNote', back_populates='goal', cascade='all, delete-orphan')
    progress_history = db.relationship('GoalProgress', back_populates='goal', cascade='all, delete-orphan', order_by='GoalProgress.recorded_at.desc()')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'created_by_id': self.created_by_id,
            'created_by_type': self.created_by_type,
            'goal_type': self.goal_type,
            'title': self.title,
            'description': self.description,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'progress_percent': round(self.progress_percent, 1),
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'student_name': self.student.name if self.student else None,
            'created_by_name': self.created_by.username if self.created_by else None
        }


class GoalNote(db.Model):
    """Goal note/encouragement model"""
    __tablename__ = 'goal_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # parent, student, teacher
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    goal = db.relationship('Goal', back_populates='notes')
    user = db.relationship('User')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.username if self.user else None
        }


class GoalProgress(db.Model):
    """Goal progress tracking model"""
    __tablename__ = 'goal_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    progress_percent = db.Column(db.Float, nullable=False)
    note = db.Column(db.Text, nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    goal = db.relationship('Goal', back_populates='progress_history')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'value': self.value,
            'progress_percent': round(self.progress_percent, 1),
            'note': self.note,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }

