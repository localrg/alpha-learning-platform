"""
Shared Challenge Models
Handles challenges between friends and class members
"""

from datetime import datetime
from src.database import db


class SharedChallenge(db.Model):
    """Model for shared challenges between students"""
    __tablename__ = 'shared_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Challenge creator
    creator_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Challenge scope
    challenge_type = db.Column(db.String(20), nullable=False)  # 'friend', 'class'
    class_id = db.Column(db.Integer, db.ForeignKey('class_groups.id'))  # For class challenges
    
    # Challenge mode
    mode = db.Column(db.String(20), nullable=False)  # 'competitive', 'collaborative'
    
    # Challenge content
    skill_id = db.Column(db.Integer, nullable=False)
    target_questions = db.Column(db.Integer, nullable=False)  # Number of questions to answer
    target_accuracy = db.Column(db.Float, nullable=False)  # Required accuracy (e.g., 0.9 for 90%)
    
    # Timing
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'expired'
    
    # Rewards
    xp_reward = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('Student', foreign_keys=[creator_id], backref='created_challenges')
    class_group = db.relationship('ClassGroup', backref='challenges')
    participants = db.relationship('ChallengeParticipant', back_populates='challenge', cascade='all, delete-orphan')
    
    def to_dict(self, include_participants=False):
        """Convert challenge to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creator': {
                'id': self.creator.id,
                'user_id': self.creator.user_id,
                'username': self.creator.user.username if self.creator.user else None,
                'display_name': self.creator.name
            },
            'challenge_type': self.challenge_type,
            'class_id': self.class_id,
            'mode': self.mode,
            'skill_id': self.skill_id,
            'target_questions': self.target_questions,
            'target_accuracy': self.target_accuracy,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'xp_reward': self.xp_reward,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_participants:
            data['participants'] = [p.to_dict() for p in self.participants]
            data['participant_count'] = len(self.participants)
        
        return data


class ChallengeParticipant(db.Model):
    """Model for challenge participants"""
    __tablename__ = 'challenge_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('shared_challenges.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Invitation status
    status = db.Column(db.String(20), default='invited')  # 'invited', 'accepted', 'declined'
    
    # Progress tracking
    questions_answered = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    
    # Completion
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # Ranking (for competitive mode)
    rank = db.Column(db.Integer)
    
    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    challenge = db.relationship('SharedChallenge', back_populates='participants')
    student = db.relationship('Student', backref='challenge_participations')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('challenge_id', 'student_id', name='unique_challenge_participant'),)
    
    def to_dict(self, include_student=True):
        """Convert participant to dictionary"""
        data = {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'student_id': self.student_id,
            'status': self.status,
            'questions_answered': self.questions_answered,
            'questions_correct': self.questions_correct,
            'accuracy': self.accuracy,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'rank': self.rank,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
        
        if include_student and self.student:
            # Get progress data if available
            progress = self.student.progress if hasattr(self.student, 'progress') else None
            data['student'] = {
                'id': self.student.id,
                'user_id': self.student.user_id,
                'username': self.student.user.username if self.student.user else None,
                'display_name': self.student.name,
                'avatar_url': self.student.avatar,
                'current_level': progress.current_level if progress else 1,
                'total_xp': progress.total_xp if progress else 0
            }
        
        return data

