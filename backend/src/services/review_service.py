"""
Review Service for managing spaced repetition review scheduling.
"""
from src.database import db
from src.models.learning_path import LearningPath
from src.models.review import ReviewSession
from datetime import datetime, timedelta


class ReviewService:
    """Service for managing skill reviews and spaced repetition."""
    
    # Spaced repetition intervals (in days)
    REVIEW_INTERVALS = {
        0: 1,    # First review: 1 day after mastery
        1: 3,    # Second review: 3 days after first
        2: 7,    # Third review: 7 days after second
        3: 14,   # Fourth review: 14 days after third
        4: 30,   # Fifth+ review: 30 days
    }
    
    @staticmethod
    def calculate_next_review_date(review_count):
        """
        Calculate next review date based on spaced repetition algorithm.
        
        Args:
            review_count: Number of reviews completed (0 for first review)
            
        Returns:
            datetime: Next review date
        """
        days = ReviewService.REVIEW_INTERVALS.get(review_count, 30)
        return datetime.utcnow() + timedelta(days=days)
    
    @staticmethod
    def schedule_first_review(learning_path_item):
        """
        Schedule the first review for a newly mastered skill.
        
        Args:
            learning_path_item: LearningPath object that was just mastered
        """
        if not learning_path_item.mastery_achieved:
            return
        
        # Schedule first review for 1 day from now
        learning_path_item.review_count = 0
        learning_path_item.next_review_date = ReviewService.calculate_next_review_date(0)
        learning_path_item.review_interval_days = 1
        
        db.session.commit()
    
    @staticmethod
    def get_reviews_due(student_id):
        """
        Get all skills due for review for a student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            list: List of LearningPath items due for review
        """
        now = datetime.utcnow()
        
        reviews_due = LearningPath.query.filter(
            LearningPath.student_id == student_id,
            LearningPath.mastery_achieved == True,
            LearningPath.next_review_date != None,
            LearningPath.next_review_date <= now
        ).all()
        
        return reviews_due
    
    @staticmethod
    def start_review_session(learning_path_id, student_id):
        """
        Start a new review session.
        
        Args:
            learning_path_id: ID of the learning path item
            student_id: ID of the student
            
        Returns:
            ReviewSession: New review session object
        """
        learning_path_item = LearningPath.query.get(learning_path_id)
        
        if not learning_path_item or learning_path_item.student_id != student_id:
            return None
        
        # Create new review session
        review_session = ReviewSession(
            student_id=student_id,
            learning_path_id=learning_path_id,
            skill_id=learning_path_item.skill_id,
            review_number=learning_path_item.review_count + 1
        )
        
        db.session.add(review_session)
        db.session.commit()
        
        return review_session
    
    @staticmethod
    def complete_review_session(review_session_id, correct, total):
        """
        Complete a review session and update scheduling.
        
        Args:
            review_session_id: ID of the review session
            correct: Number of correct answers
            total: Total number of questions
            
        Returns:
            dict: Review results and next review information
        """
        review_session = ReviewSession.query.get(review_session_id)
        
        if not review_session:
            return None
        
        # Complete the review
        review_session.complete_review(correct, total)
        
        # Get the learning path item
        learning_path_item = review_session.learning_path
        
        # Update review tracking
        learning_path_item.last_reviewed_at = datetime.utcnow()
        learning_path_item.review_count += 1
        
        # Determine next steps based on performance
        if review_session.passed:
            # Passed: Schedule next review with increased interval
            learning_path_item.next_review_date = ReviewService.calculate_next_review_date(
                learning_path_item.review_count
            )
            learning_path_item.review_interval_days = (
                learning_path_item.next_review_date - datetime.utcnow()
            ).days
            
            # Keep mastered status
            learning_path_item.status = 'mastered'
            
            result_message = "Great job! You've maintained mastery of this skill."
        else:
            # Failed: Mark as needs review and reset to learning path
            learning_path_item.status = 'needs_review'
            learning_path_item.mastery_achieved = False
            learning_path_item.next_review_date = None
            
            result_message = "This skill needs more practice. It's been added back to your learning path."
        
        db.session.commit()
        
        return {
            'review_session': review_session.to_dict(),
            'passed': review_session.passed,
            'skill_status': learning_path_item.status,
            'next_review_date': learning_path_item.next_review_date.isoformat() if learning_path_item.next_review_date else None,
            'message': result_message
        }
    
    @staticmethod
    def get_upcoming_reviews(student_id, days_ahead=7):
        """
        Get upcoming reviews scheduled in the next N days.
        
        Args:
            student_id: ID of the student
            days_ahead: Number of days to look ahead (default 7)
            
        Returns:
            list: List of LearningPath items with upcoming reviews
        """
        now = datetime.utcnow()
        future_date = now + timedelta(days=days_ahead)
        
        upcoming = LearningPath.query.filter(
            LearningPath.student_id == student_id,
            LearningPath.mastery_achieved == True,
            LearningPath.next_review_date != None,
            LearningPath.next_review_date > now,
            LearningPath.next_review_date <= future_date
        ).order_by(LearningPath.next_review_date).all()
        
        return upcoming
    
    @staticmethod
    def get_review_history(student_id, limit=10):
        """
        Get recent review history for a student.
        
        Args:
            student_id: ID of the student
            limit: Maximum number of reviews to return
            
        Returns:
            list: List of recent ReviewSession objects
        """
        history = ReviewSession.query.filter(
            ReviewSession.student_id == student_id,
            ReviewSession.completed_at != None
        ).order_by(ReviewSession.completed_at.desc()).limit(limit).all()
        
        return history

