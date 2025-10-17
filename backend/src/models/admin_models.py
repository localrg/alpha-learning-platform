"""
Database models for platform administration and management.
"""
from src.database import db
from datetime import datetime


class AuditLog(db.Model):
    """Audit log for tracking administrative actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # create, update, delete, login, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # user, skill, question, setting, etc.
    entity_id = db.Column(db.Integer)
    before_value = db.Column(db.Text)  # JSON string
    after_value = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    admin = db.relationship('User', backref='audit_logs')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_name': self.admin.username if self.admin else 'Unknown',
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'before_value': self.before_value,
            'after_value': self.after_value,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SystemSetting(db.Model):
    """System-wide settings and configuration"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # general, features, limits, integrations
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)  # JSON string for flexibility
    description = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    updater = db.relationship('User', backref='settings_updated')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'category': self.category,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

