import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useMutation } from '../../hooks/useApi';
import { interventionAPI } from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';
import Modal from '../shared/Modal';

const InterventionTools = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showNotification } = useNotification();
  
  const studentId = searchParams.get('student');
  const [selectedIntervention, setSelectedIntervention] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [interventionData, setInterventionData] = useState({
    type: '',
    notes: '',
    priority: 'medium'
  });

  const { mutate: createIntervention, loading } = useMutation(
    (data) => interventionAPI.createIntervention(data),
    {
      onSuccess: () => {
        showNotification('Intervention created successfully!', 'success');
        setShowConfirmModal(false);
        navigate('/teacher/monitoring');
      },
      onError: (error) => {
        showNotification(`Failed to create intervention: ${error}`, 'error');
      }
    }
  );

  const interventionTypes = [
    {
      id: 'message',
      title: 'Send Message',
      icon: '💬',
      description: 'Send a direct message to the student',
      color: 'blue',
      action: () => {
        setInterventionData({ ...interventionData, type: 'message' });
        setSelectedIntervention('message');
        setShowConfirmModal(true);
      }
    },
    {
      id: 'assignment',
      title: 'Create Targeted Assignment',
      icon: '📝',
      description: 'Create a custom assignment based on weak areas',
      color: 'green',
      action: () => {
        navigate(`/teacher/assignments/new?student=${studentId}`);
      }
    },
    {
      id: 'meeting',
      title: 'Schedule Meeting',
      icon: '📅',
      description: 'Schedule a 1-on-1 meeting with the student',
      color: 'purple',
      action: () => {
        setInterventionData({ ...interventionData, type: 'meeting' });
        setSelectedIntervention('meeting');
        setShowConfirmModal(true);
      }
    },
    {
      id: 'parent',
      title: 'Notify Parent',
      icon: '👨‍👩‍👧',
      description: 'Send a notification to the student\'s parent',
      color: 'orange',
      action: () => {
        setInterventionData({ ...interventionData, type: 'parent_notification' });
        setSelectedIntervention('parent');
        setShowConfirmModal(true);
      }
    },
    {
      id: 'resources',
      title: 'Recommend Resources',
      icon: '📚',
      description: 'Share helpful learning resources',
      color: 'indigo',
      action: () => {
        setInterventionData({ ...interventionData, type: 'resources' });
        setSelectedIntervention('resources');
        setShowConfirmModal(true);
      }
    },
    {
      id: 'peer_support',
      title: 'Peer Support',
      icon: '🤝',
      description: 'Connect with a peer tutor or study buddy',
      color: 'pink',
      action: () => {
        setInterventionData({ ...interventionData, type: 'peer_support' });
        setSelectedIntervention('peer_support');
        setShowConfirmModal(true);
      }
    }
  ];

  const handleConfirmIntervention = () => {
    if (!interventionData.notes.trim()) {
      showNotification('Please add notes for this intervention', 'error');
      return;
    }

    createIntervention({
      student_id: studentId,
      ...interventionData
    });
  };

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-700 border-blue-300 hover:bg-blue-200',
      green: 'bg-green-100 text-green-700 border-green-300 hover:bg-green-200',
      purple: 'bg-purple-100 text-purple-700 border-purple-300 hover:bg-purple-200',
      orange: 'bg-orange-100 text-orange-700 border-orange-300 hover:bg-orange-200',
      indigo: 'bg-indigo-100 text-indigo-700 border-indigo-300 hover:bg-indigo-200',
      pink: 'bg-pink-100 text-pink-700 border-pink-300 hover:bg-pink-200'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <button 
          onClick={() => navigate('/teacher/monitoring')}
          className="text-gray-600 hover:text-gray-900 mb-4 flex items-center"
        >
          ← Back to Monitoring
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Intervention Tools</h1>
        <p className="text-gray-600 mt-1">
          Choose an intervention strategy to help the student
          {studentId && ` (Student ID: ${studentId})`}
        </p>
      </div>

      {/* Intervention Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {interventionTypes.map((intervention) => (
          <button
            key={intervention.id}
            onClick={intervention.action}
            className={`p-6 border-2 rounded-lg text-left transition-all ${getColorClasses(intervention.color)}`}
          >
            <div className="text-4xl mb-3">{intervention.icon}</div>
            <h3 className="text-lg font-bold mb-2">{intervention.title}</h3>
            <p className="text-sm opacity-90">{intervention.description}</p>
          </button>
        ))}
      </div>

      {/* Recent Interventions */}
      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Interventions</h2>
        <div className="space-y-3">
          {/* Mock data - would come from API */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">💬</span>
              <div>
                <div className="font-medium text-gray-900">Message sent to student</div>
                <div className="text-sm text-gray-600">2 days ago • Priority: Medium</div>
              </div>
            </div>
            <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
              Completed
            </span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📝</span>
              <div>
                <div className="font-medium text-gray-900">Targeted assignment created</div>
                <div className="text-sm text-gray-600">5 days ago • Priority: High</div>
              </div>
            </div>
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
              In Progress
            </span>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title={`Confirm ${interventionTypes.find(i => i.id === selectedIntervention)?.title}`}
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority Level
            </label>
            <select
              value={interventionData.priority}
              onChange={(e) => setInterventionData({ ...interventionData, priority: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes / Details *
            </label>
            <textarea
              value={interventionData.notes}
              onChange={(e) => setInterventionData({ ...interventionData, notes: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Add details about this intervention..."
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowConfirmModal(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmIntervention}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Confirm Intervention'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default InterventionTools;

