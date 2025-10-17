"""
Content Management Service for managing skills and questions.
"""
from src.database import db
from src.models.assessment import Skill
from src.models.admin_models import AuditLog
import json


class ContentManagementService:
    """Service for managing educational content"""
    
    @staticmethod
    def create_skill(admin_id, data):
        """Create a new skill"""
        try:
            # Validate required fields
            if not data.get('name') or not data.get('subject_area'):
                return {'success': False, 'error': 'Missing required fields'}, 400
            
            # Create skill
            skill = Skill(
                name=data['name'],
                subject_area=data['subject_area'],
                grade_level=data.get('grade_level', 1),
                description=data.get('description', '')
            )
            db.session.add(skill)
            db.session.flush()
            
            # Log action
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type='create',
                entity_type='skill',
                entity_id=skill.id,
                after_value=json.dumps({'name': skill.name, 'subject_area': skill.subject_area}),
                description=f'Created skill {skill.name}'
            )
            db.session.add(audit_log)
            
            db.session.commit()
            
            return {'success': True, 'skill_id': skill.id, 'message': 'Skill created successfully'}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def update_skill(admin_id, skill_id, data):
        """Update skill information"""
        try:
            skill = Skill.query.get(skill_id)
            if not skill:
                return {'success': False, 'error': 'Skill not found'}, 404
            
            # Store before value
            before_value = {
                'name': skill.name,
                'subject_area': skill.subject_area,
                'grade_level': skill.grade_level,
                'description': skill.description
            }
            
            # Update fields
            if 'name' in data:
                skill.name = data['name']
            if 'subject_area' in data:
                skill.subject_area = data['subject_area']
            if 'grade_level' in data:
                skill.grade_level = data['grade_level']
            if 'description' in data:
                skill.description = data['description']
            
            # Store after value
            after_value = {
                'name': skill.name,
                'subject_area': skill.subject_area,
                'grade_level': skill.grade_level,
                'description': skill.description
            }
            
            # Log action
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type='update',
                entity_type='skill',
                entity_id=skill.id,
                before_value=json.dumps(before_value),
                after_value=json.dumps(after_value),
                description=f'Updated skill {skill.name}'
            )
            db.session.add(audit_log)
            
            db.session.commit()
            
            return {'success': True, 'message': 'Skill updated successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def delete_skill(admin_id, skill_id):
        """Delete a skill"""
        try:
            skill = Skill.query.get(skill_id)
            if not skill:
                return {'success': False, 'error': 'Skill not found'}, 404
            
            # Store skill info for audit log
            skill_info = {
                'name': skill.name,
                'subject_area': skill.subject_area,
                'grade_level': skill.grade_level
            }
            
            # Log action before deletion
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type='delete',
                entity_type='skill',
                entity_id=skill.id,
                before_value=json.dumps(skill_info),
                description=f'Deleted skill {skill.name}'
            )
            db.session.add(audit_log)
            
            # Delete skill
            db.session.delete(skill)
            db.session.commit()
            
            return {'success': True, 'message': 'Skill deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_skills(subject_area=None, grade_level=None, limit=100):
        """Get skills with optional filters"""
        try:
            # Start with base query
            skills_query = Skill.query
            
            # Apply filters
            if subject_area:
                skills_query = skills_query.filter_by(subject_area=subject_area)
            
            if grade_level is not None:
                skills_query = skills_query.filter_by(grade_level=grade_level)
            
            # Limit results
            skills = skills_query.limit(limit).all()
            
            # Convert to dict
            skills_data = [
                {
                    'id': s.id,
                    'name': s.name,
                    'subject_area': s.subject_area,
                    'grade_level': s.grade_level,
                    'description': s.description
                }
                for s in skills
            ]
            
            return {'success': True, 'skills': skills_data, 'count': len(skills_data)}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

