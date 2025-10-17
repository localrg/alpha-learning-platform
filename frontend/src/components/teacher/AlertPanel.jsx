import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { teacherAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';

const AlertPanel = () => {
  const navigate = useNavigate();
  const [filterPriority, setFilterPriority] = useState('all');
  
  // Mock data for demonstration
  const alerts = [
    {
      id: 1,
      student_id: 123,
      student_name: 'Bob Smith',
      class_name: 'Math 101',
      type: 'performance',
      priority: 'high',
      message: 'Student accuracy dropped to 35% (below 50% threshold)',
      created_at: '2024-12-20T10:30:00Z',
      resolved: false
    },
    {
      id: 2,
      student_id: 124,
      student_name: 'Sarah Johnson',
      class_name: 'Math 102',
      type: 'inactivity',
      priority: 'medium',
      message: 'No activity for 3 days',
      created_at: '2024-12-20T09:15:00Z',
      resolved: false
    },
    {
      id: 3,
      student_id: 125,
      student_name: 'Mike Davis',
      class_name: 'Math 101',
      type: 'assignment',
      priority: 'medium',
      message: 'Assignment "Algebra Practice" overdue by 2 days',
      created_at: '2024-12-20T08:00:00Z',
      resolved: false
    },
    {
      id: 4,
      student_id: 126,
      student_name: 'Lisa Wilson',
      class_name: 'Math 103',
      type: 'streak',
      priority: 'low',
      message: 'Lost 7-day practice streak',
      created_at: '2024-12-19T16:45:00Z',
      resolved: true
    }
  ];

  const filteredAlerts = filterPriority === 'all' 
    ? alerts 
    : alerts.filter(alert => alert.priority === filterPriority);

  const unresolvedAlerts = alerts.filter(alert => !alert.resolved);

  const handleResolveAlert = (alertId) => {
    // In real app, this would call an API
    console.log('Resolving alert:', alertId);
  };

  const handleViewStudent = (studentId) => {
    navigate(`/teacher/students/${studentId}`);
  };

  const handleCreateIntervention = (studentId) => {
    navigate(`/teacher/interventions?student=${studentId}`);
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'performance': return '📉';
      case 'inactivity': return '😴';
      case 'assignment': return '📝';
      case 'streak': return '🔥';
      default: return '⚠️';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-red-500 bg-red-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Student Alerts</h1>
          <p className="text-gray-600 mt-1">
            {unresolvedAlerts.length} unresolved alerts requiring attention
          </p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => navigate('/teacher/monitoring')}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Monitor Students
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
            Mark All Read
          </button>
        </div>
      </div>

      {/* Priority Filter */}
      <div className="flex space-x-2">
        <button
          onClick={() => setFilterPriority('all')}
          className={`px-4 py-2 rounded-lg ${
            filterPriority === 'all'
              ? 'bg-gray-800 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({alerts.length})
        </button>
        <button
          onClick={() => setFilterPriority('high')}
          className={`px-4 py-2 rounded-lg ${
            filterPriority === 'high'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          High ({alerts.filter(a => a.priority === 'high').length})
        </button>
        <button
          onClick={() => setFilterPriority('medium')}
          className={`px-4 py-2 rounded-lg ${
            filterPriority === 'medium'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Medium ({alerts.filter(a => a.priority === 'medium').length})
        </button>
        <button
          onClick={() => setFilterPriority('low')}
          className={`px-4 py-2 rounded-lg ${
            filterPriority === 'low'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Low ({alerts.filter(a => a.priority === 'low').length})
        </button>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>No alerts for the selected priority level</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div 
              key={alert.id} 
              className={`border-l-4 rounded-lg p-4 ${getPriorityColor(alert.priority)} ${
                alert.resolved ? 'opacity-60' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <span className="text-2xl">{getAlertIcon(alert.type)}</span>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="font-semibold text-gray-900">{alert.student_name}</h3>
                      <span className="text-sm text-gray-500">•</span>
                      <span className="text-sm text-gray-500">{alert.class_name}</span>
                      <span className={`px-2 py-1 text-xs rounded font-medium ${
                        alert.priority === 'high' ? 'bg-red-100 text-red-700' :
                        alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {alert.priority}
                      </span>
                      {alert.resolved && (
                        <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-700">
                          Resolved
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-2">{alert.message}</p>
                    <div className="text-xs text-gray-500">
                      {formatTimeAgo(alert.created_at)}
                    </div>
                  </div>
                </div>

                {!alert.resolved && (
                  <div className="flex items-center space-x-2 ml-4">
                    <button 
                      onClick={() => handleViewStudent(alert.student_id)}
                      className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-white"
                    >
                      View Student
                    </button>
                    <button 
                      onClick={() => handleCreateIntervention(alert.student_id)}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Intervene
                    </button>
                    <button 
                      onClick={() => handleResolveAlert(alert.id)}
                      className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                    >
                      Resolve
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Alert Statistics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold mb-4">Alert Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {alerts.filter(a => a.priority === 'high' && !a.resolved).length}
            </div>
            <div className="text-sm text-gray-600">High Priority</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {alerts.filter(a => a.priority === 'medium' && !a.resolved).length}
            </div>
            <div className="text-sm text-gray-600">Medium Priority</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {alerts.filter(a => a.priority === 'low' && !a.resolved).length}
            </div>
            <div className="text-sm text-gray-600">Low Priority</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {alerts.filter(a => a.resolved).length}
            </div>
            <div className="text-sm text-gray-600">Resolved Today</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertPanel;
