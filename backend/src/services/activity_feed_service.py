"""
Activity Feed Service
Business logic for social activity feed
"""

from datetime import datetime
from src.database import db
from src.models.activity_feed import ActivityFeed
from src.models.student import Student
from src.models.friendship import Friendship
from src.models.class_group import ClassMembership


class ActivityFeedService:
    """Service for managing activity feed"""
    
    @staticmethod
    def create_activity(student_id, activity_type, data):
        """Create a new activity entry"""
        try:
            activity = ActivityFeed(
                student_id=student_id,
                activity_type=activity_type,
                title=data.get('title'),
                description=data.get('description', ''),
                skill_id=data.get('skill_id'),
                achievement_id=data.get('achievement_id'),
                challenge_id=data.get('challenge_id'),
                class_id=data.get('class_id'),
                xp_earned=data.get('xp_earned', 0),
                level_reached=data.get('level_reached'),
                streak_days=data.get('streak_days'),
                accuracy=data.get('accuracy'),
                questions_answered=data.get('questions_answered'),
                visibility=data.get('visibility', 'friends')
            )
            
            db.session.add(activity)
            db.session.commit()
            
            return {'success': True, 'activity': activity.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_feed(student_id, filter_type=None, limit=50, offset=0):
        """Get personalized activity feed for student"""
        try:
            # Get friend IDs
            friend_ids = ActivityFeedService._get_friend_ids(student_id)
            
            # Get class member IDs
            class_member_ids = ActivityFeedService._get_class_member_ids(student_id)
            
            # Build query
            query = ActivityFeed.query
            
            # Filter by type if specified
            if filter_type:
                if filter_type == 'friends':
                    # Only friend activities
                    query = query.filter(
                        ActivityFeed.student_id.in_(friend_ids),
                        ActivityFeed.visibility.in_(['public', 'friends'])
                    )
                elif filter_type == 'classes':
                    # Only class member activities
                    query = query.filter(
                        ActivityFeed.student_id.in_(class_member_ids),
                        ActivityFeed.visibility.in_(['public', 'class'])
                    )
                elif filter_type == 'me':
                    # Only my activities
                    query = query.filter(ActivityFeed.student_id == student_id)
                elif filter_type in ['skill_mastery', 'level_up', 'achievement_unlock', 
                                    'challenge_complete', 'streak_milestone']:
                    # Filter by activity type
                    query = query.filter(
                        db.or_(
                            # Friend activities
                            db.and_(
                                ActivityFeed.student_id.in_(friend_ids),
                                ActivityFeed.visibility.in_(['public', 'friends'])
                            ),
                            # Class activities
                            db.and_(
                                ActivityFeed.student_id.in_(class_member_ids),
                                ActivityFeed.visibility.in_(['public', 'class'])
                            ),
                            # Own activities
                            ActivityFeed.student_id == student_id
                        ),
                        ActivityFeed.activity_type == filter_type
                    )
            else:
                # All visible activities (friends + classes + own)
                query = query.filter(
                    db.or_(
                        # Friend activities
                        db.and_(
                            ActivityFeed.student_id.in_(friend_ids),
                            ActivityFeed.visibility.in_(['public', 'friends'])
                        ),
                        # Class activities
                        db.and_(
                            ActivityFeed.student_id.in_(class_member_ids),
                            ActivityFeed.visibility.in_(['public', 'class'])
                        ),
                        # Own activities
                        ActivityFeed.student_id == student_id
                    )
                )
            
            # Order by newest first
            query = query.order_by(ActivityFeed.created_at.desc())
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            activities = query.limit(limit).offset(offset).all()
            
            # Convert to dict
            activity_list = [a.to_dict() for a in activities]
            
            return {
                'success': True,
                'activities': activity_list,
                'total': total_count,
                'has_more': (offset + limit) < total_count
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_student_activities(student_id, viewer_id, limit=20):
        """Get specific student's activities (respecting privacy)"""
        try:
            # Check relationship
            is_self = student_id == viewer_id
            is_friend = ActivityFeedService._is_friend(student_id, viewer_id)
            is_classmate = ActivityFeedService._is_classmate(student_id, viewer_id)
            
            # Build visibility filter
            if is_self:
                # Show all own activities
                visibility_filter = ActivityFeed.visibility.in_(['public', 'friends', 'class', 'private'])
            elif is_friend:
                # Show public and friends activities
                visibility_filter = ActivityFeed.visibility.in_(['public', 'friends'])
            elif is_classmate:
                # Show public and class activities
                visibility_filter = ActivityFeed.visibility.in_(['public', 'class'])
            else:
                # Show only public activities
                visibility_filter = ActivityFeed.visibility == 'public'
            
            activities = ActivityFeed.query.filter(
                ActivityFeed.student_id == student_id,
                visibility_filter
            ).order_by(ActivityFeed.created_at.desc()).limit(limit).all()
            
            return {
                'success': True,
                'activities': [a.to_dict() for a in activities]
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def delete_activity(activity_id, student_id):
        """Delete activity (owner only)"""
        try:
            activity = ActivityFeed.query.get(activity_id)
            
            if not activity:
                return {'error': 'Activity not found'}, 404
            
            if activity.student_id != student_id:
                return {'error': 'Only owner can delete activity'}, 403
            
            db.session.delete(activity)
            db.session.commit()
            
            return {'success': True, 'message': 'Activity deleted'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_activity_stats(student_id):
        """Get activity statistics for student"""
        try:
            # Total activities
            total = ActivityFeed.query.filter_by(student_id=student_id).count()
            
            # Activities by type
            by_type = {}
            for activity_type in ['skill_mastery', 'level_up', 'achievement_unlock', 
                                 'challenge_complete', 'streak_milestone']:
                count = ActivityFeed.query.filter_by(
                    student_id=student_id,
                    activity_type=activity_type
                ).count()
                by_type[activity_type] = count
            
            # Total XP from activities
            total_xp = db.session.query(
                db.func.sum(ActivityFeed.xp_earned)
            ).filter(ActivityFeed.student_id == student_id).scalar() or 0
            
            return {
                'success': True,
                'stats': {
                    'total_activities': total,
                    'by_type': by_type,
                    'total_xp_shown': int(total_xp)
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    # Helper methods
    
    @staticmethod
    def _get_friend_ids(student_id):
        """Get list of accepted friend IDs"""
        friendships = Friendship.query.filter(
            db.or_(
                db.and_(Friendship.requester_id == student_id, Friendship.status == 'accepted'),
                db.and_(Friendship.addressee_id == student_id, Friendship.status == 'accepted')
            )
        ).all()
        
        friend_ids = []
        for friendship in friendships:
            if friendship.requester_id == student_id:
                friend_ids.append(friendship.addressee_id)
            else:
                friend_ids.append(friendship.requester_id)
        
        return friend_ids
    
    @staticmethod
    def _get_class_member_ids(student_id):
        """Get list of classmate IDs"""
        # Get classes student is in
        memberships = ClassMembership.query.filter_by(student_id=student_id).all()
        class_ids = [m.class_id for m in memberships]
        
        # Get all members of those classes
        all_memberships = ClassMembership.query.filter(
            ClassMembership.class_id.in_(class_ids)
        ).all()
        
        member_ids = list(set([m.student_id for m in all_memberships if m.student_id != student_id]))
        
        return member_ids
    
    @staticmethod
    def _is_friend(student_id, viewer_id):
        """Check if viewer is friend of student"""
        friendship = Friendship.query.filter(
            db.or_(
                db.and_(Friendship.requester_id == student_id, Friendship.addressee_id == viewer_id),
                db.and_(Friendship.requester_id == viewer_id, Friendship.addressee_id == student_id)
            ),
            Friendship.status == 'accepted'
        ).first()
        
        return friendship is not None
    
    @staticmethod
    def _is_classmate(student_id, viewer_id):
        """Check if viewer is classmate of student"""
        # Get classes of student
        student_classes = ClassMembership.query.filter_by(student_id=student_id).all()
        student_class_ids = [m.class_id for m in student_classes]
        
        # Check if viewer is in any of those classes
        viewer_in_class = ClassMembership.query.filter(
            ClassMembership.student_id == viewer_id,
            ClassMembership.class_id.in_(student_class_ids)
        ).first()
        
        return viewer_in_class is not None
    
    # Activity creation helpers (to be called from other services)
    
    @staticmethod
    def on_skill_mastery(student_id, skill_name, accuracy, xp_earned):
        """Create activity when skill is mastered"""
        return ActivityFeedService.create_activity(student_id, 'skill_mastery', {
            'title': f'Mastered {skill_name}!',
            'description': f'{int(accuracy * 100)}% accuracy',
            'xp_earned': xp_earned,
            'accuracy': accuracy,
            'visibility': 'friends'
        })
    
    @staticmethod
    def on_level_up(student_id, new_level, total_xp):
        """Create activity when student levels up"""
        return ActivityFeedService.create_activity(student_id, 'level_up', {
            'title': f'Reached Level {new_level}!',
            'description': 'Awesome progress!',
            'level_reached': new_level,
            'visibility': 'friends'
        })
    
    @staticmethod
    def on_achievement_unlock(student_id, achievement_name, xp_earned):
        """Create activity when achievement is unlocked"""
        return ActivityFeedService.create_activity(student_id, 'achievement_unlock', {
            'title': f'Unlocked {achievement_name}!',
            'description': 'New achievement earned!',
            'xp_earned': xp_earned,
            'visibility': 'friends'
        })
    
    @staticmethod
    def on_challenge_complete(student_id, challenge_name, rank, xp_earned):
        """Create activity when challenge is completed"""
        rank_text = f'Ranked #{rank}' if rank else 'Completed'
        return ActivityFeedService.create_activity(student_id, 'challenge_complete', {
            'title': f'Completed {challenge_name}!',
            'description': f'{rank_text}',
            'xp_earned': xp_earned,
            'visibility': 'friends'
        })
    
    @staticmethod
    def on_streak_milestone(student_id, streak_days):
        """Create activity for streak milestone"""
        return ActivityFeedService.create_activity(student_id, 'streak_milestone', {
            'title': f'{streak_days} Day Streak!',
            'description': 'Keep up the great work!',
            'streak_days': streak_days,
            'visibility': 'friends'
        })

