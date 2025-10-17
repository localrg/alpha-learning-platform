"""
Learning Path Generation Service

Analyzes assessment results and generates personalized learning paths.
"""
from src.database import db
from src.models.student import Student
from src.models.assessment import Assessment, AssessmentResponse
from src.models.learning_path import LearningPath
from src.models.assessment import Skill
from datetime import datetime


class LearningPathService:
    """Service for generating and managing learning paths."""
    
    @staticmethod
    def generate_from_assessment(assessment_id):
        """
        Generate a learning path based on assessment results.
        
        Args:
            assessment_id: ID of the completed assessment
            
        Returns:
            dict: Learning path with skills and recommendations
        """
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")
        
        if not assessment.completed:
            raise ValueError("Assessment not completed yet")
        
        student = assessment.student
        
        # Analyze assessment responses
        responses = AssessmentResponse.query.filter_by(assessment_id=assessment_id).all()
        
        # Group responses by skill
        skill_performance = {}
        for response in responses:
            skill_id = response.question.skill_id
            if skill_id not in skill_performance:
                skill_performance[skill_id] = {
                    'correct': 0,
                    'total': 0,
                    'skill': response.question.skill
                }
            
            skill_performance[skill_id]['total'] += 1
            if response.is_correct:
                skill_performance[skill_id]['correct'] += 1
        
        # Calculate accuracy for each skill
        skills_to_work_on = []
        for skill_id, perf in skill_performance.items():
            accuracy = (perf['correct'] / perf['total']) * 100 if perf['total'] > 0 else 0
            
            # Skills below 70% need work
            if accuracy < 70:
                skills_to_work_on.append({
                    'skill_id': skill_id,
                    'skill_name': perf['skill'].name,
                    'skill_grade': perf['skill'].grade_level,
                    'accuracy': accuracy,
                    'questions_attempted': perf['total'],
                    'correct': perf['correct']
                })
        
        # Sort by accuracy (lowest first) and grade level
        skills_to_work_on.sort(key=lambda x: (x['skill_grade'], x['accuracy']))
        
        # Create or update learning path entries
        learning_path_items = []
        for index, skill_data in enumerate(skills_to_work_on):
            # Check if already exists
            existing = LearningPath.query.filter_by(
                student_id=student.id,
                skill_id=skill_data['skill_id']
            ).first()
            
            if existing:
                # Update existing entry
                existing.priority = index
                existing.sequence_order = index
                existing.updated_at = datetime.utcnow()
                learning_path_items.append(existing)
            else:
                # Create new entry
                new_item = LearningPath(
                    student_id=student.id,
                    skill_id=skill_data['skill_id'],
                    status='not_started',
                    priority=index,
                    sequence_order=index,
                    current_accuracy=skill_data['accuracy']
                )
                db.session.add(new_item)
                learning_path_items.append(new_item)
        
        db.session.commit()
        
        # Generate recommendations
        recommendations = LearningPathService._generate_recommendations(
            student, skills_to_work_on, assessment
        )
        
        return {
            'student_id': student.id,
            'student_name': student.name,
            'assessment_score': assessment.score_percentage,
            'total_skills_to_master': len(skills_to_work_on),
            'learning_path': [item.to_dict() for item in learning_path_items],
            'skills_analysis': skills_to_work_on,
            'recommendations': recommendations
        }
    
    @staticmethod
    def _generate_recommendations(student, skills_to_work_on, assessment):
        """Generate personalized recommendations."""
        recommendations = []
        
        # Overall performance recommendation
        if assessment.score_percentage >= 80:
            recommendations.append({
                'type': 'encouragement',
                'message': f"Great job, {student.name}! You're performing well overall."
            })
        elif assessment.score_percentage >= 60:
            recommendations.append({
                'type': 'improvement',
                'message': f"Good effort, {student.name}! Let's strengthen a few areas."
            })
        else:
            recommendations.append({
                'type': 'support',
                'message': f"Don't worry, {student.name}! We'll build a strong foundation together."
            })
        
        # Specific skill recommendations
        if len(skills_to_work_on) > 0:
            first_skill = skills_to_work_on[0]
            recommendations.append({
                'type': 'next_step',
                'message': f"Start with '{first_skill['skill_name']}' - it's a foundational skill for your grade level.",
                'skill_id': first_skill['skill_id']
            })
        
        # Time estimate
        estimated_hours = len(skills_to_work_on) * 2  # 2 hours per skill average
        recommendations.append({
            'type': 'timeline',
            'message': f"With 1 hour of daily practice, you can master these skills in about {estimated_hours} days."
        })
        
        # Study strategy
        recommendations.append({
            'type': 'strategy',
            'message': "Remember: It's better to master one skill at a time than to rush through many."
        })
        
        return recommendations
    
    @staticmethod
    def get_student_learning_path(student_id):
        """Get the current learning path for a student."""
        items = LearningPath.query.filter_by(student_id=student_id)\
            .order_by(LearningPath.sequence_order)\
            .all()
        
        return {
            'total_skills': len(items),
            'mastered': len([i for i in items if i.mastery_achieved]),
            'in_progress': len([i for i in items if i.status == 'in_progress']),
            'not_started': len([i for i in items if i.status == 'not_started']),
            'skills': [item.to_dict() for item in items]
        }
    
    @staticmethod
    def get_next_skill(student_id):
        """Get the next skill the student should work on."""
        # Find the first non-mastered skill in sequence
        next_skill = LearningPath.query.filter_by(
            student_id=student_id,
            mastery_achieved=False
        ).order_by(LearningPath.sequence_order).first()
        
        if next_skill:
            return next_skill.to_dict()
        
        return None
    
    @staticmethod
    def check_and_update_mastery(learning_path_id):
        """
        Check if a skill has been mastered and update status.
        
        Mastery criteria:
        - 90%+ accuracy
        - At least 5 questions answered
        
        Args:
            learning_path_id: ID of the learning path item
            
        Returns:
            dict: Mastery status and achievement details
        """
        item = LearningPath.query.get(learning_path_id)
        if not item:
            raise ValueError("Learning path item not found")
        
        # Check mastery criteria
        mastery_threshold = 90.0
        minimum_questions = 5
        
        is_mastered = (
            item.current_accuracy >= mastery_threshold and
            item.questions_answered >= minimum_questions
        )
        
        # If newly mastered, update status
        if is_mastered and not item.mastery_achieved:
            item.mastery_achieved = True
            item.mastery_date = datetime.utcnow()
            item.status = 'mastered'
            db.session.commit()
            
            return {
                'newly_mastered': True,
                'mastery_achieved': True,
                'skill_name': item.skill.name,
                'final_accuracy': item.current_accuracy,
                'total_attempts': item.attempts,
                'mastery_date': item.mastery_date.isoformat()
            }
        
        return {
            'newly_mastered': False,
            'mastery_achieved': item.mastery_achieved,
            'current_accuracy': item.current_accuracy,
            'questions_answered': item.questions_answered,
            'progress_to_mastery': min(100, (item.current_accuracy / mastery_threshold) * 100)
        }

