"""
Assignment Service
Business logic for teacher-created assignments
"""
from src.database import db
from src.models.assignment_model import Assignment, AssignmentStudent
from src.models.class_group import ClassGroup, ClassMembership
from src.models.student import Student
from src.models.gamification import StudentProgress
from datetime import datetime, timedelta


class AssignmentService:
    """Service for managing assignments"""
    
    @staticmethod
    def create_assignment(teacher_id, data):
        """
        Create a new assignment
        
        Args:
            teacher_id: ID of teacher creating assignment
            data: Assignment data (title, description, class_id/student_ids, skill_ids, question_count, difficulty, due_date)
        
        Returns:
            (result_dict, status_code)
        """
        try:
            # Validate required fields
            if not data.get('title'):
                return {'error': 'Title is required'}, 400
            
            if not data.get('skill_ids') or not isinstance(data['skill_ids'], list):
                return {'error': 'At least one skill is required'}, 400
            
            question_count = data.get('question_count', 10)
            if question_count < 5 or question_count > 50:
                return {'error': 'Question count must be between 5 and 50'}, 400
            
            # Verify teacher owns class if class assignment
            class_id = data.get('class_id')
            student_ids = data.get('student_ids', [])
            
            if class_id:
                class_group = ClassGroup.query.get(class_id)
                if not class_group or class_group.teacher_id != teacher_id:
                    return {'error': 'Class not found or unauthorized'}, 403
                
                # Get all students in class
                memberships = ClassMembership.query.filter_by(class_id=class_id).all()
                student_ids = [m.student_id for m in memberships]
            
            if not student_ids:
                return {'error': 'No students to assign to'}, 400
            
            # Parse due date
            due_date = None
            if data.get('due_date'):
                try:
                    due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                    if due_date < datetime.utcnow():
                        return {'error': 'Due date must be in the future'}, 400
                except:
                    return {'error': 'Invalid due date format'}, 400
            
            # Create assignment
            assignment = Assignment(
                teacher_id=teacher_id,
                class_id=class_id,
                title=data['title'],
                description=data.get('description'),
                skill_ids=data['skill_ids'],
                question_count=question_count,
                difficulty=data.get('difficulty', 'adaptive'),
                due_date=due_date
            )
            db.session.add(assignment)
            db.session.flush()
            
            # Create AssignmentStudent records
            for student_id in student_ids:
                assignment_student = AssignmentStudent(
                    assignment_id=assignment.id,
                    student_id=student_id
                )
                db.session.add(assignment_student)
            
            db.session.commit()
            
            result = assignment.to_dict()
            result['student_count'] = len(student_ids)
            
            return {'success': True, 'assignment': result}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_assignment(assignment_id, user_id, role):
        """
        Get assignment details
        
        Args:
            assignment_id: Assignment ID
            user_id: User ID (teacher or student)
            role: User role ('teacher' or 'student')
        
        Returns:
            (result_dict, status_code)
        """
        try:
            assignment = Assignment.query.get(assignment_id)
            if not assignment:
                return {'error': 'Assignment not found'}, 404
            
            # Verify authorization
            if role == 'teacher':
                if assignment.teacher_id != user_id:
                    return {'error': 'Unauthorized'}, 403
            elif role == 'student':
                # Find student record
                from src.models.user import User
                user = User.query.get(user_id)
                if not user or not hasattr(user, 'student'):
                    return {'error': 'Student not found'}, 404
                
                student_id = user.student[0].id if user.student else None
                if not student_id:
                    return {'error': 'Student not found'}, 404
                
                assignment_student = AssignmentStudent.query.filter_by(
                    assignment_id=assignment_id,
                    student_id=student_id
                ).first()
                
                if not assignment_student:
                    return {'error': 'Not assigned to you'}, 403
            
            result = assignment.to_dict()
            
            # Add stats for teachers
            if role == 'teacher':
                stats = AssignmentService.get_assignment_stats(assignment_id, user_id)
                result['stats'] = stats
            
            return {'success': True, 'assignment': result}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_teacher_assignments(teacher_id, filters=None):
        """Get all assignments created by teacher"""
        try:
            query = Assignment.query.filter_by(teacher_id=teacher_id)
            
            # Apply filters
            if filters:
                if filters.get('class_id'):
                    query = query.filter_by(class_id=filters['class_id'])
                
                if filters.get('status'):
                    # Filter by completion status
                    pass  # TODO: Implement status filtering
            
            # Sort by due date (upcoming first) or creation date
            query = query.order_by(Assignment.due_date.asc().nullslast(), Assignment.created_at.desc())
            
            assignments = query.all()
            
            result = []
            for assignment in assignments:
                assignment_dict = assignment.to_dict()
                
                # Add completion stats
                total_students = len(assignment.student_assignments)
                completed_students = sum(1 for sa in assignment.student_assignments if sa.status == 'completed')
                
                assignment_dict['total_students'] = total_students
                assignment_dict['completed_students'] = completed_students
                assignment_dict['completion_rate'] = completed_students / total_students if total_students > 0 else 0
                
                # Calculate average accuracy
                completed = [sa for sa in assignment.student_assignments if sa.status == 'completed']
                avg_accuracy = sum(sa.accuracy for sa in completed) / len(completed) if completed else 0
                assignment_dict['avg_accuracy'] = round(avg_accuracy, 2)
                
                result.append(assignment_dict)
            
            return result
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_student_assignments(student_id, filters=None):
        """Get all assignments for student"""
        try:
            query = AssignmentStudent.query.filter_by(student_id=student_id)
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query = query.filter_by(status=filters['status'])
            
            # Sort by due date
            query = query.join(Assignment).order_by(Assignment.due_date.asc().nullslast())
            
            assignment_students = query.all()
            
            result = []
            for as_record in assignment_students:
                assignment = as_record.assignment
                assignment_dict = assignment.to_dict()
                
                # Add student progress
                assignment_dict['student_status'] = as_record.status
                assignment_dict['questions_answered'] = as_record.questions_answered
                assignment_dict['questions_correct'] = as_record.questions_correct
                assignment_dict['accuracy'] = round(as_record.accuracy, 2)
                assignment_dict['started_at'] = as_record.started_at.isoformat() if as_record.started_at else None
                assignment_dict['completed_at'] = as_record.completed_at.isoformat() if as_record.completed_at else None
                
                # Check if overdue
                if assignment.due_date and assignment.due_date < datetime.utcnow() and as_record.status != 'completed':
                    assignment_dict['is_overdue'] = True
                else:
                    assignment_dict['is_overdue'] = False
                
                result.append(assignment_dict)
            
            return result
            
        except Exception as e:
            return []
    
    @staticmethod
    def update_assignment(assignment_id, teacher_id, data):
        """Update assignment (limited after students start)"""
        try:
            assignment = Assignment.query.get(assignment_id)
            if not assignment:
                return {'error': 'Assignment not found'}, 404
            
            if assignment.teacher_id != teacher_id:
                return {'error': 'Unauthorized'}, 403
            
            # Check if any student has started
            started = any(sa.status != 'assigned' for sa in assignment.student_assignments)
            
            # Can always update title, description, due date
            if 'title' in data:
                assignment.title = data['title']
            if 'description' in data:
                assignment.description = data['description']
            if 'due_date' in data:
                try:
                    assignment.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except:
                    return {'error': 'Invalid due date format'}, 400
            
            # Cannot update skills, questions, difficulty after students start
            if started:
                if 'skill_ids' in data or 'question_count' in data or 'difficulty' in data:
                    return {'error': 'Cannot change assignment details after students have started'}, 400
            else:
                if 'skill_ids' in data:
                    assignment.skill_ids = data['skill_ids']
                if 'question_count' in data:
                    assignment.question_count = data['question_count']
                if 'difficulty' in data:
                    assignment.difficulty = data['difficulty']
            
            assignment.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'assignment': assignment.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def delete_assignment(assignment_id, teacher_id):
        """Delete assignment (cannot delete after students complete)"""
        try:
            assignment = Assignment.query.get(assignment_id)
            if not assignment:
                return {'error': 'Assignment not found'}, 404
            
            if assignment.teacher_id != teacher_id:
                return {'error': 'Unauthorized'}, 403
            
            # Check if any student has completed
            completed = any(sa.status == 'completed' for sa in assignment.student_assignments)
            if completed:
                return {'error': 'Cannot delete assignment after students have completed it'}, 400
            
            db.session.delete(assignment)
            db.session.commit()
            
            return {'success': True, 'message': 'Assignment deleted'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def start_assignment(assignment_id, student_id):
        """Student starts assignment"""
        try:
            assignment_student = AssignmentStudent.query.filter_by(
                assignment_id=assignment_id,
                student_id=student_id
            ).first()
            
            if not assignment_student:
                return {'error': 'Assignment not found'}, 404
            
            if assignment_student.status == 'completed':
                return {'error': 'Assignment already completed'}, 400
            
            # Mark as in_progress
            if assignment_student.status == 'assigned':
                assignment_student.status = 'in_progress'
                assignment_student.started_at = datetime.utcnow()
                db.session.commit()
            
            assignment = assignment_student.assignment
            
            return {
                'success': True,
                'assignment': assignment.to_dict(),
                'progress': assignment_student.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def complete_assignment(assignment_id, student_id):
        """Student completes assignment"""
        try:
            assignment_student = AssignmentStudent.query.filter_by(
                assignment_id=assignment_id,
                student_id=student_id
            ).first()
            
            if not assignment_student:
                return {'error': 'Assignment not found'}, 404
            
            if assignment_student.status == 'completed':
                return {'error': 'Assignment already completed'}, 400
            
            assignment = assignment_student.assignment
            
            # Verify all questions answered
            if assignment_student.questions_answered < assignment.question_count:
                return {'error': 'Not all questions answered'}, 400
            
            # Mark as completed
            assignment_student.status = 'completed'
            assignment_student.completed_at = datetime.utcnow()
            
            # Calculate final accuracy
            assignment_student.accuracy = assignment_student.questions_correct / assignment_student.questions_answered if assignment_student.questions_answered > 0 else 0
            
            # Award XP
            xp_earned = AssignmentService._calculate_xp(assignment, assignment_student)
            
            # Add XP to student
            progress = StudentProgress.query.filter_by(student_id=student_id).first()
            if progress:
                progress.total_xp += xp_earned
                # Level up logic would go here
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Assignment completed!',
                'accuracy': round(assignment_student.accuracy, 2),
                'xp_earned': xp_earned,
                'questions_correct': assignment_student.questions_correct,
                'questions_total': assignment_student.questions_answered
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_assignment_stats(assignment_id, teacher_id=None):
        """Get statistics for an assignment"""
        try:
            assignment = Assignment.query.get(assignment_id)
            if not assignment:
                return {}
            
            if teacher_id and assignment.teacher_id != teacher_id:
                return {}
            
            student_assignments = assignment.student_assignments
            total_students = len(student_assignments)
            
            if total_students == 0:
                return {
                    'total_students': 0,
                    'completed_students': 0,
                    'in_progress_students': 0,
                    'not_started_students': 0,
                    'completion_rate': 0,
                    'avg_accuracy': 0,
                    'avg_time': 0
                }
            
            completed = [sa for sa in student_assignments if sa.status == 'completed']
            in_progress = [sa for sa in student_assignments if sa.status == 'in_progress']
            not_started = [sa for sa in student_assignments if sa.status == 'assigned']
            
            avg_accuracy = sum(sa.accuracy for sa in completed) / len(completed) if completed else 0
            avg_time = sum(sa.time_spent for sa in completed) / len(completed) if completed else 0
            
            return {
                'total_students': total_students,
                'completed_students': len(completed),
                'in_progress_students': len(in_progress),
                'not_started_students': len(not_started),
                'completion_rate': len(completed) / total_students,
                'avg_accuracy': round(avg_accuracy, 2),
                'avg_time': round(avg_time, 0)
            }
            
        except Exception as e:
            return {}
    
    @staticmethod
    def get_student_assignment_progress(assignment_id, student_id):
        """Get student's progress on assignment"""
        try:
            assignment_student = AssignmentStudent.query.filter_by(
                assignment_id=assignment_id,
                student_id=student_id
            ).first()
            
            if not assignment_student:
                return {'error': 'Assignment not found'}, 404
            
            assignment = assignment_student.assignment
            
            return {
                'success': True,
                'progress': {
                    'status': assignment_student.status,
                    'questions_answered': assignment_student.questions_answered,
                    'questions_remaining': assignment.question_count - assignment_student.questions_answered,
                    'questions_total': assignment.question_count,
                    'accuracy': round(assignment_student.accuracy, 2),
                    'time_spent': assignment_student.time_spent
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    # Helper methods
    
    @staticmethod
    def _calculate_xp(assignment, assignment_student):
        """Calculate XP earned for assignment completion"""
        # Base XP: 10 per question
        base_xp = assignment.question_count * 10
        
        # Accuracy bonus
        accuracy = assignment_student.accuracy
        if accuracy >= 0.9:
            accuracy_bonus = base_xp * 0.5
        elif accuracy >= 0.8:
            accuracy_bonus = base_xp * 0.25
        elif accuracy >= 0.7:
            accuracy_bonus = base_xp * 0.1
        else:
            accuracy_bonus = 0
        
        # On-time bonus
        on_time_bonus = 0
        if assignment.due_date and assignment_student.completed_at:
            if assignment_student.completed_at <= assignment.due_date:
                on_time_bonus = base_xp * 0.2
        
        total_xp = int(base_xp + accuracy_bonus + on_time_bonus)
        return total_xp

