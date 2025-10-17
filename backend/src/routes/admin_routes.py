"""
API routes for platform administration.
"""
from flask import Blueprint, request, jsonify
from src.services.admin_service import AdminService
from src.services.user_management_service import UserManagementService
from src.services.content_management_service import ContentManagementService
from src.services.settings_audit_service import SettingsService, AuditService

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ============================================================================
# Step 10.1: Admin Dashboard Routes
# ============================================================================

@admin_bp.route('/metrics', methods=['GET'])
def get_platform_metrics():
    """Get platform-wide metrics"""
    result, status = AdminService.get_platform_metrics()
    return jsonify(result), status


@admin_bp.route('/growth', methods=['GET'])
def get_user_growth():
    """Get user growth trends"""
    days = request.args.get('days', 30, type=int)
    result, status = AdminService.get_user_growth(days)
    return jsonify(result), status


@admin_bp.route('/health', methods=['GET'])
def get_system_health():
    """Get system health metrics"""
    result, status = AdminService.get_system_health()
    return jsonify(result), status


@admin_bp.route('/activity', methods=['GET'])
def get_recent_activity():
    """Get recent platform activity"""
    limit = request.args.get('limit', 20, type=int)
    result, status = AdminService.get_recent_activity(limit)
    return jsonify(result), status


# ============================================================================
# Step 10.2: User Management Routes
# ============================================================================

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    admin_id = data.get('admin_id', 1)  # In production, get from auth token
    result, status = UserManagementService.create_user(admin_id, data)
    return jsonify(result), status


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    data = request.json
    admin_id = data.get('admin_id', 1)  # In production, get from auth token
    result, status = UserManagementService.update_user(admin_id, user_id, data)
    return jsonify(result), status


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    admin_id = request.args.get('admin_id', 1, type=int)  # In production, get from auth token
    result, status = UserManagementService.delete_user(admin_id, user_id)
    return jsonify(result), status


@admin_bp.route('/users/search', methods=['GET'])
def search_users():
    """Search and filter users"""
    query = request.args.get('query')
    role = request.args.get('role')
    limit = request.args.get('limit', 50, type=int)
    result, status = UserManagementService.search_users(query, role, limit)
    return jsonify(result), status


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    """Get detailed user information"""
    result, status = UserManagementService.get_user_details(user_id)
    return jsonify(result), status


# ============================================================================
# Step 10.3: Content Management Routes
# ============================================================================

@admin_bp.route('/skills', methods=['POST'])
def create_skill():
    """Create a new skill"""
    data = request.json
    admin_id = data.get('admin_id', 1)  # In production, get from auth token
    result, status = ContentManagementService.create_skill(admin_id, data)
    return jsonify(result), status


@admin_bp.route('/skills/<int:skill_id>', methods=['PUT'])
def update_skill(skill_id):
    """Update skill information"""
    data = request.json
    admin_id = data.get('admin_id', 1)  # In production, get from auth token
    result, status = ContentManagementService.update_skill(admin_id, skill_id, data)
    return jsonify(result), status


@admin_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    """Delete a skill"""
    admin_id = request.args.get('admin_id', 1, type=int)  # In production, get from auth token
    result, status = ContentManagementService.delete_skill(admin_id, skill_id)
    return jsonify(result), status


@admin_bp.route('/skills', methods=['GET'])
def get_skills():
    """Get skills with optional filters"""
    subject_area = request.args.get('subject_area')
    grade_level = request.args.get('grade_level', type=int)
    limit = request.args.get('limit', 100, type=int)
    result, status = ContentManagementService.get_skills(subject_area, grade_level, limit)
    return jsonify(result), status


# ============================================================================
# Step 10.4: System Settings Routes
# ============================================================================

@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    category = request.args.get('category')
    result, status = SettingsService.get_settings(category)
    return jsonify(result), status


@admin_bp.route('/settings/<key>', methods=['GET'])
def get_setting(key):
    """Get a specific setting"""
    result, status = SettingsService.get_setting(key)
    return jsonify(result), status


@admin_bp.route('/settings/<key>', methods=['PUT'])
def update_setting(key):
    """Update or create a setting"""
    data = request.json
    admin_id = data.get('admin_id', 1)  # In production, get from auth token
    value = data.get('value')
    description = data.get('description')
    result, status = SettingsService.update_setting(admin_id, key, value, description)
    return jsonify(result), status


@admin_bp.route('/settings/<key>', methods=['DELETE'])
def delete_setting(key):
    """Delete a setting"""
    admin_id = request.args.get('admin_id', 1, type=int)  # In production, get from auth token
    result, status = SettingsService.delete_setting(admin_id, key)
    return jsonify(result), status


# ============================================================================
# Step 10.5: Audit Logging Routes
# ============================================================================

@admin_bp.route('/audit/logs', methods=['POST'])
def log_action():
    """Log an administrative action"""
    data = request.json
    result, status = AuditService.log_action(
        admin_id=data.get('admin_id', 1),
        action_type=data.get('action_type'),
        entity_type=data.get('entity_type'),
        entity_id=data.get('entity_id'),
        before_value=data.get('before_value'),
        after_value=data.get('after_value'),
        description=data.get('description'),
        ip_address=data.get('ip_address'),
        user_agent=data.get('user_agent')
    )
    return jsonify(result), status


@admin_bp.route('/audit/logs', methods=['GET'])
def get_logs():
    """Get audit logs with filters"""
    filters = {
        'action_type': request.args.get('action_type'),
        'entity_type': request.args.get('entity_type'),
        'admin_id': request.args.get('admin_id', type=int),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'limit': request.args.get('limit', 100, type=int)
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    result, status = AuditService.get_logs(**filters)
    return jsonify(result), status


@admin_bp.route('/audit/admin/<int:admin_id>', methods=['GET'])
def get_admin_activity(admin_id):
    """Get activity for a specific admin"""
    days = request.args.get('days', 30, type=int)
    result, status = AuditService.get_admin_activity(admin_id, days)
    return jsonify(result), status


@admin_bp.route('/audit/export', methods=['GET'])
def export_logs():
    """Export audit logs"""
    filters = {
        'action_type': request.args.get('action_type'),
        'entity_type': request.args.get('entity_type'),
        'admin_id': request.args.get('admin_id', type=int),
        'limit': request.args.get('limit', 1000, type=int)
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    format_type = request.args.get('format', 'json')
    result, status = AuditService.export_logs(filters, format_type)
    return jsonify(result), status

