"""
Service for managing daily challenges.
"""
from datetime import datetime, timedelta
import random
from src.database import db
from src.models.daily_challenge import DailyChallenge
from src.models.student import Student
from src.models.assessment import Skill
from src.models.gamification import StudentProgress
from src.services.gamification_service import GamificationService


class ChallengeService:
    """Service for daily challenge operations."""
    
    # Challenge type definitions
    CHALLENGE_TYPES = {
        'question_marathon': {
            'name': 'Question Marathon',
            'description_template': 'Answer {target} questions correctly today!',
            'xp': {'easy': 50, 'medium': 100, 'hard': 150},
            'targets': {'easy': 5, 'medium': 10, 'hard': 15}
        },
        'skill_focus': {
            'name': 'Skill Focus',
            'description_template': 'Practice {skill_name}! Answer {target} questions.',
            'xp': {'easy': 75, 'medium': 125, 'hard': 200},
            'targets': {'easy': 3, 'medium': 5, 'hard': 10}
        },
        'perfect_streak': {
            'name': 'Perfect Streak',
            'description_template': 'Get {target} questions correct in a row!',
            'xp': {'easy': 100, 'medium': 150, 'hard': 250},
            'targets': {'easy': 3, 'medium': 5, 'hard': 10}
        }
    }
    
    @staticmethod
    def generate_daily_challenges(student_id):
        """Generate 3 new daily challenges for a student."""
        student = Student.query.get(student_id)
        if not student:
            return None
        
        # Check if challenges already exist for today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        existing = DailyChallenge.query.filter(
            DailyChallenge.student_id == student_id,
            DailyChallenge.created_at >= today_start,
            DailyChallenge.status == 'active'
        ).count()
        
        if existing >= 3:
            return DailyChallenge.query.filter(
                DailyChallenge.student_id == student_id,
                DailyChallenge.status == 'active'
            ).all()
        
        # Expire old challenges
        ChallengeService._expire_old_challenges(student_id)
        
        # Determine difficulty distribution based on student level
        progress = StudentProgress.query.filter_by(student_id=student_id).first()
        level = progress.current_level if progress else 1
        
        difficulties = ChallengeService._get_difficulty_distribution(level)
        
        # Select 3 random challenge types (no duplicates)
        challenge_types = random.sample(list(ChallengeService.CHALLENGE_TYPES.keys()), 3)
        
        challenges = []
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        for i, challenge_type in enumerate(challenge_types):
            difficulty = difficulties[i]
            challenge = ChallengeService._create_challenge(
                student_id,
                challenge_type,
                difficulty,
                expires_at
            )
            challenges.append(challenge)
        
        db.session.commit()
        return challenges
    
    @staticmethod
    def _get_difficulty_distribution(level):
        """Get difficulty distribution based on student level."""
        if level <= 3:
            pool = ['easy'] * 6 + ['medium'] * 3 + ['hard'] * 1
        elif level <= 7:
            pool = ['easy'] * 3 + ['medium'] * 5 + ['hard'] * 2
        elif level <= 12:
            pool = ['easy'] * 1 + ['medium'] * 4 + ['hard'] * 5
        else:
            pool = ['easy'] * 1 + ['medium'] * 3 + ['hard'] * 6
        
        return random.sample(pool, 3)
    
    @staticmethod
    def _create_challenge(student_id, challenge_type, difficulty, expires_at):
        """Create a single challenge."""
        config = ChallengeService.CHALLENGE_TYPES[challenge_type]
        target = config['targets'][difficulty]
        bonus_xp = config['xp'][difficulty]
        
        # For skill_focus, select a random skill
        target_skill_id = None
        description = config['description_template'].format(target=target, skill_name='a skill')
        
        if challenge_type == 'skill_focus':
            skill = Skill.query.order_by(db.func.random()).first()
            if skill:
                target_skill_id = skill.id
                description = config['description_template'].format(
                    target=target,
                    skill_name=skill.name
                )
        else:
            description = config['description_template'].format(target=target)
        
        challenge = DailyChallenge(
            student_id=student_id,
            challenge_type=challenge_type,
            difficulty=difficulty,
            description=description,
            target_value=target,
            current_progress=0,
            target_skill_id=target_skill_id,
            bonus_xp=bonus_xp,
            status='active',
            expires_at=expires_at
        )
        
        db.session.add(challenge)
        return challenge
    
    @staticmethod
    def _expire_old_challenges(student_id):
        """Expire challenges that have passed their expiration time."""
        expired = DailyChallenge.query.filter(
            DailyChallenge.student_id == student_id,
            DailyChallenge.status == 'active',
            DailyChallenge.expires_at < datetime.utcnow()
        ).all()
        
        for challenge in expired:
            challenge.status = 'expired'
        
        if expired:
            db.session.commit()
    
    @staticmethod
    def get_active_challenges(student_id):
        """Get all active challenges for a student."""
        # Expire old challenges first
        ChallengeService._expire_old_challenges(student_id)
        
        # Get active challenges
        challenges = DailyChallenge.query.filter(
            DailyChallenge.student_id == student_id,
            DailyChallenge.status == 'active'
        ).order_by(DailyChallenge.created_at).all()
        
        # Generate new challenges if none exist
        if len(challenges) == 0:
            challenges = ChallengeService.generate_daily_challenges(student_id)
        
        return challenges
    
    @staticmethod
    def update_progress(challenge_id, increment=1):
        """Update challenge progress and check for completion."""
        challenge = DailyChallenge.query.get(challenge_id)
        if not challenge or challenge.status != 'active':
            return None
        
        # Check if expired
        if challenge.is_expired:
            challenge.status = 'expired'
            db.session.commit()
            return challenge
        
        # Update progress
        if not challenge.started_at:
            challenge.started_at = datetime.utcnow()
        
        challenge.current_progress = min(
            challenge.current_progress + increment,
            challenge.target_value
        )
        
        # Check for completion
        if challenge.current_progress >= challenge.target_value:
            challenge.status = 'completed'
            challenge.completed_at = datetime.utcnow()
            
            # Award bonus XP
            GamificationService.award_xp(
                challenge.student_id,
                'daily_challenge',
                base_xp=challenge.bonus_xp
            )
        
        db.session.commit()
        return challenge
    
    @staticmethod
    def get_challenge_stats(student_id):
        """Get challenge completion statistics."""
        total_completed = DailyChallenge.query.filter(
            DailyChallenge.student_id == student_id,
            DailyChallenge.status == 'completed'
        ).count()
        
        total_xp_earned = db.session.query(
            db.func.sum(DailyChallenge.bonus_xp)
        ).filter(
            DailyChallenge.student_id == student_id,
            DailyChallenge.status == 'completed'
        ).scalar() or 0
        
        total_challenges = DailyChallenge.query.filter(
            DailyChallenge.student_id == student_id,
            DailyChallenge.status.in_(['completed', 'expired'])
        ).count()
        
        completion_rate = total_completed / total_challenges if total_challenges > 0 else 0
        
        return {
            'total_completed': total_completed,
            'total_xp_earned': int(total_xp_earned),
            'completion_rate': round(completion_rate, 2),
            'total_challenges': total_challenges
        }
    
    @staticmethod
    def get_challenge_history(student_id, limit=30):
        """Get challenge completion history."""
        challenges = DailyChallenge.query.filter(
            DailyChallenge.student_id == student_id
        ).order_by(DailyChallenge.created_at.desc()).limit(limit).all()
        
        return [c.to_dict() for c in challenges]

