"""
Intervention models for teacher actions and messaging
"""
from src.database import db
from datetime import datetime


class TeacherMessage(db.Model):
    """Messages sent from teachers to students"""
    __tablename__ = 'teacher_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('message_templates.id'), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='sent_messages')
    student = db.relationship('Student', backref='received_messages')
    template = db.relationship('MessageTemplate', backref='messages')
    
    def __repr__(self):
        return f'<TeacherMessage {self.id} from Teacher{self.teacher_id} to Student{self.student_id}>'
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'message': self.message,
            'template_id': self.template_id,
            'sent_at': self.sent_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_read': self.is_read
        }


class MessageTemplate(db.Model):
    """Pre-written message templates for common situations"""
    __tablename__ = 'message_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # inactive, struggling, overdue, encouragement
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.JSON, nullable=True)  # List of variables like {student_name}, {skill_name}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MessageTemplate {self.id}: {self.title}>'
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'variables': self.variables or []
        }


class Intervention(db.Model):
    """Teacher interventions for student issues"""
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    intervention_type = db.Column(db.String(50), nullable=False)  # message, assignment, meeting, parent_notification
    action_taken = db.Column(db.Text, nullable=False)
    resolution_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    is_resolved = db.Column(db.Boolean, default=False)
    effectiveness_rating = db.Column(db.Integer, nullable=True)  # 1-5 rating
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='interventions')
    student = db.relationship('Student', backref='interventions')
    
    def __repr__(self):
        return f'<Intervention {self.id} {self.intervention_type} for Student{self.student_id}>'
    
    def to_dict(self):
        """Convert intervention to dictionary"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'intervention_type': self.intervention_type,
            'action_taken': self.action_taken,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'is_resolved': self.is_resolved,
            'effectiveness_rating': self.effectiveness_rating
        }


class Meeting(db.Model):
    """Scheduled meetings between teachers and students"""
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    meeting_type = db.Column(db.String(50), nullable=False)  # one_on_one, parent_conference, group
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    location = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='meetings')
    student = db.relationship('Student', backref='meetings')
    
    def __repr__(self):
        return f'<Meeting {self.id} {self.meeting_type} at {self.scheduled_at}>'
    
    def to_dict(self):
        """Convert meeting to dictionary"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'meeting_type': self.meeting_type,
            'scheduled_at': self.scheduled_at.isoformat(),
            'duration_minutes': self.duration_minutes,
            'location': self.location,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

