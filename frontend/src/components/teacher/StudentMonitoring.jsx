import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { teacherAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import DataTable from '../shared/DataTable';

const StudentMonitoring = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [filterStatus, setFilterStatus] = useState(searchParams.get('status') || 'all');
  
  const { data: monitoringData, loading, error, refetch } = useFetch(() => 
    teacherAPI.getDashboard() // This would be a dedicated monitoring endpoint
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading student data..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Failed to load monitoring data: {error}</p>
        <button 
          onClick={refetch}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  // Mock data for demonstration
  const students = [
    {
      id: 1,
      name: 'Alice Johnson',
      class: 'Math 101',
      status: 'on_track',
      current_activity: 'Practicing Algebra',
      session_duration: '15 min',
      questions_today: 12,
      accuracy_today: 0.85,
      last_active: '2 min ago'
    },
    {
      id: 2,
      name: 'Bob Smith',
      class: 'Math 101',
      status: 'needs_help',
      current_activity: 'Idle',
      session_duration: '5 min',
      questions_today: 3,
      accuracy_today: 0.45,
      last_active: '30 min ago'
    },
    {
      id: 3,
      name: 'Carol Davis',
      class: 'Math 102',
      status: 'needs_practice',
      current_activity: 'Reviewing Geometry',
      session_duration: '22 min',
      questions_today: 18,
      accuracy_today: 0.65,
      last_active: 'Active now'
    }
  ];

  const filteredStudents = filterStatus === 'all' 
    ? students 
    : students.filter(s => s.status === filterStatus);

  const columns = [
    { 
      key: 'name', 
      label: 'Student Name', 
      sortable: true,
      render: (value, row) => (
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${
            row.last_active === 'Active now' ? 'bg-green-500' : 'bg-gray-300'
          }`} />
          <span className="font-medium">{value}</span>
        </div>
      )
    },
    { key: 'class', label: 'Class', sortable: true },
    { 
      key: 'status', 
      label: 'Status', 
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value === 'on_track' ? 'bg-green-100 text-green-700' :
          value === 'needs_practice' ? 'bg-yellow-100 text-yellow-700' :
          value === 'needs_help' ? 'bg-red-100 text-red-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {value?.replace('_', ' ')}
        </span>
      )
    },
    { key: 'current_activity', label: 'Current Activity' },
    { key: 'session_duration', label: 'Session Time' },
    { 
      key: 'accuracy_today', 
      label: 'Accuracy Today', 
      sortable: true,
      render: (value) => (
        <span className={value < 0.6 ? 'text-red-600 font-semibold' : ''}>
          {Math.round(value * 100)}%
        </span>
      )
    },
    { key: 'questions_today', label: 'Questions', sortable: true },
    { key: 'last_active', label: 'Last Active' },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <div className="flex space-x-2">
          <button 
            onClick={() => navigate(`/teacher/students/${row.id}`)}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            View
          </button>
          <button 
            onClick={() => navigate(`/teacher/interventions?student=${row.id}`)}
            className="text-green-600 hover:text-green-700 text-sm"
          >
            Intervene
          </button>
        </div>
      )
    }
  ];

  const statusCounts = {
    all: students.length,
    on_track: students.filter(s => s.status === 'on_track').length,
    needs_practice: students.filter(s => s.status === 'needs_practice').length,
    needs_help: students.filter(s => s.status === 'needs_help').length,
    inactive: students.filter(s => s.status === 'inactive').length
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Student Monitoring</h1>
          <p className="text-gray-600 mt-1">Real-time view of student activity and progress</p>
        </div>
        <button 
          onClick={refetch}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Status Filter */}
      <div className="flex space-x-2">
        <button
          onClick={() => setFilterStatus('all')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({statusCounts.all})
        </button>
        <button
          onClick={() => setFilterStatus('on_track')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'on_track'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          On Track ({statusCounts.on_track})
        </button>
        <button
          onClick={() => setFilterStatus('needs_practice')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'needs_practice'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Needs Practice ({statusCounts.needs_practice})
        </button>
        <button
          onClick={() => setFilterStatus('needs_help')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'needs_help'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Needs Help ({statusCounts.needs_help})
        </button>
      </div>

      {/* Student Table */}
      <div className="bg-white rounded-lg shadow">
        <DataTable
          data={filteredStudents}
          columns={columns}
          searchable
          sortable
          pageSize={15}
        />
      </div>

      {/* Legend */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-2">Status Legend</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2" />
            <span className="font-medium">On Track:</span> Accuracy ≥ 70%, Active
          </div>
          <div>
            <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2" />
            <span className="font-medium">Needs Practice:</span> Accuracy 50-70%
          </div>
          <div>
            <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2" />
            <span className="font-medium">Needs Help:</span> Accuracy &lt; 50%
          </div>
          <div>
            <span className="inline-block w-3 h-3 bg-gray-300 rounded-full mr-2" />
            <span className="font-medium">Inactive:</span> No activity today
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentMonitoring;

