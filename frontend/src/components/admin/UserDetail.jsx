import React from 'react';
import './UserDetail.css';

const UserDetail = ({ user }) => {
  if (!user) return null;

  const getRoleBadgeClass = (role) => {
    const classes = {
      'student': 'role-badge-student',
      'teacher': 'role-badge-teacher',
      'parent': 'role-badge-parent',
      'admin': 'role-badge-admin'
    };
    return classes[role] || 'role-badge-default';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="user-detail">
      {/* Basic Information */}
      <div className="detail-section">
        <h3>Basic Information</h3>
        <div className="detail-grid">
          <div className="detail-item">
            <span className="detail-label">User ID</span>
            <span className="detail-value">{user.id}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Email</span>
            <span className="detail-value">{user.email}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Username</span>
            <span className="detail-value">{user.username || 'Not set'}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Role</span>
            <span className={`role-badge ${getRoleBadgeClass(user.role)}`}>
              {user.role}
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Status</span>
            <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Created At</span>
            <span className="detail-value">{formatDate(user.created_at)}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Last Updated</span>
            <span className="detail-value">{formatDate(user.updated_at)}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Last Login</span>
            <span className="detail-value">{formatDate(user.last_login)}</span>
          </div>
        </div>
      </div>

      {/* Role-specific Information */}
      {user.role === 'student' && user.student_profile && (
        <div className="detail-section">
          <h3>Student Profile</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Grade Level</span>
              <span className="detail-value">
                {user.student_profile.grade ? `${user.student_profile.grade}th Grade` : 'Not set'}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Current Level</span>
              <span className="detail-value">{user.student_profile.level || 1}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Total XP</span>
              <span className="detail-value">{user.student_profile.xp || 0}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Current Streak</span>
              <span className="detail-value">{user.student_profile.streak || 0} days</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Assessments Taken</span>
              <span className="detail-value">{user.student_profile.assessments_taken || 0}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Learning Hours</span>
              <span className="detail-value">
                {user.student_profile.learning_hours?.toFixed(1) || 0} hours
              </span>
            </div>
          </div>
        </div>
      )}

      {user.role === 'teacher' && user.teacher_profile && (
        <div className="detail-section">
          <h3>Teacher Profile</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Subject/Specialty</span>
              <span className="detail-value">{user.teacher_profile.subject || 'Not set'}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Total Classes</span>
              <span className="detail-value">{user.teacher_profile.total_classes || 0}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Total Students</span>
              <span className="detail-value">{user.teacher_profile.total_students || 0}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Assignments Created</span>
              <span className="detail-value">{user.teacher_profile.assignments_created || 0}</span>
            </div>
          </div>
        </div>
      )}

      {user.role === 'parent' && user.parent_profile && (
        <div className="detail-section">
          <h3>Parent Profile</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Phone Number</span>
              <span className="detail-value">{user.parent_profile.phone || 'Not set'}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Linked Children</span>
              <span className="detail-value">{user.parent_profile.linked_children || 0}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Email Notifications</span>
              <span className="detail-value">
                {user.parent_profile.email_notifications ? 'Enabled' : 'Disabled'}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">SMS Notifications</span>
              <span className="detail-value">
                {user.parent_profile.sms_notifications ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Activity Statistics */}
      {user.activity_stats && (
        <div className="detail-section">
          <h3>Activity Statistics</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Total Logins</span>
              <span className="detail-value">{user.activity_stats.total_logins || 0}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Last 7 Days</span>
              <span className="detail-value">{user.activity_stats.logins_last_7_days || 0} logins</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Last 30 Days</span>
              <span className="detail-value">{user.activity_stats.logins_last_30_days || 0} logins</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Average Session</span>
              <span className="detail-value">
                {user.activity_stats.avg_session_duration?.toFixed(1) || 0} minutes
              </span>
            </div>
          </div>
        </div>
      )}

      {/* System Information */}
      <div className="detail-section">
        <h3>System Information</h3>
        <div className="detail-grid">
          <div className="detail-item">
            <span className="detail-label">Account Age</span>
            <span className="detail-value">
              {user.created_at 
                ? Math.floor((Date.now() - new Date(user.created_at)) / (1000 * 60 * 60 * 24)) + ' days'
                : 'N/A'
              }
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Email Verified</span>
            <span className="detail-value">
              {user.email_verified ? '✅ Yes' : '❌ No'}
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Two-Factor Auth</span>
            <span className="detail-value">
              {user.two_factor_enabled ? '✅ Enabled' : '❌ Disabled'}
            </span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Password Last Changed</span>
            <span className="detail-value">{formatDate(user.password_changed_at)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDetail;

