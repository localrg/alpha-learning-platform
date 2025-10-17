"""
Teacher model for teacher profiles and information.
"""
from datetime import datetime
from src.database import db


class Teacher(db.Model):
    """
    Teacher profile linked to a user account.
    Stores teacher information and preferences.
    """
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    school = db.Column(db.String(200))
    subject = db.Column(db.String(100))
    grade_levels = db.Column(db.String(50))  # e.g., "3,4,5"
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200), default='👨‍🏫')
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    user = db.relationship('User', backref=db.backref('teacher', uselist=False))

    def __repr__(self):
        return f'<Teacher {self.name}>'

    def to_dict(self):
        """Convert teacher to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'school': self.school,
            'subject': self.subject,
            'grade_levels': self.grade_levels.split(',') if self.grade_levels else [],
            'bio': self.bio,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_profile(self, **kwargs):
        """Update teacher profile information."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'user_id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()

