import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Modal from '../shared/Modal';
import { useMutation } from '../../hooks/useApi';
import { teacherAPI } from '../../services/api';

const QuickActions = ({ studentId, studentName, classId }) => {
  const navigate = useNavigate();
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [showAssignmentModal, setShowAssignmentModal] = useState(false);
  const [message, setMessage] = useState('');
  
  const { mutate: sendMessage, loading: sendingMessage } = useMutation(
    (data) => teacherAPI.sendMessage(data),
    {
      onSuccess: () => {
        setShowMessageModal(false);
        setMessage('');
      },
      successMessage: 'Message sent successfully!'
    }
  );

  const handleSendMessage = () => {
    if (!message.trim()) return;
    
    sendMessage({
      student_id: studentId,
      message: message.trim(),
      type: 'direct'
    });
  };

  const handleCreateTargetedAssignment = () => {
    navigate(`/teacher/assignments/new?student=${studentId}`);
  };

  const handleScheduleMeeting = () => {
    // In real app, this would open a meeting scheduler
    alert(`Scheduling meeting with ${studentName}`);
  };

  const handleNotifyParent = () => {
    // In real app, this would send a parent notification
    alert(`Notifying parent of ${studentName}`);
  };

  const messageTemplates = [
    {
      title: 'Encouragement',
      message: `Hi ${studentName}, I noticed you're working hard! Keep up the great effort. Let me know if you need any help.`
    },
    {
      title: 'Check-in',
      message: `Hi ${studentName}, I haven't seen much activity from you lately. Is everything okay? I'm here to help if you need support.`
    },
    {
      title: 'Performance Concern',
      message: `Hi ${studentName}, I noticed you're struggling with some recent topics. Let's schedule some time to review together.`
    },
    {
      title: 'Assignment Reminder',
      message: `Hi ${studentName}, just a friendly reminder that your assignment is due soon. Let me know if you have any questions!`
    }
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900">Quick Actions</h3>
      
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => setShowMessageModal(true)}
          className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <span>💬</span>
          <span>Send Message</span>
        </button>

        <button
          onClick={handleCreateTargetedAssignment}
          className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          <span>📝</span>
          <span>Create Assignment</span>
        </button>

        <button
          onClick={handleScheduleMeeting}
          className="flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          <span>📅</span>
          <span>Schedule Meeting</span>
        </button>

        <button
          onClick={handleNotifyParent}
          className="flex items-center justify-center space-x-2 px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
        >
          <span>👨‍👩‍👧</span>
          <span>Notify Parent</span>
        </button>
      </div>

      {/* Message Modal */}
      <Modal
        isOpen={showMessageModal}
        onClose={() => setShowMessageModal(false)}
        title={`Send Message to ${studentName}`}
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message Templates
            </label>
            <div className="grid grid-cols-2 gap-2">
              {messageTemplates.map((template, index) => (
                <button
                  key={index}
                  onClick={() => setMessage(template.message)}
                  className="px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 text-left"
                >
                  {template.title}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Type your message here..."
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowMessageModal(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              disabled={sendingMessage}
            >
              Cancel
            </button>
            <button
              onClick={handleSendMessage}
              disabled={!message.trim() || sendingMessage}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sendingMessage ? 'Sending...' : 'Send Message'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default QuickActions;

