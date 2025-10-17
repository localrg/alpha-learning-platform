"""
Service for managing streak tracking and rewards.
"""
from datetime import datetime, date, timedelta
from src.database import db
from src.models.streak import StreakTracking
from src.services.gamification_service import GamificationService


class StreakService:
    """Service for streak tracking operations."""
    
    # Milestone rewards
    LOGIN_MILESTONES = {
        3: 25,
        7: 75,
        14: 150,
        30: 300,
        100: 1000
    }
    
    PRACTICE_MILESTONES = {
        3: 50,
        7: 100,
        14: 200,
        30: 500,
        100: 1500
    }
    
    @staticmethod
    def get_or_create_streak(student_id):
        """Get or create streak tracking for a student."""
        streak = StreakTracking.query.filter_by(student_id=student_id).first()
        if not streak:
            streak = StreakTracking(student_id=student_id)
            db.session.add(streak)
            db.session.commit()
        return streak
    
    @staticmethod
    def update_login_streak(student_id):
        """Update login streak for a student."""
        streak = StreakService.get_or_create_streak(student_id)
        today = date.today()
        
        # If already logged in today, no update needed
        if streak.last_login_date == today:
            return {'streak': streak.login_streak, 'milestone_reached': False}
        
        # Check if streak continues or breaks
        if streak.last_login_date:
            days_diff = (today - streak.last_login_date).days
            
            if days_diff == 1:
                # Streak continues
                old_streak = streak.login_streak
                streak.login_streak += 1
                streak.last_login_date = today
                
                # Update best streak
                if streak.login_streak > streak.login_streak_best:
                    streak.login_streak_best = streak.login_streak
                
                # Check for milestone
                milestone_xp = StreakService._check_milestone(
                    old_streak,
                    streak.login_streak,
                    StreakService.LOGIN_MILESTONES,
                    student_id,
                    'login_streak'
                )
                
                db.session.commit()
                return {
                    'streak': streak.login_streak,
                    'milestone_reached': milestone_xp > 0,
                    'milestone_xp': milestone_xp
                }
            else:
                # Streak breaks
                streak.login_streak = 1
                streak.last_login_date = today
                db.session.commit()
                return {'streak': 1, 'milestone_reached': False, 'streak_broken': True}
        else:
            # First login
            streak.login_streak = 1
            streak.login_streak_best = 1
            streak.last_login_date = today
            db.session.commit()
            return {'streak': 1, 'milestone_reached': False}
    
    @staticmethod
    def update_practice_streak(student_id):
        """Update practice streak for a student."""
        streak = StreakService.get_or_create_streak(student_id)
        today = date.today()
        
        # If already practiced today, no update needed
        if streak.last_practice_date == today:
            return {'streak': streak.practice_streak, 'milestone_reached': False}
        
        # Check if streak continues or breaks
        if streak.last_practice_date:
            days_diff = (today - streak.last_practice_date).days
            
            if days_diff == 1:
                # Streak continues
                old_streak = streak.practice_streak
                streak.practice_streak += 1
                streak.last_practice_date = today
                
                # Update best streak
                if streak.practice_streak > streak.practice_streak_best:
                    streak.practice_streak_best = streak.practice_streak
                
                # Check for milestone
                milestone_xp = StreakService._check_milestone(
                    old_streak,
                    streak.practice_streak,
                    StreakService.PRACTICE_MILESTONES,
                    student_id,
                    'practice_streak'
                )
                
                db.session.commit()
                return {
                    'streak': streak.practice_streak,
                    'milestone_reached': milestone_xp > 0,
                    'milestone_xp': milestone_xp
                }
            else:
                # Streak breaks
                streak.practice_streak = 1
                streak.last_practice_date = today
                db.session.commit()
                return {'streak': 1, 'milestone_reached': False, 'streak_broken': True}
        else:
            # First practice
            streak.practice_streak = 1
            streak.practice_streak_best = 1
            streak.last_practice_date = today
            db.session.commit()
            return {'streak': 1, 'milestone_reached': False}
    
    @staticmethod
    def _check_milestone(old_streak, new_streak, milestones, student_id, streak_type):
        """Check if a milestone was reached and award XP."""
        for milestone, xp in milestones.items():
            if old_streak < milestone <= new_streak:
                # Milestone reached!
                GamificationService.award_xp(
                    student_id,
                    f'{streak_type}_milestone',
                    base_xp=xp
                )
                return xp
        return 0
    
    @staticmethod
    def get_streak_stats(student_id):
        """Get streak statistics for a student."""
        streak = StreakService.get_or_create_streak(student_id)
        
        # Calculate next milestones
        login_next = None
        for milestone in sorted(StreakService.LOGIN_MILESTONES.keys()):
            if streak.login_streak < milestone:
                login_next = {
                    'days': milestone,
                    'xp': StreakService.LOGIN_MILESTONES[milestone],
                    'remaining': milestone - streak.login_streak
                }
                break
        
        practice_next = None
        for milestone in sorted(StreakService.PRACTICE_MILESTONES.keys()):
            if streak.practice_streak < milestone:
                practice_next = {
                    'days': milestone,
                    'xp': StreakService.PRACTICE_MILESTONES[milestone],
                    'remaining': milestone - streak.practice_streak
                }
                break
        
        return {
            'login_streak': streak.login_streak,
            'login_streak_best': streak.login_streak_best,
            'login_next_milestone': login_next,
            'practice_streak': streak.practice_streak,
            'practice_streak_best': streak.practice_streak_best,
            'practice_next_milestone': practice_next
        }

