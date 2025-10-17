"""
Class Group models for organizing students into classes.
"""
from datetime import datetime
from src.database import db


class ClassGroup(db.Model):
    """
    Class/Group for organizing students.
    Created by teachers, joined by students via invite code.
    """
    __tablename__ = 'class_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    grade_level = db.Column(db.Integer, nullable=False)  # 3-8
    invite_code = db.Column(db.String(6), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = db.relationship('User', backref='classes_created')
    memberships = db.relationship('ClassMembership', backref='class_group', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ClassGroup {self.name}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'grade_level': self.grade_level,
            'invite_code': self.invite_code,
            'created_at': self.created_at.isoformat(),
            'member_count': len(self.memberships)
        }


class ClassMembership(db.Model):
    """
    Membership linking students to classes.
    """
    __tablename__ = 'class_memberships'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'teacher' or 'student'
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref='class_memberships')

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('class_id', 'student_id', name='unique_class_student'),
    )

    def __repr__(self):
        return f'<ClassMembership class={self.class_id} student={self.student_id}>'

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'student_id': self.student_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat()
        }

