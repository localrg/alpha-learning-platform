import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { parentAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import DataTable from '../shared/DataTable';

const ChildProgress = () => {
  const { childId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('skills');
  const [skillFilter, setSkillFilter] = useState('all');

  const { data, loading, error } = useFetch(() => 
    parentAPI.getChildProgress(childId)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading progress..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Failed to load progress: {error}</p>
        <button 
          onClick={() => navigate('/parent/dashboard')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const { child, skills = [], assignments = [], achievements = [] } = data || {};

  const filteredSkills = skills.filter(skill => {
    if (skillFilter === 'all') return true;
    if (skillFilter === 'mastered') return skill.status === 'mastered';
    if (skillFilter === 'in_progress') return skill.status === 'in_progress';
    if (skillFilter === 'needs_practice') return skill.status === 'needs_practice';
    return true;
  });

  const skillColumns = [
    { 
      key: 'name', 
      label: 'Skill Name', 
      sortable: true 
    },
    { 
      key: 'status', 
      label: 'Status', 
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value === 'mastered' ? 'bg-green-100 text-green-700' :
          value === 'in_progress' ? 'bg-blue-100 text-blue-700' :
          'bg-yellow-100 text-yellow-700'
        }`}>
          {value?.replace('_', ' ')}
        </span>
      )
    },
    { 
      key: 'accuracy', 
      label: 'Accuracy', 
      sortable: true,
      render: (value) => `${value}%`
    },
    { 
      key: 'questions_answered', 
      label: 'Questions', 
      sortable: true 
    },
    { 
      key: 'last_practiced', 
      label: 'Last Practiced', 
      render: (value) => value ? new Date(value).toLocaleDateString() : 'Never'
    }
  ];

  const assignmentColumns = [
    { 
      key: 'title', 
      label: 'Assignment', 
      sortable: true 
    },
    { 
      key: 'status', 
      label: 'Status', 
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value === 'completed' ? 'bg-green-100 text-green-700' :
          value === 'in_progress' ? 'bg-blue-100 text-blue-700' :
          value === 'overdue' ? 'bg-red-100 text-red-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {value?.replace('_', ' ')}
        </span>
      )
    },
    { 
      key: 'score', 
      label: 'Score', 
      sortable: true,
      render: (value) => value !== null ? `${value}%` : 'N/A'
    },
    { 
      key: 'due_date', 
      label: 'Due Date', 
      render: (value) => value ? new Date(value).toLocaleDateString() : 'No due date'
    },
    { 
      key: 'submitted_at', 
      label: 'Submitted', 
      render: (value) => value ? new Date(value).toLocaleDateString() : 'Not submitted'
    }
  ];

  const achievementColumns = [
    { 
      key: 'name', 
      label: 'Achievement', 
      sortable: true,
      render: (value, row) => (
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{row.icon}</span>
          <span>{value}</span>
        </div>
      )
    },
    { 
      key: 'description', 
      label: 'Description' 
    },
    { 
      key: 'earned_at', 
      label: 'Earned', 
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString()
    },
    { 
      key: 'xp_reward', 
      label: 'XP Reward', 
      render: (value) => `+${value} XP`
    }
  ];

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
        <h1 className="text-3xl font-bold text-gray-900">{child?.name}'s Progress</h1>
        <p className="text-gray-600 mt-1">Detailed view of skills, assignments, and achievements</p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Skills</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{skills.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Skills Mastered</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {skills.filter(s => s.status === 'mastered').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Assignments</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {assignments.filter(a => a.status === 'completed').length}/{assignments.length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Achievements</div>
          <div className="text-2xl font-bold text-purple-600 mt-1">{achievements.length}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <div className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('skills')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'skills'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Skills ({skills.length})
            </button>
            <button
              onClick={() => setActiveTab('assignments')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'assignments'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Assignments ({assignments.length})
            </button>
            <button
              onClick={() => setActiveTab('achievements')}
              className={`py-4 border-b-2 font-medium text-sm ${
                activeTab === 'achievements'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Achievements ({achievements.length})
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'skills' && (
            <>
              {/* Skill Filter */}
              <div className="flex space-x-2 mb-4">
                <button
                  onClick={() => setSkillFilter('all')}
                  className={`px-3 py-1 rounded text-sm ${
                    skillFilter === 'all'
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All ({skills.length})
                </button>
                <button
                  onClick={() => setSkillFilter('mastered')}
                  className={`px-3 py-1 rounded text-sm ${
                    skillFilter === 'mastered'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Mastered ({skills.filter(s => s.status === 'mastered').length})
                </button>
                <button
                  onClick={() => setSkillFilter('in_progress')}
                  className={`px-3 py-1 rounded text-sm ${
                    skillFilter === 'in_progress'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  In Progress ({skills.filter(s => s.status === 'in_progress').length})
                </button>
                <button
                  onClick={() => setSkillFilter('needs_practice')}
                  className={`px-3 py-1 rounded text-sm ${
                    skillFilter === 'needs_practice'
                      ? 'bg-yellow-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Needs Practice ({skills.filter(s => s.status === 'needs_practice').length})
                </button>
              </div>

              <DataTable
                data={filteredSkills}
                columns={skillColumns}
                searchable
                sortable
                pageSize={10}
              />
            </>
          )}

          {activeTab === 'assignments' && (
            <DataTable
              data={assignments}
              columns={assignmentColumns}
              searchable
              sortable
              pageSize={10}
            />
          )}

          {activeTab === 'achievements' && (
            achievements.length > 0 ? (
              <DataTable
                data={achievements}
                columns={achievementColumns}
                searchable
                sortable
                pageSize={10}
              />
            ) : (
              <div className="text-center py-12 text-gray-500">
                <div className="text-6xl mb-4">🏆</div>
                <p>No achievements earned yet</p>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default ChildProgress;

