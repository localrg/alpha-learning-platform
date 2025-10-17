"""
Service for managing student profiles.
"""
from src.database import db
from src.models.student import Student
from src.models.gamification import StudentProgress
from src.models.achievement import StudentAchievement, Achievement
from src.models.streak import StreakTracking
from src.models.learning_path import LearningPath


class ProfileService:
    """Service for student profile management."""
    
    @staticmethod
    def get_profile(student_id, viewer_id=None):
        """
        Get student profile with privacy checks.
        
        Args:
            student_id: ID of student whose profile to view
            viewer_id: ID of student viewing the profile (None for public view)
            
        Returns:
            dict: Profile data if allowed, None if private
        """
        student = Student.query.get(student_id)
        if not student:
            return None
        
        # Check privacy
        is_own_profile = (viewer_id == student_id)
        
        if not is_own_profile:
            if student.profile_visibility == 'private':
                return {'error': 'This profile is private'}
            # TODO: Check 'friends' visibility when friend system is implemented
        
        # Build profile data
        profile = student.to_dict()
        
        # Add stats if allowed
        if is_own_profile or student.show_stats:
            profile['stats'] = ProfileService._get_stats(student_id)
        
        # Add achievements if allowed
        if is_own_profile or student.show_achievements:
            profile['achievements'] = ProfileService._get_achievements(student_id)
        
        # Add activity if allowed
        if is_own_profile or student.show_activity:
            profile['activity'] = ProfileService._get_activity(student_id)
        
        return profile
    
    @staticmethod
    def _get_stats(student_id):
        """Get student statistics."""
        stats = {}
        
        # Gamification stats
        progress = StudentProgress.query.filter_by(student_id=student_id).first()
        if progress:
            stats['level'] = progress.current_level
            stats['xp'] = progress.total_xp
            stats['xp_to_next_level'] = progress.xp_to_next_level
        
        # Streak stats
        streak = StreakTracking.query.filter_by(student_id=student_id).first()
        if streak:
            stats['login_streak'] = streak.login_streak
            stats['login_streak_best'] = streak.login_streak_best
            stats['practice_streak'] = streak.practice_streak
            stats['practice_streak_best'] = streak.practice_streak_best
        
        # Learning stats
        learning_paths = LearningPath.query.filter_by(student_id=student_id).all()
        stats['total_skills'] = len(learning_paths)
        stats['mastered_skills'] = sum(1 for lp in learning_paths if lp.mastery_achieved)
        stats['total_questions'] = sum(lp.total_questions for lp in learning_paths)
        
        if stats['total_questions'] > 0:
            total_correct = sum(lp.correct_answers for lp in learning_paths)
            stats['accuracy'] = round((total_correct / stats['total_questions']) * 100, 1)
        else:
            stats['accuracy'] = 0
        
        return stats
    
    @staticmethod
    def _get_achievements(student_id):
        """Get student achievements."""
        student_achievements = StudentAchievement.query.filter_by(
            student_id=student_id
        ).filter(StudentAchievement.unlocked_at.isnot(None)).all()
        
        achievements = []
        for sa in student_achievements:
            achievement = Achievement.query.get(sa.achievement_id)
            if achievement:
                achievements.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon_emoji,
                    'tier': achievement.tier,
                    'unlocked_at': sa.unlocked_at.isoformat() if sa.unlocked_at else None
                })
        
        # Sort by unlock date (most recent first)
        achievements.sort(key=lambda x: x['unlocked_at'] or '', reverse=True)
        
        return {
            'total': len(achievements),
            'featured': achievements[:6],  # Top 6 for display
            'all': achievements
        }
    
    @staticmethod
    def _get_activity(student_id):
        """Get recent activity."""
        # Get recent achievements
        recent_achievements = StudentAchievement.query.filter_by(
            student_id=student_id
        ).filter(StudentAchievement.unlocked_at.isnot(None)).order_by(StudentAchievement.unlocked_at.desc()).limit(5).all()
        
        activity = []
        for sa in recent_achievements:
            achievement = Achievement.query.get(sa.achievement_id)
            if achievement:
                activity.append({
                    'type': 'achievement',
                    'title': f'Unlocked "{achievement.name}"',
                    'icon': achievement.icon_emoji,
                    'timestamp': sa.unlocked_at.isoformat() if sa.unlocked_at else None
                })
        
        return activity
    
    @staticmethod
    def update_profile(student_id, **kwargs):
        """
        Update student profile.
        
        Args:
            student_id: ID of student
            **kwargs: Fields to update (bio, avatar, profile_visibility, etc.)
            
        Returns:
            dict: Updated profile
        """
        student = Student.query.get(student_id)
        if not student:
            return None
        
        # Update allowed fields
        allowed_fields = ['bio', 'avatar', 'profile_visibility', 'show_stats', 'show_achievements', 'show_activity']
        
        for field in allowed_fields:
            if field in kwargs:
                setattr(student, field, kwargs[field])
        
        db.session.commit()
        
        return ProfileService.get_profile(student_id, student_id)

