"""
Friendship model for social connections between students.
"""
from datetime import datetime
from src.database import db


class Friendship(db.Model):
    """Represents a friendship or friend request between two students."""
    __tablename__ = 'friendships'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    addressee_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = db.relationship('Student', foreign_keys=[requester_id], backref='sent_requests')
    addressee = db.relationship('Student', foreign_keys=[addressee_id], backref='received_requests')
    
    # Unique constraint to prevent duplicate requests
    __table_args__ = (
        db.UniqueConstraint('requester_id', 'addressee_id', name='unique_friendship'),
    )
    
    def to_dict(self):
        """Convert friendship to dictionary."""
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'addressee_id': self.addressee_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

