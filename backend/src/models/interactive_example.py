"""
Interactive Example models for storing and managing interactive learning examples.
"""
from src.database import db
from datetime import datetime
import json


class InteractiveExample(db.Model):
    """
    Represents an interactive example for a skill.
    Examples can be number lines, arrays, fraction visualizers, etc.
    """
    __tablename__ = 'interactive_examples'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    
    # Example information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    example_type = db.Column(db.String(50), nullable=False)  # 'number_line', 'array', 'fraction', etc.
    config_json = db.Column(db.Text, nullable=False)  # JSON configuration
    
    # Metadata
    difficulty_level = db.Column(db.String(20), default='beginner')
    sequence_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skill = db.relationship('Skill', backref='interactive_examples')
    interactions = db.relationship('ExampleInteraction', backref='example', lazy=True, cascade='all, delete-orphan')
    
    @property
    def config(self):
        """Get configuration as dictionary."""
        if self.config_json:
            return json.loads(self.config_json)
        return {}
    
    @config.setter
    def config(self, value):
        """Set configuration from dictionary."""
        self.config_json = json.dumps(value)
    
    def to_dict(self, student_id=None):
        """Convert to dictionary with optional student interaction data."""
        data = {
            'id': self.id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'title': self.title,
            'description': self.description,
            'example_type': self.example_type,
            'config': self.config,
            'difficulty': self.difficulty_level,
            'sequence_order': self.sequence_order,
            'created_at': self.created_at.isoformat()
        }
        
        # Add student interaction data if student_id provided
        if student_id:
            interaction = ExampleInteraction.query.filter_by(
                example_id=self.id,
                student_id=student_id
            ).order_by(ExampleInteraction.started_at.desc()).first()
            
            if interaction:
                data['interacted'] = True
                data['completed'] = interaction.completed
                data['time_spent'] = interaction.time_spent_seconds
                data['last_interaction'] = interaction.started_at.isoformat()
            else:
                data['interacted'] = False
                data['completed'] = False
                data['time_spent'] = 0
                data['last_interaction'] = None
        
        return data


class ExampleInteraction(db.Model):
    """
    Tracks student interactions with interactive examples.
    """
    __tablename__ = 'example_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    example_id = db.Column(db.Integer, db.ForeignKey('interactive_examples.id'), nullable=False)
    
    # Interaction data
    interaction_data_json = db.Column(db.Text, nullable=True)  # JSON log of actions
    time_spent_seconds = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='example_interactions')
    
    @property
    def interaction_data(self):
        """Get interaction data as dictionary."""
        if self.interaction_data_json:
            return json.loads(self.interaction_data_json)
        return []
    
    @interaction_data.setter
    def interaction_data(self, value):
        """Set interaction data from list/dictionary."""
        self.interaction_data_json = json.dumps(value)
    
    def add_interaction(self, action_data):
        """Add a new interaction action to the log."""
        current_data = self.interaction_data
        current_data.append({
            **action_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.interaction_data = current_data
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'example_id': self.example_id,
            'interaction_data': self.interaction_data,
            'time_spent_seconds': self.time_spent_seconds,
            'completed': self.completed,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

