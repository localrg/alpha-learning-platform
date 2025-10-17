"""
Hint Service for generating and managing progressive hints.
"""
from src.database import db
from src.models.hint import Hint, HintUsage
from src.models.assessment import Question
from datetime import datetime
import re


class HintService:
    """Service for managing hints and hint generation."""
    
    # Hint templates by question type and operation
    HINT_TEMPLATES = {
        'multiplication': {
            1: "Think about what multiplication means. How can you use addition to solve this?",
            2: "Multiplication is repeated addition. {factor1} × {factor2} means adding {factor1} a total of {factor2} times.",
            3: "Start with 0, then add {factor1} a total of {factor2} times: 0 + {additions}",
            4: "Example: 2 × 3 means 2 + 2 + 2 = 6. Try the same approach with your problem."
        },
        'addition': {
            1: "Think about combining the numbers together. What's a good strategy?",
            2: "Addition means putting groups together. Start with the ones place, then move to the tens.",
            3: "Add the ones place first: {ones1} + {ones2} = {ones_sum}. Then add the tens place: {tens1} + {tens2} = {tens_sum}.",
            4: "Example: 23 + 14 = (20 + 10) + (3 + 4) = 30 + 7 = 37"
        },
        'subtraction': {
            1: "Think about taking away or finding the difference between the numbers.",
            2: "Subtraction means removing from a group. Start with the ones place, then move to the tens.",
            3: "Subtract the ones place first: {ones1} - {ones2} = {ones_diff}. Then subtract the tens place: {tens1} - {tens2} = {tens_diff}.",
            4: "Example: 45 - 12 = (40 - 10) + (5 - 2) = 30 + 3 = 33"
        },
        'division': {
            1: "Think about splitting into equal groups or sharing equally.",
            2: "Division means finding how many groups of one number fit into another.",
            3: "How many groups of {divisor} can you make from {dividend}? Try counting by {divisor}s.",
            4: "Example: 12 ÷ 3 = 4 because 3 + 3 + 3 + 3 = 12"
        },
        'fraction_addition': {
            1: "Think about whether the denominators (bottom numbers) are the same.",
            2: "To add fractions, you need a common denominator. Can you find one?",
            3: "Convert the fractions to have the same denominator, then add the numerators (top numbers).",
            4: "Example: 1/2 + 1/4 = 2/4 + 1/4 = 3/4"
        },
        'fraction_comparison': {
            1: "Think about which piece is larger. Can you visualize the fractions?",
            2: "Compare fractions by finding a common denominator or thinking about their size.",
            3: "Convert both fractions to the same denominator to compare them easily.",
            4: "Example: 1/2 vs 1/3 → 3/6 vs 2/6, so 1/2 is larger"
        }
    }
    
    @staticmethod
    def identify_question_type(question):
        """
        Identify the type of question based on text and options.
        
        Args:
            question: Question object
            
        Returns:
            str: Question type (e.g., 'multiplication', 'addition')
        """
        text = question.question_text.lower()
        
        # Check for operations
        if '×' in text or '*' in text or 'multiply' in text or 'times' in text:
            return 'multiplication'
        elif '+' in text or 'add' in text or 'sum' in text:
            return 'addition'
        elif '−' in text or '-' in text or 'subtract' in text or 'difference' in text:
            return 'subtraction'
        elif '÷' in text or '/' in text or 'divide' in text:
            return 'division'
        elif 'fraction' in text:
            if '+' in text or 'add' in text:
                return 'fraction_addition'
            elif '>' in text or '<' in text or 'compare' in text or 'greater' in text or 'less' in text:
                return 'fraction_comparison'
        
        return 'general'
    
    @staticmethod
    def extract_numbers(text):
        """Extract numbers from question text."""
        # Find all numbers (including decimals and fractions)
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(n) if '.' in n else int(n) for n in numbers]
    
    @staticmethod
    def generate_hints_for_question(question):
        """
        Generate hints for a question automatically.
        
        Args:
            question: Question object
            
        Returns:
            list: List of hint dictionaries
        """
        question_type = HintService.identify_question_type(question)
        
        # Get template for this question type
        template = HintService.HINT_TEMPLATES.get(question_type)
        
        if not template:
            # Generate generic hints
            return HintService.generate_generic_hints(question)
        
        # Extract parameters from question
        numbers = HintService.extract_numbers(question.question_text)
        params = {}
        
        if question_type == 'multiplication' and len(numbers) >= 2:
            params['factor1'] = int(numbers[0])
            params['factor2'] = int(numbers[1])
            params['additions'] = ' + '.join([str(params['factor1'])] * params['factor2'])
        elif question_type in ['addition', 'subtraction'] and len(numbers) >= 2:
            num1, num2 = int(numbers[0]), int(numbers[1])
            params['ones1'] = num1 % 10
            params['ones2'] = num2 % 10
            params['tens1'] = (num1 // 10) * 10
            params['tens2'] = (num2 // 10) * 10
            if question_type == 'addition':
                params['ones_sum'] = params['ones1'] + params['ones2']
                params['tens_sum'] = params['tens1'] + params['tens2']
            else:
                params['ones_diff'] = params['ones1'] - params['ones2']
                params['tens_diff'] = params['tens1'] - params['tens2']
        elif question_type == 'division' and len(numbers) >= 2:
            params['dividend'] = int(numbers[0])
            params['divisor'] = int(numbers[1])
        
        # Generate hints for each level
        hints = []
        for level in [1, 2, 3, 4]:
            try:
                hint_text = template[level].format(**params) if params else template[level]
            except (KeyError, IndexError):
                hint_text = template[level]
            
            hints.append({
                'level': level,
                'text': hint_text,
                'type': 'example' if level == 4 else 'text'
            })
        
        return hints
    
    @staticmethod
    def generate_generic_hints(question):
        """Generate generic hints for questions without specific templates."""
        return [
            {
                'level': 1,
                'text': "Read the question carefully. What is it asking you to find?",
                'type': 'text'
            },
            {
                'level': 2,
                'text': "Think about what operation or strategy you need to use.",
                'type': 'text'
            },
            {
                'level': 3,
                'text': "Break the problem into smaller steps. What should you do first?",
                'type': 'text'
            },
            {
                'level': 4,
                'text': "Try working backwards from the answer choices, or draw a picture to help visualize the problem.",
                'type': 'text'
            }
        ]
    
    @staticmethod
    def create_hints_for_question(question_id, hints_data):
        """
        Create hints for a question.
        
        Args:
            question_id: ID of the question
            hints_data: List of hint dictionaries
            
        Returns:
            list: Created Hint objects
        """
        created_hints = []
        
        for hint_data in hints_data:
            hint = Hint(
                question_id=question_id,
                hint_level=hint_data['level'],
                hint_text=hint_data['text'],
                hint_type=hint_data.get('type', 'text'),
                image_url=hint_data.get('image_url'),
                sequence_order=hint_data['level']
            )
            db.session.add(hint)
            created_hints.append(hint)
        
        db.session.commit()
        return created_hints
    
    @staticmethod
    def get_hints_for_question(question_id):
        """
        Get all active hints for a question, ordered by level.
        
        Args:
            question_id: ID of the question
            
        Returns:
            list: List of hint dictionaries
        """
        hints = Hint.query.filter_by(
            question_id=question_id,
            is_active=True
        ).order_by(Hint.hint_level).all()
        
        return [hint.to_dict() for hint in hints]
    
    @staticmethod
    def get_next_hint(question_id, current_level=0):
        """
        Get the next hint for a question.
        
        Args:
            question_id: ID of the question
            current_level: Current hint level (0 if no hints shown yet)
            
        Returns:
            dict: Next hint data or None
        """
        next_level = current_level + 1
        
        hint = Hint.query.filter_by(
            question_id=question_id,
            hint_level=next_level,
            is_active=True
        ).first()
        
        if not hint:
            return None
        
        # Check if more hints available
        max_hint = Hint.query.filter_by(
            question_id=question_id,
            is_active=True
        ).order_by(Hint.hint_level.desc()).first()
        
        total_levels = max_hint.hint_level if max_hint else 0
        
        return {
            'hint': hint.to_dict(),
            'next_level_available': next_level < total_levels,
            'total_levels': total_levels
        }
    
    @staticmethod
    def record_hint_usage(student_id, question_id, hint_id, hint_level, 
                         attempt_number=1, time_before_hint=None):
        """
        Record that a student used a hint.
        
        Args:
            student_id: ID of the student
            question_id: ID of the question
            hint_id: ID of the hint
            hint_level: Level of the hint
            attempt_number: Which attempt when hint was used
            time_before_hint: Seconds before requesting hint
            
        Returns:
            HintUsage: Created usage record
        """
        usage = HintUsage(
            student_id=student_id,
            question_id=question_id,
            hint_id=hint_id,
            hint_level=hint_level,
            attempt_number=attempt_number,
            time_before_hint=time_before_hint
        )
        
        db.session.add(usage)
        db.session.commit()
        
        return usage
    
    @staticmethod
    def update_hint_feedback(usage_id, helpful=None, answered_correctly=None, 
                            attempts_after_hint=None):
        """
        Update hint usage with feedback and outcome.
        
        Args:
            usage_id: ID of the hint usage
            helpful: Whether hint was helpful (True/False)
            answered_correctly: Whether answered correctly after hint
            attempts_after_hint: Number of attempts after using hint
            
        Returns:
            HintUsage: Updated usage record
        """
        usage = HintUsage.query.get(usage_id)
        if not usage:
            return None
        
        if helpful is not None:
            usage.helpful = helpful
        if answered_correctly is not None:
            usage.answered_correctly = answered_correctly
        if attempts_after_hint is not None:
            usage.attempts_after_hint = attempts_after_hint
        
        db.session.commit()
        return usage
    
    @staticmethod
    def get_student_hint_stats(student_id):
        """
        Get hint usage statistics for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            dict: Statistics
        """
        usages = HintUsage.query.filter_by(student_id=student_id).all()
        
        if not usages:
            return {
                'total_hints_used': 0,
                'hints_by_level': {},
                'average_level': 0,
                'helpful_rate': 0,
                'success_rate_after_hint': 0
            }
        
        # Count by level
        hints_by_level = {}
        for usage in usages:
            level = usage.hint_level
            hints_by_level[level] = hints_by_level.get(level, 0) + 1
        
        # Calculate average level
        total_level = sum(u.hint_level for u in usages)
        average_level = total_level / len(usages)
        
        # Calculate helpful rate
        helpful_usages = [u for u in usages if u.helpful is not None]
        helpful_rate = (
            sum(1 for u in helpful_usages if u.helpful) / len(helpful_usages)
            if helpful_usages else 0
        )
        
        # Calculate success rate after hint
        answered_usages = [u for u in usages if u.answered_correctly is not None]
        success_rate = (
            sum(1 for u in answered_usages if u.answered_correctly) / len(answered_usages)
            if answered_usages else 0
        )
        
        return {
            'total_hints_used': len(usages),
            'hints_by_level': hints_by_level,
            'average_level': round(average_level, 2),
            'helpful_rate': round(helpful_rate, 2),
            'success_rate_after_hint': round(success_rate, 2)
        }
    
    @staticmethod
    def get_question_hint_stats(question_id):
        """
        Get hint usage statistics for a question.
        
        Args:
            question_id: ID of the question
            
        Returns:
            dict: Statistics
        """
        usages = HintUsage.query.filter_by(question_id=question_id).all()
        
        if not usages:
            return {
                'total_students_used_hints': 0,
                'average_hint_level': 0,
                'helpful_rate': 0,
                'success_rate_after_hint': 0
            }
        
        # Count unique students
        unique_students = len(set(u.student_id for u in usages))
        
        # Calculate average level
        average_level = sum(u.hint_level for u in usages) / len(usages)
        
        # Calculate helpful rate
        helpful_usages = [u for u in usages if u.helpful is not None]
        helpful_rate = (
            sum(1 for u in helpful_usages if u.helpful) / len(helpful_usages)
            if helpful_usages else 0
        )
        
        # Calculate success rate
        answered_usages = [u for u in usages if u.answered_correctly is not None]
        success_rate = (
            sum(1 for u in answered_usages if u.answered_correctly) / len(answered_usages)
            if answered_usages else 0
        )
        
        return {
            'total_students_used_hints': unique_students,
            'total_hint_requests': len(usages),
            'average_hint_level': round(average_level, 2),
            'helpful_rate': round(helpful_rate, 2),
            'success_rate_after_hint': round(success_rate, 2)
        }

