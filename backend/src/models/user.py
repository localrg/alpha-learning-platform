"""
User model for authentication and account management.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import db


class User(db.Model):
    """
    User model for storing user account information.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        password_hash: Hashed password (never store plain text)
        email: User email address
        created_at: Timestamp of account creation
        last_login: Timestamp of last successful login
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'teacher', 'admin'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship to student profile (one-to-one) - will be created in Step 2.1
    # student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last_login timestamp to current time."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """
        Convert user object to dictionary (for JSON responses).
        
        Returns:
            dict: User data (excluding password_hash)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

