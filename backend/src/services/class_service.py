"""
Service for managing class groups and memberships.
"""
import random
import string
from sqlalchemy import func
from src.database import db
from src.models.class_group import ClassGroup, ClassMembership
from src.models.student import Student
from src.models.user import User
from src.models.gamification import StudentProgress


class ClassService:
    """Service for class group operations."""

    @staticmethod
    def generate_invite_code():
        """Generate unique 6-character invite code."""
        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            ))
            if not ClassGroup.query.filter_by(invite_code=code).first():
                return code

    @staticmethod
    def create_class(teacher_id, name, description, grade_level):
        """Create a new class."""
        # Validate grade level
        if grade_level not in range(3, 9):
            raise ValueError("Grade level must be between 3 and 8")

        # Generate unique invite code
        invite_code = ClassService.generate_invite_code()

        # Create class
        class_group = ClassGroup(
            name=name,
            description=description,
            teacher_id=teacher_id,
            grade_level=grade_level,
            invite_code=invite_code
        )

        db.session.add(class_group)
        db.session.commit()

        return class_group

    @staticmethod
    def get_class(class_id):
        """Get class by ID."""
        return ClassGroup.query.get(class_id)

    @staticmethod
    def update_class(class_id, teacher_id, **kwargs):
        """Update class details (teacher only)."""
        class_group = ClassGroup.query.get(class_id)
        if not class_group:
            raise ValueError("Class not found")

        if class_group.teacher_id != teacher_id:
            raise ValueError("Only the teacher can update this class")

        # Update allowed fields
        for key in ['name', 'description', 'grade_level']:
            if key in kwargs:
                setattr(class_group, kwargs[key])

        db.session.commit()
        return class_group

    @staticmethod
    def delete_class(class_id, teacher_id):
        """Delete class (teacher only)."""
        class_group = ClassGroup.query.get(class_id)
        if not class_group:
            raise ValueError("Class not found")

        if class_group.teacher_id != teacher_id:
            raise ValueError("Only the teacher can delete this class")

        db.session.delete(class_group)
        db.session.commit()

    @staticmethod
    def join_class(student_id, invite_code):
        """Join a class using invite code."""
        # Find class by invite code
        class_group = ClassGroup.query.filter_by(invite_code=invite_code.upper()).first()
        if not class_group:
            raise ValueError("Invalid invite code")

        # Check if already a member
        existing = ClassMembership.query.filter_by(
            class_id=class_group.id,
            student_id=student_id
        ).first()

        if existing:
            raise ValueError("Already a member of this class")

        # Create membership
        membership = ClassMembership(
            class_id=class_group.id,
            student_id=student_id,
            role='student'
        )

        db.session.add(membership)
        db.session.commit()

        return class_group

    @staticmethod
    def leave_class(class_id, student_id):
        """Leave a class."""
        membership = ClassMembership.query.filter_by(
            class_id=class_id,
            student_id=student_id
        ).first()

        if not membership:
            raise ValueError("Not a member of this class")

        if membership.role == 'teacher':
            raise ValueError("Teachers cannot leave their own class")

        db.session.delete(membership)
        db.session.commit()

    @staticmethod
    def remove_member(class_id, student_id, teacher_id):
        """Remove a member from class (teacher only)."""
        class_group = ClassGroup.query.get(class_id)
        if not class_group:
            raise ValueError("Class not found")

        if class_group.teacher_id != teacher_id:
            raise ValueError("Only the teacher can remove members")

        membership = ClassMembership.query.filter_by(
            class_id=class_id,
            student_id=student_id
        ).first()

        if not membership:
            raise ValueError("Student is not a member")

        db.session.delete(membership)
        db.session.commit()

    @staticmethod
    def get_student_classes(student_id):
        """Get all classes a student is in."""
        memberships = ClassMembership.query.filter_by(student_id=student_id).all()

        classes = []
        for membership in memberships:
            class_group = ClassGroup.query.get(membership.class_id)
            if class_group:
                class_dict = class_group.to_dict()
                class_dict['role'] = membership.role
                class_dict['joined_at'] = membership.joined_at.isoformat()
                classes.append(class_dict)

        return classes

    @staticmethod
    def get_class_members(class_id):
        """Get all members of a class with their stats."""
        memberships = ClassMembership.query.filter_by(class_id=class_id).all()

        members = []
        for membership in memberships:
            student = Student.query.get(membership.student_id)
            if student:
                progress = StudentProgress.query.filter_by(student_id=student.id).first()

                name_parts = student.name.split(' ', 1)
                members.append({
                    'id': student.id,
                    'name': student.name,
                    'first_name': name_parts[0] if name_parts else student.name,
                    'last_name': name_parts[1] if len(name_parts) > 1 else '',
                    'grade': student.grade,
                    'avatar': student.avatar if hasattr(student, 'avatar') else '😊',
                    'level': progress.current_level if progress else 1,
                    'xp': progress.total_xp if progress else 0,
                    'role': membership.role,
                    'joined_at': membership.joined_at.isoformat()
                })

        return members

    @staticmethod
    def get_class_leaderboard(class_id):
        """Get class leaderboard sorted by XP."""
        members = ClassService.get_class_members(class_id)

        # Sort by XP descending
        members.sort(key=lambda x: x['xp'], reverse=True)

        # Add rank
        for i, member in enumerate(members, 1):
            member['rank'] = i

        return members

    @staticmethod
    def get_class_stats(class_id):
        """Get aggregate class statistics."""
        members = ClassService.get_class_members(class_id)

        if not members:
            return {
                'member_count': 0,
                'total_xp': 0,
                'average_xp': 0,
                'average_level': 0,
                'top_student': None
            }

        total_xp = sum(m['xp'] for m in members)
        average_xp = total_xp // len(members) if members else 0
        average_level = sum(m['level'] for m in members) // len(members) if members else 0

        # Get top student
        top_student = max(members, key=lambda x: x['xp']) if members else None

        return {
            'member_count': len(members),
            'total_xp': total_xp,
            'average_xp': average_xp,
            'average_level': average_level,
            'top_student': {
                'name': top_student['name'],
                'xp': top_student['xp'],
                'level': top_student['level']
            } if top_student else None
        }

