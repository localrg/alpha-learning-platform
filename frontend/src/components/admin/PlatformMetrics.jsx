import React, { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import LineChart from '../shared/LineChart';
import BarChart from '../shared/BarChart';
import PieChart from '../shared/PieChart';
import AreaChart from '../shared/AreaChart';
import './PlatformMetrics.css';

const PlatformMetrics = () => {
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);
  const [metrics, setMetrics] = useState(null);
  const [userGrowth, setUserGrowth] = useState(null);
  const [engagementData, setEngagementData] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);

  useEffect(() => {
    loadMetrics();
  }, [timeRange]);

  const loadMetrics = async () => {
    try {
      setLoading(true);

      // Load all metrics in parallel
      const [metricsRes, growthRes] = await Promise.all([
        api.get('/api/admin/metrics'),
        api.get(`/api/admin/growth?days=${timeRange}`)
      ]);

      if (metricsRes.data.success) {
        setMetrics(metricsRes.data.metrics);
        
        // Generate engagement data
        setEngagementData({
          daily_active_users: metricsRes.data.metrics.daily_active_users || 0,
          weekly_active_users: metricsRes.data.metrics.weekly_active_users || 0,
          monthly_active_users: metricsRes.data.metrics.monthly_active_users || 0,
          avg_session_duration: metricsRes.data.metrics.avg_session_duration || 0
        });

        // Generate performance data
        setPerformanceData({
          avg_assessment_score: metricsRes.data.metrics.avg_assessment_score || 0,
          completion_rate: metricsRes.data.metrics.completion_rate || 0,
          mastery_rate: metricsRes.data.metrics.mastery_rate || 0
        });
      }

      if (growthRes.data.success) {
        setUserGrowth(growthRes.data.growth);
      }
    } catch (error) {
      console.error('Error loading metrics:', error);
      showNotification('Failed to load platform metrics', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    const data = {
      metrics,
      userGrowth,
      engagementData,
      performanceData,
      generatedAt: new Date().toISOString()
    };

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `platform-metrics-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } else if (format === 'csv') {
      const csvContent = [
        ['Metric', 'Value'],
        ['Total Users', metrics?.total_users || 0],
        ['Total Students', metrics?.total_students || 0],
        ['Total Teachers', metrics?.total_teachers || 0],
        ['Total Parents', metrics?.total_parents || 0],
        ['Daily Active Users', engagementData?.daily_active_users || 0],
        ['Weekly Active Users', engagementData?.weekly_active_users || 0],
        ['Monthly Active Users', engagementData?.monthly_active_users || 0],
        ['Avg Session Duration (min)', engagementData?.avg_session_duration || 0],
        ['Avg Assessment Score (%)', performanceData?.avg_assessment_score || 0],
        ['Completion Rate (%)', performanceData?.completion_rate || 0],
        ['Mastery Rate (%)', performanceData?.mastery_rate || 0]
      ].map(row => row.join(',')).join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `platform-metrics-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }

    showNotification(`Metrics exported as ${format.toUpperCase()}`, 'success');
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="platform-metrics">
      <div className="metrics-header">
        <div>
          <h2>Platform Metrics</h2>
          <p className="subtitle">Advanced analytics and performance insights</p>
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
            <option value={365}>Last year</option>
          </select>
          <div className="export-dropdown">
            <button className="btn-export">📤 Export</button>
            <div className="export-menu">
              <button onClick={() => handleExport('csv')}>Export as CSV</button>
              <button onClick={() => handleExport('json')}>Export as JSON</button>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="metrics-overview">
        <div className="metric-card-large">
          <div className="metric-header">
            <span className="metric-icon">👥</span>
            <span className="metric-title">Total Users</span>
          </div>
          <div className="metric-value-large">{metrics?.total_users?.toLocaleString() || 0}</div>
          <div className="metric-breakdown">
            <div className="breakdown-item">
              <span className="breakdown-label">Students</span>
              <span className="breakdown-value">{metrics?.total_students?.toLocaleString() || 0}</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Teachers</span>
              <span className="breakdown-value">{metrics?.total_teachers?.toLocaleString() || 0}</span>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Parents</span>
              <span className="breakdown-value">{metrics?.total_parents?.toLocaleString() || 0}</span>
            </div>
          </div>
        </div>

        <div className="metric-card-large">
          <div className="metric-header">
            <span className="metric-icon">📊</span>
            <span className="metric-title">Learning Activity</span>
          </div>
          <div className="metric-value-large">{metrics?.total_assessments?.toLocaleString() || 0}</div>
          <div className="metric-subtitle">Total Assessments</div>
          <div className="metric-secondary">
            {metrics?.total_learning_hours?.toLocaleString() || 0} learning hours
          </div>
        </div>

        <div className="metric-card-large">
          <div className="metric-header">
            <span className="metric-icon">🎯</span>
            <span className="metric-title">Performance</span>
          </div>
          <div className="metric-value-large">{performanceData?.avg_assessment_score?.toFixed(1) || 0}%</div>
          <div className="metric-subtitle">Avg Assessment Score</div>
          <div className="metric-secondary">
            {performanceData?.mastery_rate?.toFixed(1) || 0}% mastery rate
          </div>
        </div>
      </div>

      {/* User Growth Chart */}
      {userGrowth && (
        <div className="chart-section">
          <h3>User Growth Trends</h3>
          <div className="chart-container-large">
            <AreaChart
              data={userGrowth.chart_data || []}
              xKey="date"
              areas={[
                { key: 'students', name: 'Students', color: '#667eea' },
                { key: 'teachers', name: 'Teachers', color: '#4facfe' },
                { key: 'parents', name: 'Parents', color: '#43e97b' }
              ]}
              height={350}
            />
          </div>
        </div>
      )}

      {/* Engagement Metrics */}
      {engagementData && (
        <div className="chart-section">
          <h3>User Engagement</h3>
          <div className="engagement-grid">
            <div className="engagement-card">
              <div className="engagement-value">{engagementData.daily_active_users?.toLocaleString() || 0}</div>
              <div className="engagement-label">Daily Active Users</div>
              <div className="engagement-chart">
                <BarChart
                  data={[
                    { name: 'DAU', value: engagementData.daily_active_users || 0 }
                  ]}
                  xKey="name"
                  bars={[{ key: 'value', color: '#667eea' }]}
                  height={100}
                />
              </div>
            </div>

            <div className="engagement-card">
              <div className="engagement-value">{engagementData.weekly_active_users?.toLocaleString() || 0}</div>
              <div className="engagement-label">Weekly Active Users</div>
              <div className="engagement-chart">
                <BarChart
                  data={[
                    { name: 'WAU', value: engagementData.weekly_active_users || 0 }
                  ]}
                  xKey="name"
                  bars={[{ key: 'value', color: '#4facfe' }]}
                  height={100}
                />
              </div>
            </div>

            <div className="engagement-card">
              <div className="engagement-value">{engagementData.monthly_active_users?.toLocaleString() || 0}</div>
              <div className="engagement-label">Monthly Active Users</div>
              <div className="engagement-chart">
                <BarChart
                  data={[
                    { name: 'MAU', value: engagementData.monthly_active_users || 0 }
                  ]}
                  xKey="name"
                  bars={[{ key: 'value', color: '#43e97b' }]}
                  height={100}
                />
              </div>
            </div>

            <div className="engagement-card">
              <div className="engagement-value">{engagementData.avg_session_duration?.toFixed(1) || 0} min</div>
              <div className="engagement-label">Avg Session Duration</div>
              <div className="engagement-chart">
                <BarChart
                  data={[
                    { name: 'Duration', value: engagementData.avg_session_duration || 0 }
                  ]}
                  xKey="name"
                  bars={[{ key: 'value', color: '#fa709a' }]}
                  height={100}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Distribution */}
      {performanceData && (
        <div className="chart-section">
          <h3>Performance Distribution</h3>
          <div className="performance-grid">
            <div className="performance-chart">
              <h4>Completion Rates</h4>
              <PieChart
                data={[
                  { name: 'Completed', value: performanceData.completion_rate || 0 },
                  { name: 'Incomplete', value: 100 - (performanceData.completion_rate || 0) }
                ]}
                height={250}
              />
            </div>

            <div className="performance-chart">
              <h4>Mastery Rates</h4>
              <PieChart
                data={[
                  { name: 'Mastered', value: performanceData.mastery_rate || 0 },
                  { name: 'Not Mastered', value: 100 - (performanceData.mastery_rate || 0) }
                ]}
                height={250}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlatformMetrics;

