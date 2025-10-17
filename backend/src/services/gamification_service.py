"""
Gamification Service for managing XP, levels, and rewards.
"""
from src.database import db
from src.models.gamification import StudentProgress, XPTransaction, LevelReward, StudentReward
from datetime import datetime, timedelta


class GamificationService:
    """Service for managing gamification features."""

    # Base XP values for different actions
    XP_VALUES = {
        'question_complete': 10,
        'question_correct': 5,  # Bonus
        'question_first_try': 10,  # Bonus
        'assessment_complete': 50,
        'skill_mastered': 100,
        'review_complete': 20,
        'review_perfect': 30,  # Bonus
        'video_watch': 5,
        'video_complete': 5,  # Bonus
        'example_interact': 5,
        'resource_download': 2,
        'daily_login': 5
    }

    # Difficulty multipliers
    DIFFICULTY_MULTIPLIERS = {
        'easy': 1.0,
        'medium': 1.5,
        'hard': 2.0
    }

    # Streak multipliers
    STREAK_MULTIPLIERS = {
        3: 1.2,
        5: 1.5,
        10: 2.0
    }

    @staticmethod
    def get_or_create_progress(student_id):
        """Get or create student progress record."""
        progress = StudentProgress.query.filter_by(student_id=student_id).first()
        
        if not progress:
            progress = StudentProgress(
                student_id=student_id,
                total_xp=0,
                current_level=1,
                xp_to_next_level=100,
                level_title='Novice',
                xp_multiplier=1.0
            )
            db.session.add(progress)
            db.session.commit()
        
        return progress

    @staticmethod
    def award_xp(student_id, action_type, base_xp=None, difficulty=None, metadata=None):
        """
        Award XP to a student for an action.
        
        Args:
            student_id: Student ID
            action_type: Type of action (e.g., 'question_correct')
            base_xp: Base XP amount (optional, uses default if not provided)
            difficulty: Difficulty level for multiplier (easy, medium, hard)
            metadata: Additional context (dict)
        
        Returns:
            dict with XP awarded, level info, and level-up status
        """
        # Get or create progress
        progress = GamificationService.get_or_create_progress(student_id)
        
        # Determine base XP
        if base_xp is None:
            base_xp = GamificationService.XP_VALUES.get(action_type, 0)
        
        # Calculate multiplier
        multiplier = progress.xp_multiplier
        
        # Apply difficulty multiplier
        if difficulty:
            difficulty_mult = GamificationService.DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
            multiplier *= difficulty_mult
        
        # Apply streak multiplier if in metadata
        if metadata and 'streak' in metadata:
            streak = metadata['streak']
            for streak_threshold, streak_mult in sorted(GamificationService.STREAK_MULTIPLIERS.items(), reverse=True):
                if streak >= streak_threshold:
                    multiplier *= streak_mult
                    break
        
        # Calculate bonus XP
        bonus_xp = 0
        if metadata:
            if metadata.get('first_try'):
                bonus_xp += GamificationService.XP_VALUES.get('question_first_try', 0)
            if metadata.get('perfect'):
                bonus_xp += GamificationService.XP_VALUES.get('review_perfect', 0)
        
        # Calculate total XP
        base_with_mult = int(base_xp * multiplier)
        bonus_with_mult = int(bonus_xp * multiplier) if bonus_xp > 0 else 0
        total_xp = base_with_mult + bonus_with_mult
        
        # Create transaction
        transaction = XPTransaction(
            student_id=student_id,
            action_type=action_type,
            base_xp=base_xp,
            multiplier=multiplier,
            bonus_xp=bonus_xp,
            total_xp=total_xp,
            description=GamificationService._generate_description(action_type, difficulty, metadata),
            extra_data=metadata
        )
        db.session.add(transaction)
        
        # Update progress
        previous_level = progress.current_level
        progress.total_xp += total_xp
        
        # Check for level up
        leveled_up = False
        new_rewards = []
        
        while progress.total_xp >= StudentProgress.calculate_xp_for_level(progress.current_level + 1):
            progress.current_level += 1
            leveled_up = True
            
            # Update level title
            progress.level_title = StudentProgress.get_level_title(progress.current_level)
            
            # Unlock rewards for this level
            level_rewards = LevelReward.query.filter_by(
                level=progress.current_level,
                is_active=True
            ).all()
            
            for reward in level_rewards:
                student_reward = StudentReward(
                    student_id=student_id,
                    reward_id=reward.id
                )
                db.session.add(student_reward)
                new_rewards.append(reward.to_dict())
        
        # Update XP to next level
        progress.xp_to_next_level = (
            StudentProgress.calculate_xp_for_level(progress.current_level + 1) - 
            progress.total_xp
        )
        
        db.session.commit()
        
        return {
            'xp_awarded': total_xp,
            'total_xp': progress.total_xp,
            'previous_level': previous_level,
            'current_level': progress.current_level,
            'level_title': progress.level_title,
            'leveled_up': leveled_up,
            'new_rewards': new_rewards,
            'xp_to_next_level': progress.xp_to_next_level,
            'progress_percentage': progress.get_progress_percentage(),
            'transaction_id': transaction.id
        }

    @staticmethod
    def _generate_description(action_type, difficulty=None, metadata=None):
        """Generate human-readable description for XP transaction."""
        descriptions = {
            'question_complete': 'Completed a question',
            'question_correct': 'Correct answer',
            'assessment_complete': 'Completed assessment',
            'skill_mastered': 'Mastered a skill',
            'review_complete': 'Completed review',
            'video_watch': 'Watched video',
            'example_interact': 'Interacted with example',
            'resource_download': 'Downloaded resource',
            'daily_login': 'Daily login bonus'
        }
        
        desc = descriptions.get(action_type, action_type.replace('_', ' ').title())
        
        if difficulty:
            desc += f' ({difficulty})'
        
        if metadata:
            if metadata.get('first_try'):
                desc += ' - First try!'
            if metadata.get('perfect'):
                desc += ' - Perfect!'
            if metadata.get('streak'):
                desc += f' - {metadata["streak"]} streak!'
        
        return desc

    @staticmethod
    def get_student_progress(student_id):
        """Get detailed progress for a student."""
        progress = GamificationService.get_or_create_progress(student_id)
        
        # Get rank
        all_progress = StudentProgress.query.order_by(StudentProgress.total_xp.desc()).all()
        rank = next((i + 1 for i, p in enumerate(all_progress) if p.student_id == student_id), None)
        
        result = progress.to_dict()
        result['rank'] = rank
        result['total_students'] = len(all_progress)
        result['xp_for_current_level'] = StudentProgress.calculate_xp_for_level(progress.current_level)
        
        return result

    @staticmethod
    def get_xp_history(student_id, limit=20):
        """Get recent XP transactions for a student."""
        transactions = XPTransaction.query.filter_by(student_id=student_id).order_by(
            XPTransaction.created_at.desc()
        ).limit(limit).all()
        
        return [t.to_dict() for t in transactions]

    @staticmethod
    def get_student_rewards(student_id):
        """Get unlocked and upcoming rewards for a student."""
        progress = GamificationService.get_or_create_progress(student_id)
        
        # Get unlocked rewards
        unlocked = StudentReward.query.filter_by(student_id=student_id).all()
        unlocked_rewards = [r.to_dict() for r in unlocked]
        
        # Get upcoming rewards (next 5 levels)
        upcoming_rewards = []
        for level in range(progress.current_level + 1, progress.current_level + 6):
            level_rewards = LevelReward.query.filter_by(level=level, is_active=True).all()
            for reward in level_rewards:
                reward_dict = reward.to_dict()
                reward_dict['xp_required'] = StudentProgress.calculate_xp_for_level(level)
                upcoming_rewards.append(reward_dict)
        
        return {
            'unlocked_rewards': unlocked_rewards,
            'upcoming_rewards': upcoming_rewards
        }

    @staticmethod
    def get_leaderboard(timeframe='all', limit=10):
        """
        Get leaderboard rankings.
        
        Args:
            timeframe: 'all', 'week', 'month'
            limit: Number of top students to return
        """
        if timeframe == 'all':
            # All-time leaderboard
            top_students = StudentProgress.query.order_by(
                StudentProgress.total_xp.desc()
            ).limit(limit).all()
            
            leaderboard = []
            for i, progress in enumerate(top_students, 1):
                leaderboard.append({
                    'rank': i,
                    'student_id': progress.student_id,
                    'student_name': progress.student.name if progress.student else 'Unknown',
                    'level': progress.current_level,
                    'level_title': progress.level_title,
                    'total_xp': progress.total_xp
                })
        
        elif timeframe in ['week', 'month']:
            # Time-based leaderboard
            days = 7 if timeframe == 'week' else 30
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get XP earned in timeframe
            from sqlalchemy import func
            xp_in_period = db.session.query(
                XPTransaction.student_id,
                func.sum(XPTransaction.total_xp).label('xp_earned')
            ).filter(
                XPTransaction.created_at >= cutoff_date
            ).group_by(
                XPTransaction.student_id
            ).order_by(
                func.sum(XPTransaction.total_xp).desc()
            ).limit(limit).all()
            
            leaderboard = []
            for i, (student_id, xp_earned) in enumerate(xp_in_period, 1):
                progress = StudentProgress.query.filter_by(student_id=student_id).first()
                leaderboard.append({
                    'rank': i,
                    'student_id': student_id,
                    'student_name': progress.student.name if progress and progress.student else 'Unknown',
                    'level': progress.current_level if progress else 1,
                    'level_title': progress.level_title if progress else 'Novice',
                    'total_xp': progress.total_xp if progress else 0,
                    f'xp_this_{timeframe}': int(xp_earned)
                })
        
        return leaderboard

    @staticmethod
    def seed_level_rewards():
        """Seed initial level rewards."""
        rewards_data = [
            # Every 5 levels: Title
            {'level': 2, 'reward_type': 'title', 'reward_value': 'novice', 'description': 'Novice title'},
            {'level': 5, 'reward_type': 'title', 'reward_value': 'apprentice', 'description': 'Apprentice title'},
            {'level': 10, 'reward_type': 'title', 'reward_value': 'practitioner', 'description': 'Practitioner title'},
            {'level': 15, 'reward_type': 'title', 'reward_value': 'expert', 'description': 'Expert title'},
            {'level': 20, 'reward_type': 'title', 'reward_value': 'master', 'description': 'Master title'},
            {'level': 25, 'reward_type': 'title', 'reward_value': 'grandmaster', 'description': 'Grandmaster title'},
            {'level': 30, 'reward_type': 'title', 'reward_value': 'legend', 'description': 'Legend title'},
            
            # Badges
            {'level': 3, 'reward_type': 'badge', 'reward_value': 'bronze', 'description': 'Bronze badge'},
            {'level': 10, 'reward_type': 'badge', 'reward_value': 'silver', 'description': 'Silver badge'},
            {'level': 20, 'reward_type': 'badge', 'reward_value': 'gold', 'description': 'Gold badge'},
            {'level': 30, 'reward_type': 'badge', 'reward_value': 'platinum', 'description': 'Platinum badge'},
            {'level': 50, 'reward_type': 'badge', 'reward_value': 'diamond', 'description': 'Diamond badge'},
            
            # Avatar frames
            {'level': 4, 'reward_type': 'avatar', 'reward_value': 'frame_bronze', 'description': 'Bronze avatar frame'},
            {'level': 12, 'reward_type': 'avatar', 'reward_value': 'frame_silver', 'description': 'Silver avatar frame'},
            {'level': 22, 'reward_type': 'avatar', 'reward_value': 'frame_gold', 'description': 'Gold avatar frame'},
        ]
        
        for reward_data in rewards_data:
            existing = LevelReward.query.filter_by(
                level=reward_data['level'],
                reward_type=reward_data['reward_type']
            ).first()
            
            if not existing:
                reward = LevelReward(**reward_data)
                db.session.add(reward)
        
        db.session.commit()

