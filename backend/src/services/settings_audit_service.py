"""
Settings and Audit Services for platform configuration and logging.
"""
from src.database import db
from src.models.admin_models import SystemSetting, AuditLog
from datetime import datetime, timedelta
import json


class SettingsService:
    """Service for managing system settings"""
    
    @staticmethod
    def get_settings(category=None):
        """Get system settings"""
        try:
            # Start with base query
            settings_query = SystemSetting.query
            
            # Apply category filter
            if category:
                settings_query = settings_query.filter_by(category=category)
            
            settings = settings_query.all()
            
            # Convert to dict
            settings_data = [s.to_dict() for s in settings]
            
            return {'success': True, 'settings': settings_data}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_setting(key):
        """Get a specific setting by key"""
        try:
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                return {'success': False, 'error': 'Setting not found'}, 404
            
            return {'success': True, 'setting': setting.to_dict()}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def update_setting(admin_id, key, value, description=None):
        """Update or create a setting"""
        try:
            setting = SystemSetting.query.filter_by(key=key).first()
            
            if setting:
                # Update existing setting
                before_value = setting.value
                setting.value = value
                if description:
                    setting.description = description
                setting.updated_by = admin_id
                setting.updated_at = datetime.utcnow()
                
                # Log action
                audit_log = AuditLog(
                    admin_id=admin_id,
                    action_type='update',
                    entity_type='setting',
                    entity_id=setting.id,
                    before_value=before_value,
                    after_value=value,
                    description=f'Updated setting {key}'
                )
                db.session.add(audit_log)
                
                message = 'Setting updated successfully'
            else:
                # Create new setting
                # Extract category from key (e.g., 'general.platform_name' -> 'general')
                category = key.split('.')[0] if '.' in key else 'general'
                
                setting = SystemSetting(
                    category=category,
                    key=key,
                    value=value,
                    description=description,
                    updated_by=admin_id
                )
                db.session.add(setting)
                
                # Log action
                audit_log = AuditLog(
                    admin_id=admin_id,
                    action_type='create',
                    entity_type='setting',
                    after_value=value,
                    description=f'Created setting {key}'
                )
                db.session.add(audit_log)
                
                message = 'Setting created successfully'
            
            db.session.commit()
            
            return {'success': True, 'message': message}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def delete_setting(admin_id, key):
        """Delete a setting"""
        try:
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                return {'success': False, 'error': 'Setting not found'}, 404
            
            # Log action before deletion
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type='delete',
                entity_type='setting',
                entity_id=setting.id,
                before_value=setting.value,
                description=f'Deleted setting {key}'
            )
            db.session.add(audit_log)
            
            # Delete setting
            db.session.delete(setting)
            db.session.commit()
            
            return {'success': True, 'message': 'Setting deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500


class AuditService:
    """Service for audit logging and retrieval"""
    
    @staticmethod
    def log_action(admin_id, action_type, entity_type, entity_id=None, 
                   before_value=None, after_value=None, description=None,
                   ip_address=None, user_agent=None):
        """Log an administrative action"""
        try:
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                before_value=before_value,
                after_value=after_value,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return {'success': True, 'log_id': audit_log.id}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_logs(action_type=None, entity_type=None, admin_id=None, 
                 start_date=None, end_date=None, limit=100):
        """Get audit logs with filters"""
        try:
            # Start with base query
            logs_query = AuditLog.query
            
            # Apply filters
            if action_type:
                logs_query = logs_query.filter_by(action_type=action_type)
            
            if entity_type:
                logs_query = logs_query.filter_by(entity_type=entity_type)
            
            if admin_id:
                logs_query = logs_query.filter_by(admin_id=admin_id)
            
            if start_date:
                logs_query = logs_query.filter(AuditLog.created_at >= start_date)
            
            if end_date:
                logs_query = logs_query.filter(AuditLog.created_at <= end_date)
            
            # Order by most recent first and limit
            logs = logs_query.order_by(AuditLog.created_at.desc()).limit(limit).all()
            
            # Convert to dict
            logs_data = [log.to_dict() for log in logs]
            
            return {'success': True, 'logs': logs_data, 'count': len(logs_data)}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_admin_activity(admin_id, days=30):
        """Get activity for a specific admin"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            logs = AuditLog.query.filter(
                AuditLog.admin_id == admin_id,
                AuditLog.created_at >= start_date
            ).order_by(AuditLog.created_at.desc()).all()
            
            # Convert to dict
            logs_data = [log.to_dict() for log in logs]
            
            # Calculate statistics
            action_counts = {}
            for log in logs:
                action_counts[log.action_type] = action_counts.get(log.action_type, 0) + 1
            
            return {
                'success': True,
                'activity': {
                    'logs': logs_data,
                    'total_actions': len(logs),
                    'action_counts': action_counts,
                    'period_days': days
                }
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def export_logs(filters, format='json'):
        """Export audit logs"""
        try:
            # Get logs with filters
            result, status = AuditService.get_logs(**filters)
            
            if not result['success']:
                return result, status
            
            logs = result['logs']
            
            if format == 'csv':
                # Convert to CSV
                if not logs:
                    csv_data = 'No logs found'
                else:
                    # CSV header
                    headers = ['id', 'admin_name', 'action_type', 'entity_type', 'entity_id', 'description', 'created_at']
                    csv_data = ','.join(headers) + '\n'
                    
                    # CSV rows
                    for log in logs:
                        row = [
                            str(log.get('id', '')),
                            log.get('admin_name', ''),
                            log.get('action_type', ''),
                            log.get('entity_type', ''),
                            str(log.get('entity_id', '')),
                            log.get('description', ''),
                            log.get('created_at', '')
                        ]
                        csv_data += ','.join(row) + '\n'
                
                return {'success': True, 'data': csv_data, 'format': 'csv'}, 200
            else:
                # JSON format
                return {'success': True, 'data': logs, 'format': 'json'}, 200
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

