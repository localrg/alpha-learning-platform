"""
Assessment models for storing assessment data and student responses.
"""
from datetime import datetime
from src.database import db


class Assessment(db.Model):
    """
    Represents an assessment taken by a student.
    Each assessment is linked to a student and contains multiple responses.
    """
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # 'diagnostic', 'unit_test', 'skill_check'
    grade_level = db.Column(db.Integer, nullable=False)  # Grade level assessed (3-8)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    score_percentage = db.Column(db.Float, nullable=False, default=0.0)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship to student
    student = db.relationship('Student', backref=db.backref('assessments', lazy=True))
    
    # Relationship to responses
    responses = db.relationship('AssessmentResponse', backref='assessment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Assessment {self.id} - {self.assessment_type} for Student {self.student_id}>'

    def to_dict(self):
        """Convert assessment to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'assessment_type': self.assessment_type,
            'grade_level': self.grade_level,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'score_percentage': self.score_percentage,
            'completed': self.completed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

    def calculate_score(self):
        """Calculate and update the score based on responses."""
        if self.total_questions == 0:
            self.score_percentage = 0.0
        else:
            self.score_percentage = (self.correct_answers / self.total_questions) * 100
        db.session.commit()

    def mark_complete(self):
        """Mark the assessment as completed."""
        self.completed = True
        self.completed_at = datetime.utcnow()
        self.calculate_score()
        db.session.commit()


class AssessmentResponse(db.Model):
    """
    Represents a student's response to a single question in an assessment.
    """
    __tablename__ = 'assessment_responses'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    student_answer = db.Column(db.String(500), nullable=True)  # Student's answer
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    time_spent_seconds = db.Column(db.Integer, nullable=True)  # Time spent on this question
    answered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to question
    question = db.relationship('Question', backref=db.backref('responses', lazy=True))

    def __repr__(self):
        return f'<AssessmentResponse {self.id} - Q{self.question_id} {"✓" if self.is_correct else "✗"}>'

    def to_dict(self):
        """Convert response to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'question_id': self.question_id,
            'student_answer': self.student_answer,
            'is_correct': self.is_correct,
            'time_spent_seconds': self.time_spent_seconds,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None,
        }


class Question(db.Model):
    """
    Represents a question in the question bank.
    Questions are used in assessments and learning sessions.
    """
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # 'multiple_choice', 'numeric', 'text'
    correct_answer = db.Column(db.String(500), nullable=False)
    options = db.Column(db.JSON, nullable=True)  # For multiple choice: ["option1", "option2", ...]
    explanation = db.Column(db.Text, nullable=True)  # Explanation of the answer
    difficulty = db.Column(db.String(20), nullable=False)  # 'easy', 'medium', 'hard'
    grade_level = db.Column(db.Integer, nullable=False)  # 3-8
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to skill
    skill = db.relationship('Skill', backref=db.backref('questions', lazy=True))

    def __repr__(self):
        return f'<Question {self.id} - {self.skill_id} ({self.difficulty})>'

    def to_dict(self, include_answer=False):
        """
        Convert question to dictionary for JSON serialization.
        
        Args:
            include_answer: If True, include correct_answer and explanation
        """
        data = {
            'id': self.id,
            'skill_id': self.skill_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.options,
            'difficulty': self.difficulty,
            'grade_level': self.grade_level,
        }
        
        if include_answer:
            data['correct_answer'] = self.correct_answer
            data['explanation'] = self.explanation
        
        return data


class Skill(db.Model):
    """
    Represents a math skill that students need to master.
    Skills are organized by grade level and subject area.
    """
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    grade_level = db.Column(db.Integer, nullable=False)  # 3-8
    subject_area = db.Column(db.String(100), nullable=False)  # 'arithmetic', 'fractions', 'geometry', etc.
    prerequisite_skill_ids = db.Column(db.JSON, nullable=True)  # List of skill IDs that are prerequisites
    mastery_threshold = db.Column(db.Float, nullable=False, default=0.9)  # 90% by default
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Skill {self.id} - {self.name} (Grade {self.grade_level})>'

    def to_dict(self):
        """Convert skill to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'grade_level': self.grade_level,
            'subject_area': self.subject_area,
            'prerequisite_skill_ids': self.prerequisite_skill_ids or [],
            'mastery_threshold': self.mastery_threshold,
        }

