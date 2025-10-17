import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { assignmentAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import DataTable from '../shared/DataTable';
import BarChart from '../shared/BarChart';

const AssignmentDetail = () => {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  
  const { data: assignment, loading, error } = useFetch(() => 
    assignmentAPI.getAssignmentDetail(assignmentId)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading assignment..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Failed to load assignment: {error}</p>
        <button 
          onClick={() => navigate('/teacher/assignments')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Assignments
        </button>
      </div>
    );
  }

  const {
    title,
    description,
    assignment_type,
    class_name,
    skills = [],
    question_count,
    difficulty,
    due_date,
    time_limit,
    students = [],
    completion_rate = 0,
    avg_score = 0,
    status
  } = assignment || {};

  const studentColumns = [
    { 
      key: 'name', 
      label: 'Student Name', 
      sortable: true 
    },
    { 
      key: 'status', 
      label: 'Status', 
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value === 'completed' ? 'bg-green-100 text-green-700' :
          value === 'in_progress' ? 'bg-blue-100 text-blue-700' :
          value === 'not_started' ? 'bg-gray-100 text-gray-700' :
          'bg-red-100 text-red-700'
        }`}>
          {value?.replace('_', ' ')}
        </span>
      )
    },
    { 
      key: 'progress', 
      label: 'Progress', 
      sortable: true,
      render: (value) => (
        <div className="flex items-center space-x-2">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full" 
              style={{ width: `${value}%` }}
            />
          </div>
          <span className="text-sm text-gray-600 w-12">{value}%</span>
        </div>
      )
    },
    { 
      key: 'score', 
      label: 'Score', 
      sortable: true,
      render: (value) => value !== null ? `${value}%` : 'N/A'
    },
    { 
      key: 'questions_correct', 
      label: 'Correct', 
      sortable: true,
      render: (value, row) => `${value || 0}/${row.questions_answered || 0}`
    },
    { 
      key: 'time_spent', 
      label: 'Time Spent', 
      render: (value) => value ? `${Math.round(value)} min` : 'N/A'
    },
    { 
      key: 'submitted_at', 
      label: 'Submitted', 
      render: (value) => value ? new Date(value).toLocaleDateString() : 'Not submitted'
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <button 
          onClick={() => navigate(`/teacher/students/${row.student_id}`)}
          className="text-blue-600 hover:text-blue-700 text-sm"
        >
          View Student
        </button>
      )
    }
  ];

  const isOverdue = due_date && new Date(due_date) < new Date();

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button 
            onClick={() => navigate('/teacher/assignments')}
            className="text-gray-600 hover:text-gray-900 mb-2 flex items-center"
          >
            ← Back to Assignments
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          <p className="text-gray-600 mt-1">
            {assignment_type === 'class' ? class_name : 'Individual Assignment'}
          </p>
        </div>
        <div className="flex space-x-2">
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Edit
          </button>
          <button className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
            Delete
          </button>
        </div>
      </div>

      {/* Assignment Info */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <div className="text-sm text-gray-600">Status</div>
            <div className="mt-1">
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                status === 'active' ? 'bg-green-100 text-green-700' :
                status === 'completed' ? 'bg-blue-100 text-blue-700' :
                status === 'overdue' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {status}
              </span>
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-600">Due Date</div>
            <div className={`mt-1 font-medium ${isOverdue ? 'text-red-600' : 'text-gray-900'}`}>
              {due_date ? new Date(due_date).toLocaleDateString() : 'No due date'}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-600">Questions</div>
            <div className="mt-1 font-medium text-gray-900">{question_count}</div>
          </div>

          <div>
            <div className="text-sm text-gray-600">Difficulty</div>
            <div className="mt-1 font-medium text-gray-900 capitalize">{difficulty}</div>
          </div>
        </div>

        {description && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">Description</div>
            <p className="mt-1 text-gray-900">{description}</p>
          </div>
        )}

        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600 mb-2">Skills</div>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, index) => (
              <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Students</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{students.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Completion Rate</div>
          <div className="text-2xl font-bold text-green-600 mt-1">{completion_rate}%</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Average Score</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">{Math.round(avg_score)}%</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Not Started</div>
          <div className="text-2xl font-bold text-red-600 mt-1">
            {students.filter(s => s.status === 'not_started').length}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <div className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Student Progress
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'analytics'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Analytics
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <DataTable
              data={students}
              columns={studentColumns}
              searchable
              sortable
              pageSize={10}
            />
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold mb-4">Score Distribution</h3>
                {students.filter(s => s.score !== null).length > 0 ? (
                  <BarChart
                    data={students.filter(s => s.score !== null).map(s => ({
                      name: s.name,
                      score: s.score
                    }))}
                    xKey="name"
                    bars={[
                      { key: 'score', label: 'Score %', color: '#3b82f6' }
                    ]}
                    height={300}
                  />
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No score data available yet
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AssignmentDetail;

