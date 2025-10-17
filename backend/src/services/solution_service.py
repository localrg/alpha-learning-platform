"""
Solution Service for generating and managing worked solutions.
"""
import re
from src.database import db
from src.models.solution import WorkedSolution, SolutionView
from src.models.assessment import Question, AssessmentResponse


class SolutionService:
    """Service for managing worked solutions."""

    @staticmethod
    def extract_numbers(text):
        """Extract numbers from question text."""
        # Match integers and decimals
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(n) if '.' in n else int(n) for n in numbers]

    @staticmethod
    def identify_operation(question):
        """Identify the mathematical operation in the question."""
        text = question.question_text.lower()
        
        if '×' in text or '*' in text or 'multiply' in text or 'times' in text or 'product' in text:
            return 'multiplication'
        elif '+' in text or 'add' in text or 'sum' in text or 'plus' in text:
            return 'addition'
        elif '−' in text or '-' in text or 'subtract' in text or 'minus' in text or 'difference' in text:
            return 'subtraction'
        elif '÷' in text or '/' in text or 'divide' in text or 'quotient' in text:
            return 'division'
        elif 'fraction' in text or '/' in question.correct_answer:
            return 'fraction'
        else:
            return 'general'

    @staticmethod
    def generate_multiplication_solution(question, numbers):
        """Generate step-by-step solution for multiplication."""
        if len(numbers) < 2:
            return None
        
        factor1, factor2 = numbers[0], numbers[1]
        answer = factor1 * factor2
        
        steps = [
            {
                'step_number': 1,
                'step_type': 'explanation',
                'content': f"Understand what {factor1} × {factor2} means",
                'explanation': f"Multiplication means repeated addition. {factor1} × {factor2} means adding {factor1} a total of {factor2} times.",
                'highlight': False
            },
            {
                'step_number': 2,
                'step_type': 'calculation',
                'content': f"Set up repeated addition: {factor1} + {factor1} + ... ({factor2} times)",
                'explanation': f"We need to add {factor1} to itself {factor2} times.",
                'highlight': False
            },
            {
                'step_number': 3,
                'step_type': 'calculation',
                'content': f"Perform the addition: {' + '.join([str(factor1)] * factor2)}",
                'explanation': "Add all the numbers together.",
                'highlight': True
            },
            {
                'step_number': 4,
                'step_type': 'calculation',
                'content': f"= {answer}",
                'explanation': "This is our final answer.",
                'highlight': True
            },
            {
                'step_number': 5,
                'step_type': 'check',
                'content': f"Check: {factor2} × {factor1} = {answer}",
                'explanation': f"We can verify by switching the order (commutative property). {factor2} groups of {factor1} also equals {answer}.",
                'highlight': False
            }
        ]
        
        return steps

    @staticmethod
    def generate_addition_solution(question, numbers):
        """Generate step-by-step solution for addition."""
        if len(numbers) < 2:
            return None
        
        num1, num2 = numbers[0], numbers[1]
        answer = num1 + num2
        
        # Extract place values
        ones1 = num1 % 10
        tens1 = (num1 // 10) % 10
        ones2 = num2 % 10
        tens2 = (num2 // 10) % 10
        
        ones_sum = ones1 + ones2
        carry = 1 if ones_sum >= 10 else 0
        ones_result = ones_sum % 10
        
        tens_sum = tens1 + tens2 + carry
        
        steps = [
            {
                'step_number': 1,
                'step_type': 'explanation',
                'content': f"Line up the numbers by place value",
                'explanation': f"Write {num1} and {num2} with ones under ones and tens under tens.",
                'highlight': False
            },
            {
                'step_number': 2,
                'step_type': 'calculation',
                'content': f"Add the ones place: {ones1} + {ones2} = {ones_sum}",
                'explanation': "Start with the rightmost column (ones place).",
                'highlight': True
            }
        ]
        
        if carry:
            steps.append({
                'step_number': 3,
                'step_type': 'calculation',
                'content': f"Write {ones_result} in ones place, carry {carry} to tens",
                'explanation': f"Since {ones_sum} ≥ 10, we write {ones_result} and carry {carry} to the tens column.",
                'highlight': True
            })
            steps.append({
                'step_number': 4,
                'step_type': 'calculation',
                'content': f"Add the tens place: {tens1} + {tens2} + {carry} = {tens_sum}",
                'explanation': "Don't forget to add the carried number!",
                'highlight': True
            })
        else:
            steps.append({
                'step_number': 3,
                'step_type': 'calculation',
                'content': f"Add the tens place: {tens1} + {tens2} = {tens_sum}",
                'explanation': "Move to the tens column.",
                'highlight': True
            })
        
        steps.append({
            'step_number': len(steps) + 1,
            'step_type': 'calculation',
            'content': f"Final answer: {answer}",
            'explanation': "Combine the tens and ones to get the complete answer.",
            'highlight': True
        })
        
        steps.append({
            'step_number': len(steps) + 1,
            'step_type': 'check',
            'content': f"Check: {num2} + {num1} = {answer}",
            'explanation': "Addition works in any order (commutative property).",
            'highlight': False
        })
        
        return steps

    @staticmethod
    def generate_subtraction_solution(question, numbers):
        """Generate step-by-step solution for subtraction."""
        if len(numbers) < 2:
            return None
        
        num1, num2 = numbers[0], numbers[1]
        answer = num1 - num2
        
        # Extract place values
        ones1 = num1 % 10
        tens1 = (num1 // 10) % 10
        ones2 = num2 % 10
        tens2 = (num2 // 10) % 10
        
        borrow_needed = ones1 < ones2
        
        if borrow_needed:
            ones_result = (ones1 + 10) - ones2
            tens_result = (tens1 - 1) - tens2
        else:
            ones_result = ones1 - ones2
            tens_result = tens1 - tens2
        
        steps = [
            {
                'step_number': 1,
                'step_type': 'explanation',
                'content': f"Line up the numbers by place value",
                'explanation': f"Write {num1} on top and {num2} below it, aligning place values.",
                'highlight': False
            },
            {
                'step_number': 2,
                'step_type': 'calculation',
                'content': f"Look at the ones place: {ones1} - {ones2}",
                'explanation': "Start with the rightmost column (ones place).",
                'highlight': False
            }
        ]
        
        if borrow_needed:
            steps.append({
                'step_number': 3,
                'step_type': 'calculation',
                'content': f"Borrow from tens: {ones1} becomes {ones1 + 10}",
                'explanation': f"Since {ones1} < {ones2}, we borrow 10 from the tens place.",
                'highlight': True
            })
            steps.append({
                'step_number': 4,
                'step_type': 'calculation',
                'content': f"Subtract ones: {ones1 + 10} - {ones2} = {ones_result}",
                'explanation': "Now we can subtract in the ones place.",
                'highlight': True
            })
            steps.append({
                'step_number': 5,
                'step_type': 'calculation',
                'content': f"Subtract tens: {tens1 - 1} - {tens2} = {tens_result}",
                'explanation': "Remember we borrowed 1 from the tens place.",
                'highlight': True
            })
        else:
            steps.append({
                'step_number': 3,
                'step_type': 'calculation',
                'content': f"Subtract ones: {ones1} - {ones2} = {ones_result}",
                'explanation': "No borrowing needed.",
                'highlight': True
            })
            steps.append({
                'step_number': 4,
                'step_type': 'calculation',
                'content': f"Subtract tens: {tens1} - {tens2} = {tens_result}",
                'explanation': "Move to the tens column.",
                'highlight': True
            })
        
        steps.append({
            'step_number': len(steps) + 1,
            'step_type': 'calculation',
            'content': f"Final answer: {answer}",
            'explanation': "Combine the tens and ones to get the complete answer.",
            'highlight': True
        })
        
        steps.append({
            'step_number': len(steps) + 1,
            'step_type': 'check',
            'content': f"Check: {answer} + {num2} = {num1}",
            'explanation': "We can verify by adding the answer to the number we subtracted.",
            'highlight': False
        })
        
        return steps

    @staticmethod
    def generate_generic_solution(question):
        """Generate a generic solution when specific templates aren't available."""
        answer = question.correct_answer
        explanation = question.explanation or "See the explanation above."
        
        steps = [
            {
                'step_number': 1,
                'step_type': 'explanation',
                'content': "Read the question carefully",
                'explanation': "Make sure you understand what is being asked.",
                'highlight': False
            },
            {
                'step_number': 2,
                'step_type': 'explanation',
                'content': "Identify the key information",
                'explanation': "Look for important numbers, words, or patterns in the question.",
                'highlight': False
            },
            {
                'step_number': 3,
                'step_type': 'calculation',
                'content': explanation,
                'explanation': "This explains how to solve the problem.",
                'highlight': True
            },
            {
                'step_number': 4,
                'step_type': 'calculation',
                'content': f"Answer: {answer}",
                'explanation': "This is the correct answer.",
                'highlight': True
            }
        ]
        
        return steps

    @staticmethod
    def generate_solution_for_question(question):
        """Generate a worked solution for a question."""
        operation = SolutionService.identify_operation(question)
        numbers = SolutionService.extract_numbers(question.question_text)
        
        if operation == 'multiplication':
            steps = SolutionService.generate_multiplication_solution(question, numbers)
        elif operation == 'addition':
            steps = SolutionService.generate_addition_solution(question, numbers)
        elif operation == 'subtraction':
            steps = SolutionService.generate_subtraction_solution(question, numbers)
        else:
            steps = SolutionService.generate_generic_solution(question)
        
        if not steps:
            steps = SolutionService.generate_generic_solution(question)
        
        return {
            'question_id': question.id,
            'solution_type': 'step_by_step',
            'steps': steps,
            'difficulty_level': question.difficulty,
            'show_after_attempts': 1
        }

    @staticmethod
    def create_solution(question_id, solution_data):
        """Create a new worked solution."""
        solution = WorkedSolution(
            question_id=question_id,
            solution_type=solution_data.get('solution_type', 'step_by_step'),
            steps=solution_data.get('steps', []),
            difficulty_level=solution_data.get('difficulty_level', 'beginner'),
            show_after_attempts=solution_data.get('show_after_attempts', 1)
        )
        
        db.session.add(solution)
        db.session.commit()
        
        return solution

    @staticmethod
    def get_solution_for_question(question_id):
        """Get the active solution for a question."""
        solution = WorkedSolution.query.filter_by(
            question_id=question_id,
            is_active=True
        ).first()
        
        return solution.to_dict() if solution else None

    @staticmethod
    def is_eligible_for_solution(student_id, question_id):
        """Check if student is eligible to view solution."""
        # Get solution
        solution = WorkedSolution.query.filter_by(
            question_id=question_id,
            is_active=True
        ).first()
        
        if not solution:
            return False, 0, 0
        
        # Count student's attempts
        attempts = AssessmentResponse.query.filter_by(
            question_id=question_id
        ).join(AssessmentResponse.assessment).filter_by(
            student_id=student_id
        ).count()
        
        eligible = attempts >= solution.show_after_attempts
        
        return eligible, attempts, solution.show_after_attempts

    @staticmethod
    def record_solution_view(student_id, question_id, solution_id, time_spent=None, steps_viewed=None):
        """Record that a student viewed a solution."""
        view = SolutionView(
            student_id=student_id,
            question_id=question_id,
            solution_id=solution_id,
            time_spent_seconds=time_spent,
            steps_viewed=steps_viewed
        )
        
        db.session.add(view)
        db.session.commit()
        
        return view

    @staticmethod
    def update_solution_feedback(view_id, helpful=None, understood=None):
        """Update feedback for a solution view."""
        view = SolutionView.query.get(view_id)
        
        if not view:
            return None
        
        if helpful is not None:
            view.helpful = helpful
        
        if understood is not None:
            view.understood = understood
        
        db.session.commit()
        
        return view

    @staticmethod
    def get_student_solution_stats(student_id):
        """Get solution viewing statistics for a student."""
        views = SolutionView.query.filter_by(student_id=student_id).all()
        
        if not views:
            return {
                'total_solutions_viewed': 0,
                'average_time_per_solution': 0,
                'helpful_rate': 0,
                'understanding_rate': 0
            }
        
        total_views = len(views)
        total_time = sum(v.time_spent_seconds for v in views if v.time_spent_seconds)
        helpful_count = sum(1 for v in views if v.helpful is True)
        understood_count = sum(1 for v in views if v.understood is True)
        feedback_count = sum(1 for v in views if v.helpful is not None)
        assessment_count = sum(1 for v in views if v.understood is not None)
        
        return {
            'total_solutions_viewed': total_views,
            'average_time_per_solution': total_time // total_views if total_views > 0 else 0,
            'helpful_rate': helpful_count / feedback_count if feedback_count > 0 else 0,
            'understanding_rate': understood_count / assessment_count if assessment_count > 0 else 0
        }

    @staticmethod
    def get_question_solution_stats(question_id):
        """Get solution viewing statistics for a question."""
        views = SolutionView.query.filter_by(question_id=question_id).all()
        
        if not views:
            return {
                'total_views': 0,
                'unique_students': 0,
                'average_time': 0,
                'helpful_rate': 0,
                'understanding_rate': 0
            }
        
        total_views = len(views)
        unique_students = len(set(v.student_id for v in views))
        total_time = sum(v.time_spent_seconds for v in views if v.time_spent_seconds)
        helpful_count = sum(1 for v in views if v.helpful is True)
        understood_count = sum(1 for v in views if v.understood is True)
        feedback_count = sum(1 for v in views if v.helpful is not None)
        assessment_count = sum(1 for v in views if v.understood is not None)
        
        return {
            'total_views': total_views,
            'unique_students': unique_students,
            'average_time': total_time // total_views if total_views > 0 else 0,
            'helpful_rate': helpful_count / feedback_count if feedback_count > 0 else 0,
            'understanding_rate': understood_count / assessment_count if assessment_count > 0 else 0
        }

