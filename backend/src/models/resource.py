"""
Resource models for storing downloadable educational materials.
"""
from datetime import datetime
from src.database import db


class Resource(db.Model):
    """
    Represents a downloadable educational resource (worksheet, reference guide, etc.).
    """
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(db.String(50), nullable=False)  # 'worksheet', 'reference', 'practice', 'study_guide', 'answer_key'
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)  # Nullable for general resources
    grade_level = db.Column(db.Integer, nullable=False)  # 3-8
    difficulty = db.Column(db.String(20), nullable=False, default='medium')  # 'easy', 'medium', 'hard'
    file_url = db.Column(db.String(500), nullable=False)  # URL to downloadable file
    file_type = db.Column(db.String(10), nullable=False)  # 'pdf', 'docx', 'png', 'jpg'
    file_size_kb = db.Column(db.Integer, nullable=False)  # File size in KB
    thumbnail_url = db.Column(db.String(500), nullable=True)  # Optional thumbnail
    tags = db.Column(db.JSON, nullable=True)  # Array of tags for search
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    download_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skill = db.relationship('Skill', backref=db.backref('resources', lazy=True))

    def __repr__(self):
        return f'<Resource {self.id} - {self.title}>'

    def to_dict(self):
        """Convert resource to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'resource_type': self.resource_type,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'grade_level': self.grade_level,
            'difficulty': self.difficulty,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_size_kb': self.file_size_kb,
            'thumbnail_url': self.thumbnail_url,
            'tags': self.tags or [],
            'is_active': self.is_active,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ResourceDownload(db.Model):
    """
    Tracks when students download resources.
    Used for analytics and understanding resource usage.
    """
    __tablename__ = 'resource_downloads'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    downloaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    download_method = db.Column(db.String(20), nullable=False, default='direct')  # 'direct', 'print', 'email'

    # Relationships
    student = db.relationship('Student', backref=db.backref('resource_downloads', lazy=True))
    resource = db.relationship('Resource', backref=db.backref('downloads', lazy=True))

    def __repr__(self):
        return f'<ResourceDownload {self.id} - Student{self.student_id} Resource{self.resource_id}>'

    def to_dict(self):
        """Convert download to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'resource_id': self.resource_id,
            'resource': self.resource.to_dict() if self.resource else None,
            'downloaded_at': self.downloaded_at.isoformat() if self.downloaded_at else None,
            'download_method': self.download_method
        }

