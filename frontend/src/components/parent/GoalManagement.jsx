import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFetch, useMutation } from '../../hooks/useApi';
import { goalAPI, parentAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import Modal from '../shared/Modal';
import { useNotification } from '../../contexts/NotificationContext';

const GoalManagement = () => {
  const { childId } = useParams();
  const navigate = useNavigate();
  const { showNotification } = useNotification();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [filterStatus, setFilterStatus] = useState('active');

  const [goalForm, setGoalForm] = useState({
    type: 'skill',
    target_value: '',
    deadline: '',
    notes: ''
  });

  const { data: child } = useFetch(() => parentAPI.getChildOverview(childId));
  const { data: goals, loading, refetch } = useFetch(() => goalAPI.getGoals(childId));

  const { mutate: createGoal, loading: creating } = useMutation(
    (data) => goalAPI.createGoal({ ...data, student_id: childId }),
    {
      onSuccess: () => {
        showNotification('Goal created successfully!', 'success');
        setShowCreateModal(false);
        setGoalForm({ type: 'skill', target_value: '', deadline: '', notes: '' });
        refetch();
      },
      onError: (error) => {
        showNotification(`Failed to create goal: ${error}`, 'error');
      }
    }
  );

  const { mutate: updateGoal } = useMutation(
    (data) => goalAPI.updateGoal(data.id, data),
    {
      onSuccess: () => {
        showNotification('Goal updated successfully!', 'success');
        refetch();
      }
    }
  );

  const handleCreateGoal = (e) => {
    e.preventDefault();
    createGoal(goalForm);
  };

  const handleAddNote = (goalId, note) => {
    if (!note.trim()) return;
    updateGoal({ id: goalId, notes: note });
  };

  const filteredGoals = goals?.filter(goal => {
    if (filterStatus === 'all') return true;
    if (filterStatus === 'active') return goal.status === 'in_progress';
    if (filterStatus === 'completed') return goal.status === 'completed';
    if (filterStatus === 'failed') return goal.status === 'failed';
    return true;
  }) || [];

  const getGoalIcon = (type) => {
    const icons = {
      skill: '🎯',
      time: '⏰',
      accuracy: '🎯',
      assignments: '📝',
      streak: '🔥',
      custom: '⭐'
    };
    return icons[type] || '🎯';
  };

  const getStatusColor = (status) => {
    const colors = {
      in_progress: 'bg-blue-100 text-blue-700',
      completed: 'bg-green-100 text-green-700',
      failed: 'bg-red-100 text-red-700'
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const calculateProgress = (goal) => {
    if (!goal.current_value || !goal.target_value) return 0;
    return Math.min(Math.round((goal.current_value / goal.target_value) * 100), 100);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading goals..." />
      </div>
    );
  }

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
            <h1 className="text-3xl font-bold text-gray-900">{child?.name}'s Goals</h1>
            <p className="text-gray-600 mt-1">Set and track learning goals</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            + Create Goal
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-2">
        <button
          onClick={() => setFilterStatus('active')}
          className={`px-4 py-2 rounded text-sm font-medium ${
            filterStatus === 'active'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Active ({goals?.filter(g => g.status === 'in_progress').length || 0})
        </button>
        <button
          onClick={() => setFilterStatus('completed')}
          className={`px-4 py-2 rounded text-sm font-medium ${
            filterStatus === 'completed'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Completed ({goals?.filter(g => g.status === 'completed').length || 0})
        </button>
        <button
          onClick={() => setFilterStatus('failed')}
          className={`px-4 py-2 rounded text-sm font-medium ${
            filterStatus === 'failed'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Failed ({goals?.filter(g => g.status === 'failed').length || 0})
        </button>
        <button
          onClick={() => setFilterStatus('all')}
          className={`px-4 py-2 rounded text-sm font-medium ${
            filterStatus === 'all'
              ? 'bg-gray-800 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({goals?.length || 0})
        </button>
      </div>

      {/* Goals Grid */}
      {filteredGoals.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredGoals.map((goal) => {
            const progress = calculateProgress(goal);
            const daysLeft = goal.deadline ? 
              Math.ceil((new Date(goal.deadline) - new Date()) / 86400000) : null;

            return (
              <div key={goal.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-3xl">{getGoalIcon(goal.type)}</span>
                    <div>
                      <h3 className="font-bold text-gray-900 capitalize">
                        {goal.type.replace('_', ' ')} Goal
                      </h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(goal.status)}`}>
                        {goal.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                    <span>Progress</span>
                    <span className="font-medium">{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        progress === 100 ? 'bg-green-600' :
                        progress >= 75 ? 'bg-blue-600' :
                        progress >= 50 ? 'bg-yellow-600' :
                        'bg-red-600'
                      }`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current:</span>
                    <span className="font-medium">{goal.current_value || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Target:</span>
                    <span className="font-medium">{goal.target_value}</span>
                  </div>
                  {goal.deadline && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Deadline:</span>
                      <span className={`font-medium ${daysLeft < 7 ? 'text-red-600' : ''}`}>
                        {daysLeft > 0 ? `${daysLeft} days left` : 'Overdue'}
                      </span>
                    </div>
                  )}
                </div>

                {goal.notes && (
                  <div className="mt-4 p-3 bg-gray-50 rounded text-sm text-gray-700">
                    {goal.notes}
                  </div>
                )}

                <button
                  onClick={() => setSelectedGoal(goal)}
                  className="mt-4 w-full px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
                >
                  Add Note
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="text-6xl mb-4">🎯</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No {filterStatus} goals</h3>
          <p className="text-gray-600 mb-6">
            {filterStatus === 'active' ? 'Create a goal to start tracking progress' : `No ${filterStatus} goals found`}
          </p>
          {filterStatus === 'active' && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Create Your First Goal
            </button>
          )}
        </div>
      )}

      {/* Create Goal Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Goal"
      >
        <form onSubmit={handleCreateGoal} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Goal Type</label>
            <select
              value={goalForm.type}
              onChange={(e) => setGoalForm({ ...goalForm, type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
              required
            >
              <option value="skill">Master a Skill</option>
              <option value="time">Practice Time</option>
              <option value="accuracy">Accuracy Target</option>
              <option value="assignments">Complete Assignments</option>
              <option value="streak">Maintain Streak</option>
              <option value="custom">Custom Goal</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Value</label>
            <input
              type="number"
              value={goalForm.target_value}
              onChange={(e) => setGoalForm({ ...goalForm, target_value: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
              placeholder="e.g., 5 skills, 100 minutes, 90%"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Deadline (Optional)</label>
            <input
              type="date"
              value={goalForm.deadline}
              onChange={(e) => setGoalForm({ ...goalForm, deadline: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
            <textarea
              value={goalForm.notes}
              onChange={(e) => setGoalForm({ ...goalForm, notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
              rows={3}
              placeholder="Add any notes or encouragement..."
            />
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {creating ? 'Creating...' : 'Create Goal'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Note Modal */}
      {selectedGoal && (
        <Modal
          isOpen={!!selectedGoal}
          onClose={() => setSelectedGoal(null)}
          title="Add Note to Goal"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const note = e.target.note.value;
              handleAddNote(selectedGoal.id, note);
              setSelectedGoal(null);
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Note</label>
              <textarea
                name="note"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
                rows={4}
                placeholder="Add encouragement or progress notes..."
                defaultValue={selectedGoal.notes || ''}
              />
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => setSelectedGoal(null)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Save Note
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};

export default GoalManagement;

