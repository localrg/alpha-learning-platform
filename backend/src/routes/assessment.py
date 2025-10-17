"""
Assessment API routes for creating and managing assessments.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.student import Student
from src.models.assessment import Assessment, AssessmentResponse, Question, Skill
import random

assessment_bp = Blueprint('assessment', __name__, url_prefix='/api/assessment')


@assessment_bp.route('/start', methods=['POST'])
@jwt_required()
def start_assessment():
    """
    Start a new assessment for the current student.
    
    Request body:
    {
        "assessment_type": "diagnostic",  // or "unit_test", "skill_check"
        "grade_level": 5,                 // optional, defaults to student's grade
        "skill_id": 1                     // optional, for skill-specific assessments
    }
    
    Response:
    {
        "assessment": {...},
        "questions": [...]  // Questions without answers
    }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        data = request.get_json()
        assessment_type = data.get('assessment_type', 'diagnostic')
        grade_level = data.get('grade_level', student.grade)
        skill_id = data.get('skill_id')
        
        # Validate assessment type
        valid_types = ['diagnostic', 'unit_test', 'skill_check']
        if assessment_type not in valid_types:
            return jsonify({'error': f'Invalid assessment type. Must be one of: {valid_types}'}), 400
        
        # Select questions based on assessment type
        if assessment_type == 'diagnostic':
            # Diagnostic: Sample questions from current grade and 2 grades below
            questions = _select_diagnostic_questions(grade_level)
        elif assessment_type == 'skill_check' and skill_id:
            # Skill check: All questions from specific skill
            questions = Question.query.filter_by(skill_id=skill_id).all()
        else:
            # Unit test: Questions from specific grade level
            questions = Question.query.filter_by(grade_level=grade_level).all()
            questions = random.sample(questions, min(10, len(questions)))
        
        if not questions:
            return jsonify({'error': 'No questions available for this assessment'}), 404
        
        # Create assessment
        assessment = Assessment(
            student_id=student.id,
            assessment_type=assessment_type,
            grade_level=grade_level,
            total_questions=len(questions)
        )
        db.session.add(assessment)
        db.session.commit()
        
        # Return assessment and questions (without answers)
        return jsonify({
            'assessment': assessment.to_dict(),
            'questions': [q.to_dict(include_answer=False) for q in questions]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/<int:assessment_id>/submit', methods=['POST'])
@jwt_required()
def submit_response(assessment_id):
    """
    Submit a response to a question in an assessment.
    
    Request body:
    {
        "question_id": 1,
        "student_answer": "56",
        "time_spent_seconds": 15
    }
    
    Response:
    {
        "response": {...},
        "is_correct": true,
        "explanation": "..."
    }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Verify assessment belongs to student
        assessment = Assessment.query.get(assessment_id)
        if not assessment or assessment.student_id != student.id:
            return jsonify({'error': 'Assessment not found'}), 404
        
        if assessment.completed:
            return jsonify({'error': 'Assessment already completed'}), 400
        
        data = request.get_json()
        question_id = data.get('question_id')
        student_answer = data.get('student_answer', '').strip()
        time_spent = data.get('time_spent_seconds', 0)
        
        if not question_id:
            return jsonify({'error': 'question_id is required'}), 400
        
        # Get question
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Check if already answered
        existing_response = AssessmentResponse.query.filter_by(
            assessment_id=assessment_id,
            question_id=question_id
        ).first()
        
        if existing_response:
            return jsonify({'error': 'Question already answered'}), 400
        
        # Check if answer is correct
        is_correct = student_answer.lower() == question.correct_answer.lower()
        
        # Create response
        response = AssessmentResponse(
            assessment_id=assessment_id,
            question_id=question_id,
            student_answer=student_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent
        )
        db.session.add(response)
        
        # Update assessment correct count
        if is_correct:
            assessment.correct_answers += 1
        
        db.session.commit()
        
        return jsonify({
            'response': response.to_dict(),
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/<int:assessment_id>/complete', methods=['POST'])
@jwt_required()
def complete_assessment(assessment_id):
    """
    Mark an assessment as complete and calculate final score.
    
    Response:
    {
        "assessment": {...},
        "score_percentage": 85.0,
        "skills_to_work_on": [...]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Verify assessment belongs to student
        assessment = Assessment.query.get(assessment_id)
        if not assessment or assessment.student_id != student.id:
            return jsonify({'error': 'Assessment not found'}), 404
        
        if assessment.completed:
            return jsonify({'error': 'Assessment already completed'}), 400
        
        # Mark as complete
        assessment.mark_complete()
        
        # Analyze results to identify skills to work on
        skills_to_work_on = _analyze_assessment_results(assessment)
        
        return jsonify({
            'assessment': assessment.to_dict(),
            'score_percentage': assessment.score_percentage,
            'skills_to_work_on': skills_to_work_on
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/history', methods=['GET'])
@jwt_required()
def get_assessment_history():
    """
    Get all assessments for the current student.
    
    Response:
    {
        "assessments": [...]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        assessments = Assessment.query.filter_by(student_id=student.id).order_by(Assessment.started_at.desc()).all()
        
        return jsonify({
            'assessments': [a.to_dict() for a in assessments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/<int:assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment(assessment_id):
    """
    Get a specific assessment with all responses.
    
    Response:
    {
        "assessment": {...},
        "responses": [...]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        assessment = Assessment.query.get(assessment_id)
        if not assessment or assessment.student_id != student.id:
            return jsonify({'error': 'Assessment not found'}), 404
        
        # Get all responses with question details
        responses_with_questions = []
        for response in assessment.responses:
            response_dict = response.to_dict()
            response_dict['question'] = response.question.to_dict(include_answer=True)
            responses_with_questions.append(response_dict)
        
        return jsonify({
            'assessment': assessment.to_dict(),
            'responses': responses_with_questions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/skills', methods=['GET'])
def get_skills():
    """
    Get all available skills, optionally filtered by grade level.
    
    Query params:
    - grade_level: Filter by grade (optional)
    
    Response:
    {
        "skills": [...]
    }
    """
    try:
        grade_level = request.args.get('grade_level', type=int)
        
        if grade_level:
            skills = Skill.query.filter_by(grade_level=grade_level).all()
        else:
            skills = Skill.query.all()
        
        return jsonify({
            'skills': [s.to_dict() for s in skills]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Helper functions

def _select_diagnostic_questions(grade_level):
    """
    Select questions for a diagnostic assessment.
    Samples from current grade and 2 grades below.
    """
    questions = []
    
    # Determine grade range (current grade and 2 below, minimum grade 3)
    min_grade = max(3, grade_level - 2)
    grades_to_test = range(min_grade, grade_level + 1)
    
    # Get questions from each grade
    for grade in grades_to_test:
        grade_questions = Question.query.filter_by(grade_level=grade).all()
        if grade_questions:
            # Sample 3-4 questions per grade
            sample_size = min(4, len(grade_questions))
            questions.extend(random.sample(grade_questions, sample_size))
    
    # Limit to 10-12 total questions
    if len(questions) > 12:
        questions = random.sample(questions, 12)
    elif len(questions) > 10:
        questions = random.sample(questions, 10)
    
    return questions


def _analyze_assessment_results(assessment):
    """
    Analyze assessment results to identify skills the student needs to work on.
    Returns a list of skills where the student struggled.
    """
    # Get all responses
    responses = assessment.responses
    
    # Group responses by skill
    skill_performance = {}
    for response in responses:
        skill_id = response.question.skill_id
        if skill_id not in skill_performance:
            skill_performance[skill_id] = {'correct': 0, 'total': 0}
        
        skill_performance[skill_id]['total'] += 1
        if response.is_correct:
            skill_performance[skill_id]['correct'] += 1
    
    # Identify skills where performance is below 70%
    skills_to_work_on = []
    for skill_id, performance in skill_performance.items():
        accuracy = performance['correct'] / performance['total']
        if accuracy < 0.7:
            skill = Skill.query.get(skill_id)
            if skill:
                skill_dict = skill.to_dict()
                skill_dict['accuracy'] = accuracy
                skill_dict['questions_attempted'] = performance['total']
                skills_to_work_on.append(skill_dict)
    
    # Sort by accuracy (lowest first)
    skills_to_work_on.sort(key=lambda x: x['accuracy'])
    
    return skills_to_work_on

