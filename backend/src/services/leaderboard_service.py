"""
Leaderboard service for rankings and competition.
"""
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, func
from src.database import db
from src.models.student import Student
from src.models.gamification import StudentProgress
from src.models.achievement import StudentAchievement
from src.models.learning_path import LearningPath


class LeaderboardService:
    """Service for managing leaderboards and rankings."""
    
    @staticmethod
    def get_global_xp_leaderboard(limit=50, offset=0):
        """Get global XP leaderboard."""
        students = db.session.query(
            Student.id,
            Student.name,
            StudentProgress.total_xp,
            StudentProgress.current_level
        ).join(
            StudentProgress, Student.id == StudentProgress.student_id
        ).order_by(
            desc(StudentProgress.total_xp),
            Student.id  # Tie-breaker
        ).limit(limit).offset(offset).all()
        
        # Calculate ranks
        leaderboard = []
        for idx, (student_id, name, total_xp, level) in enumerate(students, start=offset+1):
            leaderboard.append({
                'rank': idx,
                'student_id': student_id,
                'student_name': name,
                'total_xp': total_xp,
                'level': level,
                'tier': LeaderboardService._get_tier_from_rank(idx)
            })
        
        return leaderboard
    
    @staticmethod
    def get_grade_leaderboard(grade, limit=50, offset=0):
        """Get grade-level XP leaderboard."""
        students = db.session.query(
            Student.id,
            Student.name,
            StudentProgress.total_xp,
            StudentProgress.current_level
        ).join(
            StudentProgress, Student.id == StudentProgress.student_id
        ).filter(
            Student.grade == grade
        ).order_by(
            desc(StudentProgress.total_xp),
            Student.id
        ).limit(limit).offset(offset).all()
        
        leaderboard = []
        for idx, (student_id, name, total_xp, level) in enumerate(students, start=offset+1):
            leaderboard.append({
                'rank': idx,
                'student_id': student_id,
                'student_name': name,
                'total_xp': total_xp,
                'level': level,
                'grade': grade,
                'tier': LeaderboardService._get_tier_from_rank(idx)
            })
        
        return leaderboard
    
    @staticmethod
    def get_skills_leaderboard(limit=50, offset=0):
        """Get skills mastered leaderboard."""
        # Count mastered skills per student
        students = db.session.query(
            Student.id,
            Student.name,
            Student.grade,
            func.count(LearningPath.id).label('skills_mastered')
        ).outerjoin(
            LearningPath, and_(
                Student.id == LearningPath.student_id,
                LearningPath.mastery_achieved == True
            )
        ).group_by(
            Student.id
        ).order_by(
            desc('skills_mastered'),
            Student.id
        ).limit(limit).offset(offset).all()
        
        leaderboard = []
        for idx, (student_id, name, grade, skills_mastered) in enumerate(students, start=offset+1):
            leaderboard.append({
                'rank': idx,
                'student_id': student_id,
                'student_name': name,
                'grade': grade,
                'skills_mastered': skills_mastered,
                'tier': LeaderboardService._get_tier_from_rank(idx)
            })
        
        return leaderboard
    
    @staticmethod
    def get_achievements_leaderboard(limit=50, offset=0):
        """Get achievements unlocked leaderboard."""
        students = db.session.query(
            Student.id,
            Student.name,
            Student.grade,
            func.count(StudentAchievement.id).label('achievements_unlocked')
        ).outerjoin(
            StudentAchievement, and_(
                Student.id == StudentAchievement.student_id,
                StudentAchievement.unlocked_at != None
            )
        ).group_by(
            Student.id
        ).order_by(
            desc('achievements_unlocked'),
            Student.id
        ).limit(limit).offset(offset).all()
        
        leaderboard = []
        for idx, (student_id, name, grade, achievements) in enumerate(students, start=offset+1):
            leaderboard.append({
                'rank': idx,
                'student_id': student_id,
                'student_name': name,
                'grade': grade,
                'achievements_unlocked': achievements,
                'tier': LeaderboardService._get_tier_from_rank(idx)
            })
        
        return leaderboard
    
    @staticmethod
    def get_student_rank(student_id, leaderboard_type='global_xp'):
        """Get specific student's rank in a leaderboard."""
        if leaderboard_type == 'global_xp':
            # Count students with more XP
            student_progress = StudentProgress.query.filter_by(student_id=student_id).first()
            if not student_progress:
                return None
            
            rank = db.session.query(func.count(StudentProgress.id)).filter(
                StudentProgress.total_xp > student_progress.total_xp
            ).scalar() + 1
            
            total_students = db.session.query(func.count(StudentProgress.id)).scalar()
            
            return {
                'rank': rank,
                'total_students': total_students,
                'percentile': (rank / total_students * 100) if total_students > 0 else 0,
                'tier': LeaderboardService._get_tier_from_rank(rank),
                'metric_value': student_progress.total_xp,
                'metric_name': 'Total XP'
            }
        
        elif leaderboard_type == 'skills':
            # Count students with more skills mastered
            student = Student.query.get(student_id)
            if not student:
                return None
            
            skills_mastered = LearningPath.query.filter_by(
                student_id=student_id,
                mastery_achieved=True
            ).count()
            
            rank = db.session.query(func.count(func.distinct(Student.id))).select_from(Student).outerjoin(
                LearningPath, and_(
                    Student.id == LearningPath.student_id,
                    LearningPath.mastery_achieved == True
                )
            ).group_by(Student.id).having(
                func.count(LearningPath.id) > skills_mastered
            ).scalar() or 0
            
            rank += 1
            
            total_students = Student.query.count()
            
            return {
                'rank': rank,
                'total_students': total_students,
                'percentile': (rank / total_students * 100) if total_students > 0 else 0,
                'tier': LeaderboardService._get_tier_from_rank(rank),
                'metric_value': skills_mastered,
                'metric_name': 'Skills Mastered'
            }
        
        elif leaderboard_type == 'achievements':
            # Count students with more achievements
            achievements_unlocked = StudentAchievement.query.filter(
                and_(
                    StudentAchievement.student_id == student_id,
                    StudentAchievement.unlocked_at != None
                )
            ).count()
            
            # This is simplified - in production would use a more efficient query
            rank = 1
            total_students = Student.query.count()
            
            return {
                'rank': rank,
                'total_students': total_students,
                'percentile': (rank / total_students * 100) if total_students > 0 else 0,
                'tier': LeaderboardService._get_tier_from_rank(rank),
                'metric_value': achievements_unlocked,
                'metric_name': 'Achievements Unlocked'
            }
        
        return None
    
    @staticmethod
    def get_nearby_students(student_id, leaderboard_type='global_xp', range_size=5):
        """Get students near the given student's rank."""
        rank_info = LeaderboardService.get_student_rank(student_id, leaderboard_type)
        if not rank_info:
            return []
        
        rank = rank_info['rank']
        start_rank = max(1, rank - range_size)
        
        # Get leaderboard around student's rank
        if leaderboard_type == 'global_xp':
            return LeaderboardService.get_global_xp_leaderboard(
                limit=range_size * 2 + 1,
                offset=start_rank - 1
            )
        elif leaderboard_type == 'skills':
            return LeaderboardService.get_skills_leaderboard(
                limit=range_size * 2 + 1,
                offset=start_rank - 1
            )
        elif leaderboard_type == 'achievements':
            return LeaderboardService.get_achievements_leaderboard(
                limit=range_size * 2 + 1,
                offset=start_rank - 1
            )
        
        return []
    
    @staticmethod
    def _get_tier_from_rank(rank):
        """Get tier badge based on rank."""
        if rank == 1:
            return 'champion'
        elif rank <= 3:
            return 'master'
        elif rank <= 10:
            return 'expert'
        elif rank <= 25:
            return 'intermediate'
        else:
            return 'beginner'
    
    @staticmethod
    def get_leaderboard_summary(student_id):
        """Get summary of student's ranks across all leaderboards."""
        summary = {}
        
        # Global XP
        global_rank = LeaderboardService.get_student_rank(student_id, 'global_xp')
        if global_rank:
            summary['global_xp'] = global_rank
        
        # Skills
        skills_rank = LeaderboardService.get_student_rank(student_id, 'skills')
        if skills_rank:
            summary['skills'] = skills_rank
        
        # Achievements
        achievements_rank = LeaderboardService.get_student_rank(student_id, 'achievements')
        if achievements_rank:
            summary['achievements'] = achievements_rank
        
        return summary

