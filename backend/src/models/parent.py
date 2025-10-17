"""
Parent Models
Database models for parent accounts and child linking
"""
from src.database import db
from datetime import datetime


class Parent(db.Model):
    """Parent account model"""
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    notification_preferences = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='parent_profile')
    children = db.relationship('ParentChildLink', back_populates='parent', foreign_keys='ParentChildLink.parent_id')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'notification_preferences': self.notification_preferences or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ParentChildLink(db.Model):
    """Parent-child relationship model"""
    __tablename__ = 'parent_child_links'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    relationship = db.Column(db.String(50), default='parent')  # parent, guardian, etc.
    is_primary_contact = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # active, removed
    linked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('Parent', back_populates='children', foreign_keys=[parent_id])
    student = db.relationship('Student', backref='parent_links')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('parent_id', 'student_id', name='unique_parent_student'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'student_email': self.student.user.email if self.student and self.student.user else None,
            'relationship': self.relationship,
            'is_primary_contact': self.is_primary_contact,
            'status': self.status,
            'linked_at': self.linked_at.isoformat() if self.linked_at else None
        }


class LinkRequest(db.Model):
    """Parent-child link request model"""
    __tablename__ = 'link_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  # invite_code, email_request
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, expired
    invite_code = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    
    # Relationships
    parent = db.relationship('Parent', backref='link_requests')
    student = db.relationship('Student', backref='link_requests')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'parent_email': self.parent.email if self.parent else None,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'request_type': self.request_type,
            'status': self.status,
            'invite_code': self.invite_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None
        }

