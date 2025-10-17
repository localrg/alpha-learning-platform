import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { parentAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import LineChart from '../shared/LineChart';
import BarChart from '../shared/BarChart';

const ParentDashboard = () => {
  const navigate = useNavigate();
  const [selectedChildId, setSelectedChildId] = useState(null);

  const { data: children, loading: loadingChildren } = useFetch(parentAPI.getChildren);
  
  const { data: childData, loading: loadingChild } = useFetch(
    () => selectedChildId ? parentAPI.getChildOverview(selectedChildId) : null,
    [selectedChildId]
  );

  // Auto-select first child when data loads
  React.useEffect(() => {
    if (children && children.length > 0 && !selectedChildId) {
      setSelectedChildId(children[0].id);
    }
  }, [children, selectedChildId]);

  if (loadingChildren) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading..." />
      </div>
    );
  }

  if (!children || children.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">👨‍👩‍👧</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Children Linked</h2>
        <p className="text-gray-600 mb-6">
          You haven't linked any children to your account yet.
        </p>
        <button
          onClick={() => navigate('/parent/link-child')}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Link a Child
        </button>
      </div>
    );
  }

  const selectedChild = children.find(c => c.id === selectedChildId);

  return (
    <div className="space-y-6 p-6">
      {/* Header with Child Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Parent Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor your child's learning progress</p>
        </div>
        
        {/* Child Selector */}
        <div className="flex items-center space-x-3">
          <label className="text-sm font-medium text-gray-700">Viewing:</label>
          <select
            value={selectedChildId || ''}
            onChange={(e) => setSelectedChildId(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            {children.map(child => (
              <option key={child.id} value={child.id}>
                {child.name} {child.grade && `(Grade ${child.grade})`}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loadingChild ? (
        <div className="flex items-center justify-center min-h-[300px]">
          <LoadingSpinner text="Loading child data..." />
        </div>
      ) : childData ? (
        <>
          {/* Child Overview Card */}
          <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">{selectedChild?.name}</h2>
                <p className="text-green-100 mt-1">
                  {selectedChild?.grade && `Grade ${selectedChild.grade} • `}
                  {childData.class_name || 'No class assigned'}
                </p>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold">Level {childData.level || 1}</div>
                <div className="text-green-100">
                  {childData.total_xp || 0} XP
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 mt-6">
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-sm text-green-100">Current Streak</div>
                <div className="text-2xl font-bold mt-1">{childData.current_streak || 0} days</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-sm text-green-100">Accuracy</div>
                <div className="text-2xl font-bold mt-1">{childData.accuracy || 0}%</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-sm text-green-100">Skills Mastered</div>
                <div className="text-2xl font-bold mt-1">{childData.skills_mastered || 0}</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-sm text-green-100">Achievements</div>
                <div className="text-2xl font-bold mt-1">{childData.achievements_count || 0}</div>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">This Week</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                {childData.practice_time_week || 0} min
              </div>
              <div className="text-xs text-gray-500 mt-1">Practice time</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Questions Answered</div>
              <div className="text-2xl font-bold text-blue-600 mt-1">
                {childData.questions_answered_week || 0}
              </div>
              <div className="text-xs text-gray-500 mt-1">This week</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Assignments</div>
              <div className="text-2xl font-bold text-green-600 mt-1">
                {childData.assignments_completed || 0}/{childData.assignments_total || 0}
              </div>
              <div className="text-xs text-gray-500 mt-1">Completed</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600">Last Active</div>
              <div className="text-2xl font-bold text-purple-600 mt-1">
                {childData.last_active ? new Date(childData.last_active).toLocaleDateString() : 'N/A'}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {childData.last_active && `${Math.floor((new Date() - new Date(childData.last_active)) / 86400000)} days ago`}
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Progress Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Weekly Progress</h3>
              {childData.weekly_progress && childData.weekly_progress.length > 0 ? (
                <LineChart
                  data={childData.weekly_progress}
                  xKey="day"
                  lines={[
                    { key: 'questions', label: 'Questions Answered', color: '#3b82f6' },
                    { key: 'accuracy', label: 'Accuracy %', color: '#10b981' }
                  ]}
                  height={250}
                />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No activity data for this week
                </div>
              )}
            </div>

            {/* Skills Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Top Skills</h3>
              {childData.top_skills && childData.top_skills.length > 0 ? (
                <BarChart
                  data={childData.top_skills}
                  xKey="skill"
                  bars={[
                    { key: 'accuracy', label: 'Accuracy %', color: '#8b5cf6' }
                  ]}
                  height={250}
                />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No skill data available
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Activity</h3>
            {childData.recent_activity && childData.recent_activity.length > 0 ? (
              <div className="space-y-3">
                {childData.recent_activity.slice(0, 5).map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{activity.icon || '📚'}</span>
                      <div>
                        <div className="font-medium text-gray-900">{activity.description}</div>
                        <div className="text-sm text-gray-600">
                          {new Date(activity.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    {activity.xp_earned && (
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-sm font-medium">
                        +{activity.xp_earned} XP
                      </span>
                    )}
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate(`/parent/child/${selectedChildId}/progress`)}
              className="p-4 bg-blue-50 border-2 border-blue-200 rounded-lg hover:bg-blue-100 text-left"
            >
              <div className="text-2xl mb-2">📊</div>
              <div className="font-bold text-gray-900">View Detailed Progress</div>
              <div className="text-sm text-gray-600 mt-1">See skills, assignments, and achievements</div>
            </button>
            
            <button
              onClick={() => navigate(`/parent/child/${selectedChildId}/reports`)}
              className="p-4 bg-green-50 border-2 border-green-200 rounded-lg hover:bg-green-100 text-left"
            >
              <div className="text-2xl mb-2">📈</div>
              <div className="font-bold text-gray-900">Activity Reports</div>
              <div className="text-sm text-gray-600 mt-1">Weekly and monthly progress reports</div>
            </button>
            
            <button
              onClick={() => navigate(`/parent/child/${selectedChildId}/goals`)}
              className="p-4 bg-purple-50 border-2 border-purple-200 rounded-lg hover:bg-purple-100 text-left"
            >
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-bold text-gray-900">Goals & Targets</div>
              <div className="text-sm text-gray-600 mt-1">Set and track learning goals</div>
            </button>
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-gray-500">
          Select a child to view their progress
        </div>
      )}
    </div>
  );
};

export default ParentDashboard;

