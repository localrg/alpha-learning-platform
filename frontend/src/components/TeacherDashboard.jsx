import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useFetch } from '../hooks/useApi';
import { teacherAPI } from '../services/api';
import StatCard from './teacher/StatCard';
import LoadingSpinner from './shared/LoadingSpinner';
import LineChart from './shared/LineChart';
import BarChart from './shared/BarChart';

const TeacherDashboard = () => {
  const navigate = useNavigate();
  const { data: dashboardData, loading, error, refetch } = useFetch(teacherAPI.getDashboard);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Failed to load dashboard: {error}</p>
        <button 
          onClick={refetch}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const {
    total_students = 0,
    total_classes = 0,
    active_students = 0,
    pending_assignments = 0,
    alerts = [],
    recent_activity = [],
    class_performance = [],
    student_engagement = []
  } = dashboardData || {};

  // Calculate engagement rate
  const engagementRate = total_students > 0 
    ? Math.round((active_students / total_students) * 100) 
    : 0;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Teacher Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your classroom overview.</p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => navigate('/teacher/classes')}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            My Classes
          </button>
          <button 
            onClick={() => navigate('/teacher/assignments')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Create Assignment
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Students"
          value={total_students}
          subtitle="Across all classes"
          icon="👥"
          color="blue"
        />
        <StatCard
          title="Active Today"
          value={active_students}
          subtitle={`${engagementRate}% engagement`}
          icon="✓"
          color="green"
          trend={engagementRate >= 70 ? 5 : -5}
          trendLabel="vs last week"
        />
        <StatCard
          title="My Classes"
          value={total_classes}
          subtitle="Active classes"
          icon="🎓"
          color="purple"
        />
        <StatCard
          title="Pending Reviews"
          value={pending_assignments}
          subtitle="Assignments to grade"
          icon="📝"
          color={pending_assignments > 10 ? 'red' : 'yellow'}
        />
      </div>

      {/* Alerts */}
      {alerts && alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow border-l-4 border-l-red-500 p-6">
          <div className="mb-4">
            <h2 className="text-xl font-bold flex items-center">
              <span className="text-red-600 mr-2">⚠️</span>
              Student Alerts ({alerts.length})
            </h2>
            <p className="text-gray-600 text-sm mt-1">Students who need your attention</p>
          </div>
          <div className="space-y-3">
            {alerts.slice(0, 5).map((alert, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{alert.student_name}</p>
                  <p className="text-sm text-gray-600">{alert.message}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded ${
                    alert.priority === 'high' ? 'bg-red-100 text-red-700' :
                    alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {alert.priority}
                  </span>
                  <button 
                    onClick={() => navigate(`/teacher/monitoring?student=${alert.student_id}`)}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                  >
                    View
                  </button>
                </div>
              </div>
            ))}
            {alerts.length > 5 && (
              <button 
                onClick={() => navigate('/teacher/monitoring')}
                className="w-full text-center text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View all {alerts.length} alerts →
              </button>
            )}
          </div>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Class Performance */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4">
            <h2 className="text-xl font-bold">Class Performance</h2>
            <p className="text-gray-600 text-sm">Average accuracy by class</p>
          </div>
          {class_performance && class_performance.length > 0 ? (
            <BarChart
              data={class_performance}
              xKey="class_name"
              bars={[
                { key: 'avg_accuracy', label: 'Accuracy %', color: '#3b82f6' }
              ]}
              height={250}
            />
          ) : (
            <div className="text-center py-8 text-gray-500">
              No performance data available
            </div>
          )}
        </div>

        {/* Student Engagement */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4">
            <h2 className="text-xl font-bold">Student Engagement</h2>
            <p className="text-gray-600 text-sm">Last 7 days</p>
          </div>
          {student_engagement && student_engagement.length > 0 ? (
            <LineChart
              data={student_engagement}
              xKey="date"
              lines={[
                { key: 'active_students', label: 'Active Students', color: '#10b981' },
                { key: 'total_sessions', label: 'Total Sessions', color: '#3b82f6' }
              ]}
              height={250}
            />
          ) : (
            <div className="text-center py-8 text-gray-500">
              No engagement data available
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold">Recent Activity</h2>
          <p className="text-gray-600 text-sm">Latest student activity across your classes</p>
        </div>
        {recent_activity && recent_activity.length > 0 ? (
          <div className="space-y-3">
            {recent_activity.slice(0, 10).map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-semibold">
                      {activity.student_name?.charAt(0) || '?'}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{activity.student_name}</p>
                    <p className="text-sm text-gray-600">{activity.activity}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">{activity.class_name}</p>
                  <p className="text-xs text-gray-400">{activity.time_ago || activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No recent activity
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => navigate('/teacher/assignments')}
            className="h-20 flex flex-col items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <span className="text-2xl mb-1">📝</span>
            <span className="text-sm">Create Assignment</span>
          </button>
          <button 
            onClick={() => navigate('/teacher/monitoring')}
            className="h-20 flex flex-col items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <span className="text-2xl mb-1">👀</span>
            <span className="text-sm">Monitor Students</span>
          </button>
          <button 
            onClick={() => navigate('/teacher/analytics')}
            className="h-20 flex flex-col items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <span className="text-2xl mb-1">📊</span>
            <span className="text-sm">View Analytics</span>
          </button>
          <button 
            onClick={() => navigate('/teacher/messages')}
            className="h-20 flex flex-col items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <span className="text-2xl mb-1">💬</span>
            <span className="text-sm">Messages</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;

