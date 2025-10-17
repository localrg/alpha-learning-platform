import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './TeacherDashboard.css';

function TeacherDashboard({ onViewClass, onViewStudent }) {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('/api/teacher/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      if (data.success) {
        setDashboardData(data);
      } else {
        setError(data.error || 'Failed to load dashboard');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="teacher-dashboard">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="teacher-dashboard">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="teacher-dashboard">
        <div className="error">No dashboard data available</div>
      </div>
    );
  }

  const { teacher, stats, classes, alerts } = dashboardData;

  return (
    <div className="teacher-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="teacher-info">
          <span className="teacher-avatar">{teacher.avatar}</span>
          <div>
            <h1>Teacher Dashboard</h1>
            <p className="teacher-name">{teacher.name}</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_students}</div>
            <div className="stat-label">Total Students</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_classes}</div>
            <div className="stat-label">Classes</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{Math.round(stats.avg_class_performance * 100)}%</div>
            <div className="stat-label">Avg Performance</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_questions_answered.toLocaleString()}</div>
            <div className="stat-label">Questions Answered</div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {alerts && alerts.length > 0 && (
        <div className="alerts-section">
          <h2>📢 Alerts & Notifications</h2>
          <div className="alerts-list">
            {alerts.map((alert, index) => (
              <div key={index} className={`alert alert-${alert.severity}`}>
                <span className="alert-icon">
                  {alert.severity === 'high' ? '⚠️' : alert.severity === 'medium' ? '⚡' : 'ℹ️'}
                </span>
                <div className="alert-content">
                  <div className="alert-title">{alert.class_name}</div>
                  <div className="alert-message">{alert.message}</div>
                </div>
                {alert.class_id && (
                  <button 
                    className="btn-view-class"
                    onClick={() => onViewClass(alert.class_id)}
                  >
                    View Class
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Classes */}
      <div className="classes-section">
        <h2>📚 My Classes</h2>
        {classes && classes.length > 0 ? (
          <div className="classes-grid">
            {classes.map((classItem) => (
              <div key={classItem.id} className="class-card">
                <div className="class-header">
                  <h3>{classItem.name}</h3>
                  <span className="student-count">{classItem.student_count} students</span>
                </div>

                <div className="class-metrics">
                  <div className="metric">
                    <span className="metric-label">Avg Accuracy:</span>
                    <span className="metric-value">{Math.round(classItem.avg_accuracy * 100)}%</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Active:</span>
                    <span className="metric-value">{classItem.active_students}/{classItem.student_count}</span>
                  </div>
                  {classItem.struggling_students > 0 && (
                    <div className="metric warning">
                      <span className="metric-label">⚠️ Need Help:</span>
                      <span className="metric-value">{classItem.struggling_students}</span>
                    </div>
                  )}
                </div>

                <div className="class-actions">
                  <button 
                    className="btn-primary"
                    onClick={() => onViewClass(classItem.id)}
                  >
                    View Details
                  </button>
                  <button className="btn-secondary">
                    Create Assignment
                  </button>
                  <button className="btn-secondary">
                    Message Class
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-classes">
            <p>You don't have any classes yet.</p>
            <button className="btn-primary">Create Your First Class</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default TeacherDashboard;

