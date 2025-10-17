import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { teacherAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import DataTable from '../shared/DataTable';
import BarChart from '../shared/BarChart';

const ClassDetail = () => {
  const { classId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('students');
  
  const { data: classData, loading, error } = useFetch(() => teacherAPI.getClassOverview(classId));

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading class details..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Failed to load class: {error}</p>
        <button 
          onClick={() => navigate('/teacher/classes')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Classes
        </button>
      </div>
    );
  }

  const {
    class_info = {},
    students = [],
    performance_metrics = {},
    skill_distribution = []
  } = classData || {};

  const studentColumns = [
    { key: 'name', label: 'Student Name', sortable: true },
    { 
      key: 'level', 
      label: 'Level', 
      sortable: true,
      render: (value) => <span className="font-semibold text-blue-600">{value}</span>
    },
    { 
      key: 'accuracy', 
      label: 'Accuracy', 
      sortable: true,
      render: (value) => `${Math.round(value * 100)}%`
    },
    { 
      key: 'questions_answered', 
      label: 'Questions', 
      sortable: true 
    },
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
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <button 
          onClick={() => navigate(`/teacher/students/${row.id}`)}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          View Details →
        </button>
      )
    }
  ];

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button 
            onClick={() => navigate('/teacher/classes')}
            className="text-gray-600 hover:text-gray-900 mb-2 flex items-center"
          >
            ← Back to Classes
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{class_info.name}</h1>
          <p className="text-gray-600 mt-1">
            {class_info.grade_level} • {class_info.student_count} students
          </p>
        </div>
        <div className="flex space-x-2">
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Edit Class
          </button>
          <button 
            onClick={() => navigate(`/teacher/assignments/new?class=${classId}`)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Create Assignment
          </button>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Average Accuracy</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {Math.round((performance_metrics.avg_accuracy || 0) * 100)}%
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Active Students</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {performance_metrics.active_students || 0}/{class_info.student_count}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Questions</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {(performance_metrics.total_questions || 0).toLocaleString()}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Struggling Students</div>
          <div className="text-2xl font-bold text-red-600 mt-1">
            {performance_metrics.struggling_students || 0}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <div className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('students')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'students'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Students ({students.length})
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'performance'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Performance
            </button>
            <button
              onClick={() => setActiveTab('assignments')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'assignments'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Assignments
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'students' && (
            <DataTable
              data={students}
              columns={studentColumns}
              searchable
              sortable
              pageSize={10}
            />
          )}

          {activeTab === 'performance' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold mb-4">Skill Distribution</h3>
                {skill_distribution && skill_distribution.length > 0 ? (
                  <BarChart
                    data={skill_distribution}
                    xKey="skill_name"
                    bars={[
                      { key: 'avg_accuracy', label: 'Average Accuracy', color: '#3b82f6' }
                    ]}
                    height={300}
                  />
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No performance data available
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'assignments' && (
            <div className="text-center py-12 text-gray-500">
              <p>Assignment management coming soon</p>
              <button 
                onClick={() => navigate(`/teacher/assignments/new?class=${classId}`)}
                className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Create First Assignment
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Invite Code */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="font-bold text-gray-900 mb-2">Class Invite Code</h3>
        <p className="text-sm text-gray-600 mb-3">
          Share this code with students to join your class
        </p>
        <div className="flex items-center space-x-3">
          <code className="flex-1 px-4 py-3 bg-white rounded-lg font-mono text-lg font-bold">
            {class_info.invite_code}
          </code>
          <button 
            onClick={() => {
              navigator.clipboard.writeText(class_info.invite_code);
              alert('Invite code copied to clipboard!');
            }}
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Copy Code
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClassDetail;

