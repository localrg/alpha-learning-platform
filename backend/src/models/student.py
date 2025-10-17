"""
Student model for storing student profile information.
Each user can have one student profile.
"""
from datetime import datetime
from src.database import db


class Student(db.Model):
    """
    Student profile linked to a user account.
    Stores student information and learning preferences.
    """
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer, nullable=False)  # 3-8 for grades 3rd-8th
    
    # Profile fields
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True, default='😊')  # Emoji or image URL
    profile_visibility = db.Column(db.String(20), nullable=False, default='public')  # public, friends, private
    show_stats = db.Column(db.Boolean, nullable=False, default=True)
    show_achievements = db.Column(db.Boolean, nullable=False, default=True)
    show_activity = db.Column(db.Boolean, nullable=False, default=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    user = db.relationship('User', backref=db.backref('student', uselist=False))

    def __repr__(self):
        return f'<Student {self.name} (Grade {self.grade})>'

    def to_dict(self):
        """Convert student to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'grade': self.grade,
            'bio': self.bio,
            'avatar': self.avatar,
            'profile_visibility': self.profile_visibility,
            'show_stats': self.show_stats,
            'show_achievements': self.show_achievements,
            'show_activity': self.show_activity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_profile(self, name=None, grade=None):
        """Update student profile information."""
        if name is not None:
            self.name = name
        if grade is not None:
            self.grade = grade
        self.updated_at = datetime.utcnow()
        db.session.commit()

