import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { assignmentAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import DataTable from '../shared/DataTable';
import EmptyState from '../shared/EmptyState';

const AssignmentList = () => {
  const navigate = useNavigate();
  const [filterStatus, setFilterStatus] = useState('all');
  
  const { data: assignments, loading, error, refetch } = useFetch(assignmentAPI.getTeacherAssignments);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading assignments..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Failed to load assignments: {error}</p>
        <button 
          onClick={refetch}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!assignments || assignments.length === 0) {
    return (
      <div className="p-6">
        <EmptyState
          icon="📝"
          title="No Assignments Yet"
          description="Create your first assignment to get started with targeted practice for your students."
          actionLabel="Create Assignment"
          onAction={() => navigate('/teacher/assignments/new')}
        />
      </div>
    );
  }

  const filteredAssignments = filterStatus === 'all' 
    ? assignments 
    : assignments.filter(a => a.status === filterStatus);

  const columns = [
    { 
      key: 'title', 
      label: 'Assignment Title', 
      sortable: true,
      render: (value, row) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{row.class_name || 'Individual'}</div>
        </div>
      )
    },
    { 
      key: 'skills', 
      label: 'Skills', 
      render: (value) => (
        <div className="flex flex-wrap gap-1">
          {value?.slice(0, 3).map((skill, i) => (
            <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
              {skill}
            </span>
          ))}
          {value?.length > 3 && (
            <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
              +{value.length - 3}
            </span>
          )}
        </div>
      )
    },
    { 
      key: 'due_date', 
      label: 'Due Date', 
      sortable: true,
      render: (value) => {
        if (!value) return <span className="text-gray-400">No due date</span>;
        const date = new Date(value);
        const isOverdue = date < new Date();
        return (
          <span className={isOverdue ? 'text-red-600 font-medium' : 'text-gray-700'}>
            {date.toLocaleDateString()}
          </span>
        );
      }
    },
    { 
      key: 'completion_rate', 
      label: 'Completion', 
      sortable: true,
      render: (value, row) => (
        <div className="flex items-center space-x-2">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full" 
              style={{ width: `${value}%` }}
            />
          </div>
          <span className="text-sm text-gray-600 w-12">{value}%</span>
        </div>
      )
    },
    { 
      key: 'avg_score', 
      label: 'Avg Score', 
      sortable: true,
      render: (value) => value ? `${Math.round(value)}%` : 'N/A'
    },
    { 
      key: 'status', 
      label: 'Status', 
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value === 'active' ? 'bg-green-100 text-green-700' :
          value === 'completed' ? 'bg-blue-100 text-blue-700' :
          value === 'overdue' ? 'bg-red-100 text-red-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <button 
          onClick={() => navigate(`/teacher/assignments/${row.id}`)}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          View Details →
        </button>
      )
    }
  ];

  const statusCounts = {
    all: assignments.length,
    active: assignments.filter(a => a.status === 'active').length,
    completed: assignments.filter(a => a.status === 'completed').length,
    overdue: assignments.filter(a => a.status === 'overdue').length
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-1">Manage and track student assignments</p>
        </div>
        <button 
          onClick={() => navigate('/teacher/assignments/new')}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          + Create Assignment
        </button>
      </div>

      {/* Status Filter */}
      <div className="flex space-x-2">
        <button
          onClick={() => setFilterStatus('all')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'all'
              ? 'bg-gray-800 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({statusCounts.all})
        </button>
        <button
          onClick={() => setFilterStatus('active')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'active'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Active ({statusCounts.active})
        </button>
        <button
          onClick={() => setFilterStatus('completed')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'completed'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Completed ({statusCounts.completed})
        </button>
        <button
          onClick={() => setFilterStatus('overdue')}
          className={`px-4 py-2 rounded-lg ${
            filterStatus === 'overdue'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Overdue ({statusCounts.overdue})
        </button>
      </div>

      {/* Assignments Table */}
      <div className="bg-white rounded-lg shadow">
        <DataTable
          data={filteredAssignments}
          columns={columns}
          searchable
          sortable
          pageSize={10}
        />
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Assignments</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {assignments.length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Avg Completion</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {Math.round(assignments.reduce((acc, a) => acc + (a.completion_rate || 0), 0) / assignments.length)}%
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Avg Score</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {Math.round(assignments.reduce((acc, a) => acc + (a.avg_score || 0), 0) / assignments.length)}%
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Overdue</div>
          <div className="text-2xl font-bold text-red-600 mt-1">
            {statusCounts.overdue}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignmentList;

