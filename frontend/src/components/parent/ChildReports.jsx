import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { parentAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import LineChart from '../shared/LineChart';
import BarChart from '../shared/BarChart';
import AreaChart from '../shared/AreaChart';

const ChildReports = () => {
  const { childId } = useParams();
  const navigate = useNavigate();
  const [reportType, setReportType] = useState('weekly');
  const [timeRange, setTimeRange] = useState('last_4_weeks');

  const { data, loading, error } = useFetch(() => 
    parentAPI.getChildReports(childId, { report_type: reportType, time_range: timeRange }),
    [childId, reportType, timeRange]
  );

  const handleExport = (format) => {
    // Trigger export download
    const exportData = {
      child_id: childId,
      report_type: reportType,
      time_range: timeRange,
      format
    };
    
    // Create download link
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `child-report-${reportType}-${Date.now()}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Generating report..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Failed to load report: {error}</p>
        <button 
          onClick={() => navigate('/parent/dashboard')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const { child, report_data, insights } = data || {};

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <button 
          onClick={() => navigate('/parent/dashboard')}
          className="text-gray-600 hover:text-gray-900 mb-4 flex items-center"
        >
          ← Back to Dashboard
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{child?.name}'s Activity Reports</h1>
            <p className="text-gray-600 mt-1">Detailed learning analytics and insights</p>
          </div>
          
          {/* Export Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => handleExport('json')}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
            >
              Export JSON
            </button>
            <button
              onClick={() => handleExport('csv')}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
            >
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-4">
          {/* Report Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
            >
              <option value="weekly">Weekly Progress</option>
              <option value="monthly">Monthly Summary</option>
              <option value="skill">Skill Performance</option>
              <option value="time">Time Analysis</option>
            </select>
          </div>

          {/* Time Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
            >
              <option value="last_4_weeks">Last 4 Weeks</option>
              <option value="last_3_months">Last 3 Months</option>
              <option value="last_6_months">Last 6 Months</option>
              <option value="current_year">Current Year</option>
            </select>
          </div>
        </div>
      </div>

      {report_data ? (
        <>
          {/* Key Insights */}
          {insights && insights.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-blue-900 mb-3">📊 Key Insights</h3>
              <div className="space-y-2">
                {insights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <p className="text-blue-800">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Report Content */}
          {reportType === 'weekly' && (
            <div className="space-y-6">
              {/* Weekly Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Avg Daily Practice</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">
                    {report_data.avg_daily_practice || 0} min
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Questions/Week</div>
                  <div className="text-2xl font-bold text-blue-600 mt-1">
                    {report_data.avg_questions_per_week || 0}
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Avg Accuracy</div>
                  <div className="text-2xl font-bold text-purple-600 mt-1">
                    {report_data.avg_accuracy || 0}%
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Consistency Score</div>
                  <div className="text-2xl font-bold text-orange-600 mt-1">
                    {report_data.consistency_score || 0}/10
                  </div>
                </div>
              </div>

              {/* Weekly Trend Chart */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Weekly Progress Trend</h3>
                {report_data.weekly_data && report_data.weekly_data.length > 0 ? (
                  <LineChart
                    data={report_data.weekly_data}
                    xKey="week"
                    lines={[
                      { key: 'practice_time', label: 'Practice Time (min)', color: '#10b981' },
                      { key: 'questions_answered', label: 'Questions Answered', color: '#3b82f6' },
                      { key: 'accuracy', label: 'Accuracy %', color: '#8b5cf6' }
                    ]}
                    height={300}
                  />
                ) : (
                  <div className="text-center py-8 text-gray-500">No data available</div>
                )}
              </div>
            </div>
          )}

          {reportType === 'monthly' && (
            <div className="space-y-6">
              {/* Monthly Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Total Practice Time</div>
                  <div className="text-2xl font-bold text-green-600 mt-1">
                    {Math.floor((report_data.total_practice_time || 0) / 60)}h {(report_data.total_practice_time || 0) % 60}m
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Skills Improved</div>
                  <div className="text-2xl font-bold text-blue-600 mt-1">
                    {report_data.skills_improved || 0}
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Achievements Earned</div>
                  <div className="text-2xl font-bold text-purple-600 mt-1">
                    {report_data.achievements_earned || 0}
                  </div>
                </div>
              </div>

              {/* Monthly Breakdown */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Monthly Breakdown</h3>
                {report_data.monthly_data && report_data.monthly_data.length > 0 ? (
                  <AreaChart
                    data={report_data.monthly_data}
                    xKey="month"
                    areas={[
                      { key: 'practice_time', label: 'Practice Time', color: '#10b981' },
                      { key: 'questions_answered', label: 'Questions', color: '#3b82f6' }
                    ]}
                    height={300}
                  />
                ) : (
                  <div className="text-center py-8 text-gray-500">No data available</div>
                )}
              </div>
            </div>
          )}

          {reportType === 'skill' && (
            <div className="space-y-6">
              {/* Skill Performance Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Top Skill</div>
                  <div className="text-lg font-bold text-green-600 mt-1">
                    {report_data.top_skill || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500">
                    {report_data.top_skill_accuracy || 0}% accuracy
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Needs Focus</div>
                  <div className="text-lg font-bold text-red-600 mt-1">
                    {report_data.weakest_skill || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500">
                    {report_data.weakest_skill_accuracy || 0}% accuracy
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Overall Progress</div>
                  <div className="text-2xl font-bold text-blue-600 mt-1">
                    {report_data.overall_progress || 0}%
                  </div>
                </div>
              </div>

              {/* Skill Performance Chart */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Skill Performance</h3>
                {report_data.skill_data && report_data.skill_data.length > 0 ? (
                  <BarChart
                    data={report_data.skill_data}
                    xKey="skill"
                    bars={[
                      { key: 'accuracy', label: 'Accuracy %', color: '#8b5cf6' },
                      { key: 'questions_answered', label: 'Questions Answered', color: '#10b981' }
                    ]}
                    height={400}
                  />
                ) : (
                  <div className="text-center py-8 text-gray-500">No skill data available</div>
                )}
              </div>
            </div>
          )}

          {reportType === 'time' && (
            <div className="space-y-6">
              {/* Time Analysis Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Best Time</div>
                  <div className="text-lg font-bold text-green-600 mt-1">
                    {report_data.best_time || 'N/A'}
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Peak Day</div>
                  <div className="text-lg font-bold text-blue-600 mt-1">
                    {report_data.peak_day || 'N/A'}
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Avg Session</div>
                  <div className="text-lg font-bold text-purple-600 mt-1">
                    {report_data.avg_session_length || 0} min
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-600">Consistency</div>
                  <div className="text-lg font-bold text-orange-600 mt-1">
                    {report_data.consistency_score || 0}/10
                  </div>
                </div>
              </div>

              {/* Time Pattern Chart */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Practice Time Patterns</h3>
                {report_data.time_data && report_data.time_data.length > 0 ? (
                  <BarChart
                    data={report_data.time_data}
                    xKey="time_period"
                    bars={[
                      { key: 'practice_time', label: 'Practice Time (min)', color: '#10b981' },
                      { key: 'accuracy', label: 'Accuracy %', color: '#f59e0b' }
                    ]}
                    height={300}
                  />
                ) : (
                  <div className="text-center py-8 text-gray-500">No time data available</div>
                )}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 text-gray-500">
          No report data available for the selected criteria
        </div>
      )}
    </div>
  );
};

export default ChildReports;
