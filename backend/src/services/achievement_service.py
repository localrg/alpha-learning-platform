"""
Achievement service for tracking and unlocking achievements.
"""
from datetime import datetime
from sqlalchemy import and_
from src.database import db
from src.models.achievement import Achievement, StudentAchievement, AchievementProgressLog
from src.services.gamification_service import GamificationService


class AchievementService:
    """Service for managing achievements and badges."""
    
    # Achievement definitions
    ACHIEVEMENTS = [
        # Practice Achievements (Quantity)
        {'name': 'First Steps', 'description': 'Answer 10 questions', 'category': 'practice', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 10, 'icon_emoji': '🏆', 'xp_reward': 50},
        {'name': 'Dedicated Learner', 'description': 'Answer 100 questions', 'category': 'practice', 'tier': 'silver', 'requirement_type': 'count', 'requirement_value': 100, 'icon_emoji': '📚', 'xp_reward': 200},
        {'name': 'Practice Master', 'description': 'Answer 500 questions', 'category': 'practice', 'tier': 'gold', 'requirement_type': 'count', 'requirement_value': 500, 'icon_emoji': '⭐', 'xp_reward': 500},
        {'name': 'Question Champion', 'description': 'Answer 1,000 questions', 'category': 'practice', 'tier': 'platinum', 'requirement_type': 'count', 'requirement_value': 1000, 'icon_emoji': '👑', 'xp_reward': 1000},
        {'name': 'Practice Legend', 'description': 'Answer 5,000 questions', 'category': 'practice', 'tier': 'diamond', 'requirement_type': 'count', 'requirement_value': 5000, 'icon_emoji': '💎', 'xp_reward': 5000},
        
        # Mastery Achievements (Quality)
        {'name': 'First Mastery', 'description': 'Master 1 skill', 'category': 'mastery', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 1, 'icon_emoji': '🎯', 'xp_reward': 100},
        {'name': 'Skill Collector', 'description': 'Master 5 skills', 'category': 'mastery', 'tier': 'silver', 'requirement_type': 'count', 'requirement_value': 5, 'icon_emoji': '🏅', 'xp_reward': 300},
        {'name': 'Mastery Expert', 'description': 'Master 10 skills', 'category': 'mastery', 'tier': 'gold', 'requirement_type': 'count', 'requirement_value': 10, 'icon_emoji': '🌟', 'xp_reward': 750},
        {'name': 'Mastery Champion', 'description': 'Master 25 skills', 'category': 'mastery', 'tier': 'platinum', 'requirement_type': 'count', 'requirement_value': 25, 'icon_emoji': '🔥', 'xp_reward': 2000},
        {'name': 'Complete Mastery', 'description': 'Master 50 skills', 'category': 'mastery', 'tier': 'diamond', 'requirement_type': 'count', 'requirement_value': 50, 'icon_emoji': '💫', 'xp_reward': 5000},
        
        # Accuracy Achievements (Precision)
        {'name': 'Sharp Shooter', 'description': '10 first-try correct answers', 'category': 'accuracy', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 10, 'icon_emoji': '🎯', 'xp_reward': 50},
        {'name': 'Precision Expert', 'description': '50 first-try correct answers', 'category': 'accuracy', 'tier': 'silver', 'requirement_type': 'count', 'requirement_value': 50, 'icon_emoji': '🏹', 'xp_reward': 200},
        {'name': 'Perfect Aim', 'description': '100 first-try correct answers', 'category': 'accuracy', 'tier': 'gold', 'requirement_type': 'count', 'requirement_value': 100, 'icon_emoji': '🎪', 'xp_reward': 500},
        {'name': 'Flawless Performer', 'description': '500 first-try correct answers', 'category': 'accuracy', 'tier': 'platinum', 'requirement_type': 'count', 'requirement_value': 500, 'icon_emoji': '✨', 'xp_reward': 2000},
        
        # Streak Achievements (Consistency)
        {'name': 'Hot Streak', 'description': '5 correct answers in a row', 'category': 'streak', 'tier': 'bronze', 'requirement_type': 'streak', 'requirement_value': 5, 'icon_emoji': '🔥', 'xp_reward': 50},
        {'name': 'On Fire', 'description': '10 correct answers in a row', 'category': 'streak', 'tier': 'silver', 'requirement_type': 'streak', 'requirement_value': 10, 'icon_emoji': '🌶️', 'xp_reward': 150},
        {'name': 'Unstoppable', 'description': '25 correct answers in a row', 'category': 'streak', 'tier': 'gold', 'requirement_type': 'streak', 'requirement_value': 25, 'icon_emoji': '⚡', 'xp_reward': 500},
        {'name': 'Perfect Streak', 'description': '50 correct answers in a row', 'category': 'streak', 'tier': 'platinum', 'requirement_type': 'streak', 'requirement_value': 50, 'icon_emoji': '💥', 'xp_reward': 2000},
        
        # Review Achievements (Retention)
        {'name': 'Reviewer', 'description': 'Complete 5 reviews', 'category': 'review', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 5, 'icon_emoji': '📝', 'xp_reward': 50},
        {'name': 'Review Regular', 'description': 'Complete 25 reviews', 'category': 'review', 'tier': 'silver', 'requirement_type': 'count', 'requirement_value': 25, 'icon_emoji': '📖', 'xp_reward': 200},
        {'name': 'Review Expert', 'description': 'Complete 100 reviews', 'category': 'review', 'tier': 'gold', 'requirement_type': 'count', 'requirement_value': 100, 'icon_emoji': '📚', 'xp_reward': 750},
        {'name': 'Perfect Reviewer', 'description': '10 perfect reviews (100% correct)', 'category': 'review', 'tier': 'platinum', 'requirement_type': 'count', 'requirement_value': 10, 'icon_emoji': '🌟', 'xp_reward': 1000},
        
        # Learning Achievements (Exploration)
        {'name': 'Video Watcher', 'description': 'Watch 5 videos', 'category': 'learning', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 5, 'icon_emoji': '📹', 'xp_reward': 25},
        {'name': 'Resource Explorer', 'description': 'Download 10 resources', 'category': 'learning', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 10, 'icon_emoji': '📦', 'xp_reward': 25},
        {'name': 'Interactive Learner', 'description': 'Try 10 interactive examples', 'category': 'learning', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 10, 'icon_emoji': '🎮', 'xp_reward': 25},
        {'name': 'Hint Seeker', 'description': 'Use hints 25 times', 'category': 'learning', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 25, 'icon_emoji': '💡', 'xp_reward': 50},
        {'name': 'Solution Student', 'description': 'View 50 worked solutions', 'category': 'learning', 'tier': 'silver', 'requirement_type': 'count', 'requirement_value': 50, 'icon_emoji': '📐', 'xp_reward': 100},
        
        # Time Achievements (Dedication)
        {'name': 'Quick Learner', 'description': '1 hour total practice time', 'category': 'time', 'tier': 'bronze', 'requirement_type': 'time', 'requirement_value': 60, 'icon_emoji': '⏰', 'xp_reward': 50},
        {'name': 'Dedicated Student', 'description': '10 hours total practice time', 'category': 'time', 'tier': 'silver', 'requirement_type': 'time', 'requirement_value': 600, 'icon_emoji': '⏳', 'xp_reward': 300},
        {'name': 'Time Champion', 'description': '50 hours total practice time', 'category': 'time', 'tier': 'gold', 'requirement_type': 'time', 'requirement_value': 3000, 'icon_emoji': '⌛', 'xp_reward': 1000},
        {'name': 'Lifetime Learner', 'description': '100 hours total practice time', 'category': 'time', 'tier': 'platinum', 'requirement_type': 'time', 'requirement_value': 6000, 'icon_emoji': '🕰️', 'xp_reward': 2500},
        
        # Speed Achievements (Efficiency)
        {'name': 'Speed Demon', 'description': 'Answer 10 questions in under 30 seconds each', 'category': 'speed', 'tier': 'silver', 'requirement_type': 'count', 'requirement_value': 10, 'icon_emoji': '⚡', 'xp_reward': 150},
        {'name': 'Lightning Fast', 'description': 'Answer 50 questions in under 20 seconds each', 'category': 'speed', 'tier': 'gold', 'requirement_type': 'count', 'requirement_value': 50, 'icon_emoji': '💨', 'xp_reward': 500},
        
        # Special Achievements (Milestones)
        {'name': 'Welcome Aboard', 'description': 'Complete first assessment', 'category': 'special', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 1, 'icon_emoji': '🎉', 'xp_reward': 100},
        {'name': 'Early Bird', 'description': 'Log in before 8 AM', 'category': 'special', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 1, 'icon_emoji': '🌅', 'xp_reward': 25},
        {'name': 'Night Owl', 'description': 'Log in after 10 PM', 'category': 'special', 'tier': 'bronze', 'requirement_type': 'count', 'requirement_value': 1, 'icon_emoji': '🦉', 'xp_reward': 25},
        {'name': 'Weekend Warrior', 'description': 'Practice on Saturday and Sunday', 'category': 'special', 'tier': 'silver', 'requirement_type': 'count', 'requirement_value': 1, 'icon_emoji': '🏖️', 'xp_reward': 100},
        {'name': 'Daily Dedication', 'description': '7-day login streak', 'category': 'special', 'tier': 'gold', 'requirement_type': 'streak', 'requirement_value': 7, 'icon_emoji': '📅', 'xp_reward': 500},
        {'name': 'Monthly Master', 'description': '30-day login streak', 'category': 'special', 'tier': 'platinum', 'requirement_type': 'streak', 'requirement_value': 30, 'icon_emoji': '📆', 'xp_reward': 2000},
        {'name': 'Completionist', 'description': 'Reach 100% mastery in one grade level', 'category': 'special', 'tier': 'diamond', 'requirement_type': 'percentage', 'requirement_value': 100, 'icon_emoji': '🏆', 'xp_reward': 5000},
    ]
    
    @staticmethod
    def seed_achievements():
        """Seed achievement definitions."""
        for achievement_data in AchievementService.ACHIEVEMENTS:
            # Check if achievement already exists
            existing = Achievement.query.filter_by(name=achievement_data['name']).first()
            if not existing:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
        
        db.session.commit()
        return len(AchievementService.ACHIEVEMENTS)
    
    @staticmethod
    def get_or_create_student_achievement(student_id, achievement_id):
        """Get or create student achievement record."""
        student_achievement = StudentAchievement.query.filter_by(
            student_id=student_id,
            achievement_id=achievement_id
        ).first()
        
        if not student_achievement:
            student_achievement = StudentAchievement(
                student_id=student_id,
                achievement_id=achievement_id,
                progress=0
            )
            db.session.add(student_achievement)
            db.session.commit()
        
        return student_achievement
    
    @staticmethod
    def update_progress(student_id, achievement_id, delta, description=None):
        """Update achievement progress."""
        student_achievement = AchievementService.get_or_create_student_achievement(student_id, achievement_id)
        
        # Don't update if already unlocked
        if student_achievement.unlocked_at:
            return student_achievement
        
        # Update progress
        old_progress = student_achievement.progress
        student_achievement.progress += delta
        student_achievement.updated_at = datetime.utcnow()
        
        # Log progress change
        log = AchievementProgressLog(
            student_id=student_id,
            achievement_id=achievement_id,
            student_achievement_id=student_achievement.id,
            progress_delta=delta,
            new_progress=student_achievement.progress,
            description=description
        )
        db.session.add(log)
        db.session.commit()
        
        # Check if should unlock
        if student_achievement.progress >= student_achievement.achievement.requirement_value:
            AchievementService.unlock_achievement(student_id, achievement_id)
        
        return student_achievement
    
    @staticmethod
    def unlock_achievement(student_id, achievement_id):
        """Unlock achievement and award XP."""
        student_achievement = StudentAchievement.query.filter_by(
            student_id=student_id,
            achievement_id=achievement_id
        ).first()
        
        if not student_achievement or student_achievement.unlocked_at:
            return None
        
        # Unlock
        student_achievement.unlocked_at = datetime.utcnow()
        student_achievement.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Award XP
        achievement = student_achievement.achievement
        if achievement.xp_reward > 0:
            GamificationService.award_xp(
                student_id=student_id,
                action_type='achievement_unlock',
                base_xp=achievement.xp_reward,
                metadata={'achievement_name': achievement.name}
            )
        
        return student_achievement
    
    @staticmethod
    def get_student_achievements(student_id, category=None, unlocked_only=False):
        """Get student's achievements with progress."""
        # Get all achievements
        query = Achievement.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        
        achievements = query.all()
        
        # Get student progress for each
        result = []
        for achievement in achievements:
            student_achievement = StudentAchievement.query.filter_by(
                student_id=student_id,
                achievement_id=achievement.id
            ).first()
            
            if student_achievement:
                data = student_achievement.to_dict()
            else:
                # Create default data for not-started achievements
                data = {
                    'student_id': student_id,
                    'achievement_id': achievement.id,
                    'progress': 0,
                    'unlocked_at': None,
                    'is_displayed': False,
                    'achievement': achievement.to_dict(),
                    'progress_percentage': 0,
                    'is_unlocked': False
                }
            
            if unlocked_only and not data['is_unlocked']:
                continue
            
            result.append(data)
        
        return result
    
    @staticmethod
    def get_unlocked_achievements(student_id):
        """Get student's unlocked achievements."""
        return AchievementService.get_student_achievements(student_id, unlocked_only=True)
    
    @staticmethod
    def get_in_progress_achievements(student_id, limit=5):
        """Get achievements close to unlocking."""
        student_achievements = StudentAchievement.query.filter(
            and_(
                StudentAchievement.student_id == student_id,
                StudentAchievement.unlocked_at == None
            )
        ).all()
        
        # Calculate progress percentage and sort
        progress_list = []
        for sa in student_achievements:
            if sa.achievement.requirement_value > 0:
                percentage = (sa.progress / sa.achievement.requirement_value) * 100
                if percentage > 0:  # Only include started achievements
                    progress_list.append((sa, percentage))
        
        # Sort by progress percentage descending
        progress_list.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N
        return [sa.to_dict() for sa, _ in progress_list[:limit]]
    
    @staticmethod
    def get_displayed_achievements(student_id):
        """Get achievements displayed on profile."""
        student_achievements = StudentAchievement.query.filter_by(
            student_id=student_id,
            is_displayed=True
        ).all()
        
        return [sa.to_dict() for sa in student_achievements]
    
    @staticmethod
    def toggle_display(student_id, achievement_id):
        """Toggle achievement display on profile."""
        student_achievement = StudentAchievement.query.filter_by(
            student_id=student_id,
            achievement_id=achievement_id
        ).first()
        
        if not student_achievement or not student_achievement.unlocked_at:
            return None
        
        student_achievement.is_displayed = not student_achievement.is_displayed
        student_achievement.updated_at = datetime.utcnow()
        db.session.commit()
        
        return student_achievement
    
    @staticmethod
    def get_achievement_stats(student_id):
        """Get achievement statistics."""
        all_achievements = Achievement.query.filter_by(is_active=True).count()
        unlocked = StudentAchievement.query.filter(
            and_(
                StudentAchievement.student_id == student_id,
                StudentAchievement.unlocked_at != None
            )
        ).count()
        
        displayed = StudentAchievement.query.filter_by(
            student_id=student_id,
            is_displayed=True
        ).count()
        
        # Get recent unlocks
        recent = StudentAchievement.query.filter(
            and_(
                StudentAchievement.student_id == student_id,
                StudentAchievement.unlocked_at != None
            )
        ).order_by(StudentAchievement.unlocked_at.desc()).limit(5).all()
        
        return {
            'total_achievements': all_achievements,
            'unlocked_count': unlocked,
            'displayed_count': displayed,
            'completion_percentage': (unlocked / all_achievements * 100) if all_achievements > 0 else 0,
            'recent_unlocks': [sa.to_dict() for sa in recent]
        }
    
    @staticmethod
    def track_action(student_id, action_type, metadata=None):
        """Track action and update relevant achievements."""
        if metadata is None:
            metadata = {}
        
        # Map actions to achievements
        updates = []
        
        if action_type == 'question_complete':
            # Practice achievements
            updates.append(('First Steps', 1, 'Answered a question'))
            updates.append(('Dedicated Learner', 1, 'Answered a question'))
            updates.append(('Practice Master', 1, 'Answered a question'))
            updates.append(('Question Champion', 1, 'Answered a question'))
            updates.append(('Practice Legend', 1, 'Answered a question'))
            
            # Accuracy achievements (if first try)
            if metadata.get('first_try'):
                updates.append(('Sharp Shooter', 1, 'First-try correct'))
                updates.append(('Precision Expert', 1, 'First-try correct'))
                updates.append(('Perfect Aim', 1, 'First-try correct'))
                updates.append(('Flawless Performer', 1, 'First-try correct'))
            
            # Speed achievements (if fast)
            time_taken = metadata.get('time_taken', 999)
            if time_taken < 30:
                updates.append(('Speed Demon', 1, f'Answered in {time_taken}s'))
            if time_taken < 20:
                updates.append(('Lightning Fast', 1, f'Answered in {time_taken}s'))
        
        elif action_type == 'skill_mastered':
            updates.append(('First Mastery', 1, 'Mastered a skill'))
            updates.append(('Skill Collector', 1, 'Mastered a skill'))
            updates.append(('Mastery Expert', 1, 'Mastered a skill'))
            updates.append(('Mastery Champion', 1, 'Mastered a skill'))
            updates.append(('Complete Mastery', 1, 'Mastered a skill'))
        
        elif action_type == 'review_complete':
            updates.append(('Reviewer', 1, 'Completed a review'))
            updates.append(('Review Regular', 1, 'Completed a review'))
            updates.append(('Review Expert', 1, 'Completed a review'))
            
            if metadata.get('perfect'):
                updates.append(('Perfect Reviewer', 1, 'Perfect review'))
        
        elif action_type == 'video_watch':
            updates.append(('Video Watcher', 1, 'Watched a video'))
        
        elif action_type == 'resource_download':
            updates.append(('Resource Explorer', 1, 'Downloaded a resource'))
        
        elif action_type == 'example_try':
            updates.append(('Interactive Learner', 1, 'Tried an example'))
        
        elif action_type == 'hint_use':
            updates.append(('Hint Seeker', 1, 'Used a hint'))
        
        elif action_type == 'solution_view':
            updates.append(('Solution Student', 1, 'Viewed a solution'))
        
        elif action_type == 'assessment_complete':
            updates.append(('Welcome Aboard', 1, 'Completed assessment'))
        
        # Apply updates
        for achievement_name, delta, description in updates:
            achievement = Achievement.query.filter_by(name=achievement_name).first()
            if achievement:
                AchievementService.update_progress(student_id, achievement.id, delta, description)
        
        return len(updates)

