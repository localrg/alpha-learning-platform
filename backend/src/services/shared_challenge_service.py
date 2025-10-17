"""
Shared Challenge Service
Business logic for shared challenges between students
"""

from datetime import datetime, timedelta
from src.database import db
from src.models.shared_challenge import SharedChallenge, ChallengeParticipant
from src.models.student import Student
from src.models.class_group import ClassGroup, ClassMembership
from src.models.friendship import Friendship
from src.services.gamification_service import GamificationService


class SharedChallengeService:
    """Service for managing shared challenges between students"""
    
    @staticmethod
    def calculate_xp_reward(skill_id, target_questions, target_accuracy):
        """Calculate XP reward for challenge"""
        base_xp = 50
        
        # Difficulty multiplier based on skill (simplified - could be from skill data)
        difficulty_multiplier = 1.5
        
        # More questions = more XP
        question_multiplier = target_questions / 10
        
        # Higher accuracy = more XP
        accuracy_multiplier = target_accuracy
        
        xp_reward = int(base_xp * difficulty_multiplier * question_multiplier * accuracy_multiplier)
        return max(xp_reward, 50)  # Minimum 50 XP
    
    @staticmethod
    def create_challenge(creator_id, data):
        """Create a new challenge"""
        try:
            # Validate creator
            creator = Student.query.get(creator_id)
            if not creator:
                return {'error': 'Creator not found'}, 404
            
            # Validate challenge type
            challenge_type = data.get('challenge_type')
            if challenge_type not in ['friend', 'class']:
                return {'error': 'Invalid challenge type'}, 400
            
            # For class challenges, verify creator is teacher
            class_id = data.get('class_id')
            if challenge_type == 'class':
                if not class_id:
                    return {'error': 'Class ID required for class challenges'}, 400
                
                class_group = ClassGroup.query.get(class_id)
                if not class_group:
                    return {'error': 'Class not found'}, 404
                
                # Check if creator is the teacher
                if class_group.teacher_id != creator.user_id:
                    return {'error': 'Only teachers can create class challenges'}, 403
            
            # Calculate end time
            duration_hours = data.get('duration_hours', 24)
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Calculate XP reward
            xp_reward = SharedChallengeService.calculate_xp_reward(
                data.get('skill_id'),
                data.get('target_questions'),
                data.get('target_accuracy')
            )
            
            # Create challenge
            challenge = SharedChallenge(
                title=data.get('title'),
                description=data.get('description', ''),
                creator_id=creator_id,
                challenge_type=challenge_type,
                class_id=class_id,
                mode=data.get('mode', 'competitive'),
                skill_id=data.get('skill_id'),
                target_questions=data.get('target_questions'),
                target_accuracy=data.get('target_accuracy'),
                start_time=start_time,
                end_time=end_time,
                xp_reward=xp_reward,
                status='active'
            )
            
            db.session.add(challenge)
            db.session.flush()  # Get challenge ID
            
            # Add participants
            participant_ids = []
            
            if challenge_type == 'friend':
                # Add specified friends
                participant_ids = data.get('participant_ids', [])
            elif challenge_type == 'class':
                # Add all class members
                memberships = ClassMembership.query.filter_by(class_id=class_id).all()
                participant_ids = [m.student_id for m in memberships]
            
            # Create participant records
            for student_id in participant_ids:
                participant = ChallengeParticipant(
                    challenge_id=challenge.id,
                    student_id=student_id,
                    status='invited'
                )
                db.session.add(participant)
            
            # Creator auto-accepts
            creator_participant = ChallengeParticipant(
                challenge_id=challenge.id,
                student_id=creator_id,
                status='accepted'
            )
            db.session.add(creator_participant)
            
            db.session.commit()
            
            return {'success': True, 'challenge': challenge.to_dict(include_participants=True)}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_challenge(challenge_id, student_id=None):
        """Get challenge details"""
        challenge = SharedChallenge.query.get(challenge_id)
        if not challenge:
            return {'error': 'Challenge not found'}, 404
        
        # Check if student is participant
        if student_id:
            participant = ChallengeParticipant.query.filter_by(
                challenge_id=challenge_id,
                student_id=student_id
            ).first()
            
            if not participant:
                return {'error': 'Not a participant in this challenge'}, 403
        
        # Get challenge data with participants
        data = challenge.to_dict(include_participants=True)
        
        # Add my participation if student_id provided
        if student_id:
            my_participation = ChallengeParticipant.query.filter_by(
                challenge_id=challenge_id,
                student_id=student_id
            ).first()
            
            if my_participation:
                data['my_participation'] = my_participation.to_dict(include_student=False)
        
        return {'success': True, 'challenge': data}, 200
    
    @staticmethod
    def get_student_challenges(student_id, filter_status=None):
        """Get all challenges for a student"""
        # Get all participations
        participations = ChallengeParticipant.query.filter_by(
            student_id=student_id
        ).all()
        
        challenges = []
        for participation in participations:
            challenge = participation.challenge
            
            # Apply status filter
            if filter_status:
                if filter_status == 'active' and challenge.status != 'active':
                    continue
                elif filter_status == 'completed' and challenge.status != 'completed':
                    continue
                elif filter_status == 'invited' and participation.status != 'invited':
                    continue
            
            # Build challenge data
            challenge_data = challenge.to_dict()
            challenge_data['my_participation'] = participation.to_dict(include_student=False)
            challenge_data['participant_count'] = len(challenge.participants)
            
            challenges.append(challenge_data)
        
        # Sort by end_time (soonest first)
        challenges.sort(key=lambda x: x['end_time'])
        
        return {'success': True, 'challenges': challenges}, 200
    
    @staticmethod
    def accept_challenge(challenge_id, student_id):
        """Accept a challenge invitation"""
        participant = ChallengeParticipant.query.filter_by(
            challenge_id=challenge_id,
            student_id=student_id
        ).first()
        
        if not participant:
            return {'error': 'Participation not found'}, 404
        
        if participant.status != 'invited':
            return {'error': 'Challenge already responded to'}, 400
        
        participant.status = 'accepted'
        participant.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'success': True, 'participation': participant.to_dict()}, 200
    
    @staticmethod
    def decline_challenge(challenge_id, student_id):
        """Decline a challenge invitation"""
        participant = ChallengeParticipant.query.filter_by(
            challenge_id=challenge_id,
            student_id=student_id
        ).first()
        
        if not participant:
            return {'error': 'Participation not found'}, 404
        
        if participant.status != 'invited':
            return {'error': 'Challenge already responded to'}, 400
        
        participant.status = 'declined'
        participant.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'success': True, 'participation': participant.to_dict()}, 200
    
    @staticmethod
    def update_progress(challenge_id, student_id, question_result):
        """Update participant progress after answering a question"""
        participant = ChallengeParticipant.query.filter_by(
            challenge_id=challenge_id,
            student_id=student_id
        ).first()
        
        if not participant:
            return {'error': 'Participation not found'}, 404
        
        if participant.status != 'accepted':
            return {'error': 'Must accept challenge first'}, 400
        
        # Update progress
        participant.questions_answered += 1
        if question_result.get('correct'):
            participant.questions_correct += 1
        
        # Recalculate accuracy
        if participant.questions_answered > 0:
            participant.accuracy = participant.questions_correct / participant.questions_answered
        
        participant.updated_at = datetime.utcnow()
        
        # Check for completion
        challenge = participant.challenge
        challenge_completed = False
        
        if (participant.questions_answered >= challenge.target_questions and
            participant.accuracy >= challenge.target_accuracy):
            participant.completed = True
            participant.completed_at = datetime.utcnow()
            challenge_completed = True
            
            # Award XP
            GamificationService.award_xp(student_id, 'challenge_completion', base_xp=challenge.xp_reward)
        
        db.session.commit()
        
        return {
            'success': True,
            'progress': participant.to_dict(include_student=False),
            'challenge_completed': challenge_completed
        }, 200
    
    @staticmethod
    def get_challenge_leaderboard(challenge_id):
        """Get ranked leaderboard for a challenge"""
        challenge = SharedChallenge.query.get(challenge_id)
        if not challenge:
            return {'error': 'Challenge not found'}, 404
        
        # Get all participants
        participants = ChallengeParticipant.query.filter_by(
            challenge_id=challenge_id
        ).all()
        
        # Sort by: completed first, then accuracy, then questions answered (more is better)
        def sort_key(p):
            return (
                not p.completed,  # Completed first (False < True)
                -p.accuracy,  # Higher accuracy first
                -p.questions_answered  # More questions first
            )
        
        participants.sort(key=sort_key)
        
        # Assign ranks
        for i, participant in enumerate(participants, 1):
            participant.rank = i
        
        db.session.commit()
        
        # Build leaderboard
        leaderboard = [p.to_dict() for p in participants]
        
        return {
            'success': True,
            'challenge': challenge.to_dict(),
            'leaderboard': leaderboard
        }, 200
    
    @staticmethod
    def complete_challenge(challenge_id):
        """Mark challenge as completed and award final rewards"""
        challenge = SharedChallenge.query.get(challenge_id)
        if not challenge:
            return {'error': 'Challenge not found'}, 404
        
        if challenge.status != 'active':
            return {'error': 'Challenge already completed or expired'}, 400
        
        challenge.status = 'completed'
        challenge.updated_at = datetime.utcnow()
        
        # Get leaderboard
        participants = ChallengeParticipant.query.filter_by(
            challenge_id=challenge_id,
            completed=True
        ).order_by(
            ChallengeParticipant.accuracy.desc(),
            ChallengeParticipant.questions_answered.desc()
        ).all()
        
        # Award bonus XP to top 3 in competitive mode
        if challenge.mode == 'competitive' and len(participants) > 0:
            bonuses = [0.5, 0.25, 0.1]  # 50%, 25%, 10% bonus
            
            for i, participant in enumerate(participants[:3]):
                bonus_xp = int(challenge.xp_reward * bonuses[i])
                GamificationService.award_xp(
                    participant.student_id,
                    f'challenge_rank_{i+1}',
                    base_xp=bonus_xp
                )
        
        db.session.commit()
        
        return {'success': True, 'challenge': challenge.to_dict()}, 200
    
    @staticmethod
    def delete_challenge(challenge_id, student_id):
        """Delete a challenge (creator only)"""
        challenge = SharedChallenge.query.get(challenge_id)
        if not challenge:
            return {'error': 'Challenge not found'}, 404
        
        if challenge.creator_id != student_id:
            return {'error': 'Only creator can delete challenge'}, 403
        
        db.session.delete(challenge)
        db.session.commit()
        
        return {'success': True, 'message': 'Challenge deleted'}, 200
    
    @staticmethod
    def expire_challenges():
        """Background task to expire old challenges"""
        now = datetime.utcnow()
        
        expired_challenges = SharedChallenge.query.filter(
            SharedChallenge.end_time < now,
            SharedChallenge.status == 'active'
        ).all()
        
        for challenge in expired_challenges:
            challenge.status = 'expired'
            challenge.updated_at = now
        
        db.session.commit()
        
        return {'success': True, 'expired_count': len(expired_challenges)}, 200

