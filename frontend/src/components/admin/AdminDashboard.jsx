import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import LineChart from '../shared/LineChart';
import BarChart from '../shared/BarChart';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const { showNotification } = useNotification();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [growth, setGrowth] = useState(null);
  const [health, setHealth] = useState(null);
  const [activity, setActivity] = useState([]);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    loadDashboardData();
  }, [timeRange]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load all dashboard data in parallel
      const [metricsRes, growthRes, healthRes, activityRes] = await Promise.all([
        api.get('/api/admin/metrics'),
        api.get(`/api/admin/growth?days=${timeRange}`),
        api.get('/api/admin/health'),
        api.get('/api/admin/activity?limit=10')
      ]);

      if (metricsRes.data.success) {
        setMetrics(metricsRes.data.metrics);
      }

      if (growthRes.data.success) {
        setGrowth(growthRes.data.growth);
      }

      if (healthRes.data.success) {
        setHealth(healthRes.data.health);
      }

      if (activityRes.data.success) {
        setActivity(activityRes.data.activity || []);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
      showNotification('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getHealthStatus = (value, thresholds) => {
    if (value >= thresholds.good) return 'healthy';
    if (value >= thresholds.warning) return 'warning';
    return 'critical';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num?.toString() || '0';
  };

  const getActivityIcon = (type) => {
    const icons = {
      'user_created': '👤',
      'user_deleted': '🗑️',
      'user_updated': '✏️',
      'content_created': '📝',
      'content_updated': '📋',
      'settings_changed': '⚙️',
      'system_alert': '⚠️',
      'login': '🔐',
      'logout': '🚪'
    };
    return icons[type] || '📌';
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <div>
          <h2>Admin Dashboard</h2>
          <p className="subtitle">Platform overview and system health</p>
        </div>
        <div className="header-actions">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="time-range-select"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button className="btn-refresh" onClick={loadDashboardData}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Platform Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            👥
          </div>
          <div className="metric-info">
            <span className="metric-label">Total Users</span>
            <span className="metric-value">{formatNumber(metrics?.total_users)}</span>
            <span className="metric-change positive">
              +{metrics?.users_growth || 0}% this month
            </span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            🎓
          </div>
          <div className="metric-info">
            <span className="metric-label">Students</span>
            <span className="metric-value">{formatNumber(metrics?.total_students)}</span>
            <span className="metric-change positive">
              +{metrics?.students_growth || 0}% this month
            </span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            👨‍🏫
          </div>
          <div className="metric-info">
            <span className="metric-label">Teachers</span>
            <span className="metric-value">{formatNumber(metrics?.total_teachers)}</span>
            <span className="metric-change neutral">
              {metrics?.teachers_growth || 0}% this month
            </span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
            👨‍👩‍👧
          </div>
          <div className="metric-info">
            <span className="metric-label">Parents</span>
            <span className="metric-value">{formatNumber(metrics?.total_parents)}</span>
            <span className="metric-change positive">
              +{metrics?.parents_growth || 0}% this month
            </span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            📊
          </div>
          <div className="metric-info">
            <span className="metric-label">Assessments Taken</span>
            <span className="metric-value">{formatNumber(metrics?.total_assessments)}</span>
            <span className="metric-change positive">
              +{metrics?.assessments_growth || 0}% this month
            </span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)' }}>
            ⏱️
          </div>
          <div className="metric-info">
            <span className="metric-label">Learning Hours</span>
            <span className="metric-value">{formatNumber(metrics?.total_learning_hours)}</span>
            <span className="metric-change positive">
              +{metrics?.hours_growth || 0}% this month
            </span>
          </div>
        </div>
      </div>

      {/* User Growth Chart */}
      {growth && (
        <div className="dashboard-section">
          <h3>User Growth Trends</h3>
          <div className="chart-container">
            <LineChart
              data={growth.chart_data || []}
              xKey="date"
              lines={[
                { key: 'students', name: 'Students', color: '#667eea' },
                { key: 'teachers', name: 'Teachers', color: '#4facfe' },
                { key: 'parents', name: 'Parents', color: '#43e97b' }
              ]}
              height={300}
            />
          </div>
        </div>
      )}

      {/* System Health */}
      {health && (
        <div className="dashboard-section">
          <h3>System Health</h3>
          <div className="health-grid">
            <div className={`health-card ${getHealthStatus(health.database_performance, { good: 90, warning: 70 })}`}>
              <div className="health-header">
                <span className="health-icon">💾</span>
                <span className="health-label">Database</span>
              </div>
              <div className="health-value">{health.database_performance}%</div>
              <div className="health-status">
                {getHealthStatus(health.database_performance, { good: 90, warning: 70 }) === 'healthy' ? 'Optimal' : 'Needs Attention'}
              </div>
            </div>

            <div className={`health-card ${getHealthStatus(health.api_response_time < 200 ? 95 : health.api_response_time < 500 ? 75 : 50, { good: 90, warning: 70 })}`}>
              <div className="health-header">
                <span className="health-icon">⚡</span>
                <span className="health-label">API Response</span>
              </div>
              <div className="health-value">{health.api_response_time}ms</div>
              <div className="health-status">
                {health.api_response_time < 200 ? 'Excellent' : health.api_response_time < 500 ? 'Good' : 'Slow'}
              </div>
            </div>

            <div className={`health-card ${getHealthStatus(100 - health.error_rate, { good: 98, warning: 95 })}`}>
              <div className="health-header">
                <span className="health-icon">🎯</span>
                <span className="health-label">Success Rate</span>
              </div>
              <div className="health-value">{(100 - health.error_rate).toFixed(2)}%</div>
              <div className="health-status">
                {health.error_rate < 2 ? 'Excellent' : health.error_rate < 5 ? 'Good' : 'Poor'}
              </div>
            </div>

            <div className={`health-card ${getHealthStatus(health.active_sessions, { good: 10, warning: 5 })}`}>
              <div className="health-header">
                <span className="health-icon">👤</span>
                <span className="health-label">Active Sessions</span>
              </div>
              <div className="health-value">{health.active_sessions}</div>
              <div className="health-status">
                {health.active_sessions > 10 ? 'High Activity' : 'Normal'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="dashboard-section">
        <div className="section-header">
          <h3>Recent Activity</h3>
          <button className="btn-link" onClick={() => navigate('/admin/audit')}>
            View All →
          </button>
        </div>
        <div className="activity-list">
          {activity.length === 0 ? (
            <div className="empty-activity">No recent activity</div>
          ) : (
            activity.map((item, index) => (
              <div key={index} className="activity-item">
                <span className="activity-icon">{getActivityIcon(item.type)}</span>
                <div className="activity-info">
                  <span className="activity-description">{item.description}</span>
                  <span className="activity-meta">
                    {item.user_name} • {new Date(item.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-section">
        <h3>Quick Actions</h3>
        <div className="quick-actions">
          <button className="action-btn" onClick={() => navigate('/admin/users')}>
            <span className="action-icon">👥</span>
            <span className="action-label">Manage Users</span>
          </button>
          <button className="action-btn" onClick={() => navigate('/admin/content')}>
            <span className="action-icon">📚</span>
            <span className="action-label">Manage Content</span>
          </button>
          <button className="action-btn" onClick={() => navigate('/admin/settings')}>
            <span className="action-icon">⚙️</span>
            <span className="action-label">System Settings</span>
          </button>
          <button className="action-btn" onClick={() => navigate('/admin/audit')}>
            <span className="action-icon">📋</span>
            <span className="action-label">Audit Logs</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

