import React, { useState } from 'react';
import { useFetch, useMutation } from '../../hooks/useApi';
import { communicationAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import { useNotification } from '../../contexts/NotificationContext';

const TeacherMessaging = () => {
  const { showNotification } = useNotification();
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messageText, setMessageText] = useState('');
  const [filterType, setFilterType] = useState('all');

  const { data: conversations, loading, refetch } = useFetch(
    () => communicationAPI.getConversations()
  );

  const { data: messages, loading: loadingMessages } = useFetch(
    () => selectedConversation ? communicationAPI.getMessages(selectedConversation.id) : null,
    [selectedConversation]
  );

  const { mutate: sendMessage, loading: sending } = useMutation(
    (data) => communicationAPI.sendMessage(data),
    {
      onSuccess: () => {
        showNotification('Message sent successfully!', 'success');
        setMessageText('');
        refetch();
      },
      onError: (error) => {
        showNotification(`Failed to send message: ${error}`, 'error');
      }
    }
  );

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;

    sendMessage({
      conversation_id: selectedConversation.id,
      message: messageText,
      type: 'message'
    });
  };

  const filteredConversations = conversations?.filter(conv => {
    if (filterType === 'all') return true;
    return conv.type === filterType;
  }) || [];

  const getConversationIcon = (type) => {
    switch (type) {
      case 'parent': return '👨‍👩‍👧';
      case 'student': return '👤';
      default: return '💬';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading messages..." />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-120px)] flex bg-gray-50">
      {/* Conversations List */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-3">Messages</h2>
          
          {/* Filter Tabs */}
          <div className="flex space-x-2">
            <button
              onClick={() => setFilterType('all')}
              className={`px-3 py-1 rounded text-sm ${
                filterType === 'all'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType('parent')}
              className={`px-3 py-1 rounded text-sm ${
                filterType === 'parent'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Parents
            </button>
            <button
              onClick={() => setFilterType('student')}
              className={`px-3 py-1 rounded text-sm ${
                filterType === 'student'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Students
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No conversations yet
            </div>
          ) : (
            filteredConversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setSelectedConversation(conv)}
                className={`w-full p-4 border-b border-gray-200 text-left hover:bg-gray-50 transition-colors ${
                  selectedConversation?.id === conv.id ? 'bg-green-50' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{getConversationIcon(conv.type)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-gray-900 truncate">
                        {conv.name}
                      </h3>
                      {conv.unread_count > 0 && (
                        <span className="ml-2 px-2 py-1 bg-green-600 text-white rounded-full text-xs">
                          {conv.unread_count}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 truncate mt-1">
                      {conv.last_message}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatTime(conv.last_message_time)}
                    </p>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Conversation Header */}
            <div className="bg-white border-b border-gray-200 p-4">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getConversationIcon(selectedConversation.type)}</span>
                <div>
                  <h3 className="font-bold text-gray-900">{selectedConversation.name}</h3>
                  <p className="text-sm text-gray-600 capitalize">{selectedConversation.type}</p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {loadingMessages ? (
                <div className="flex items-center justify-center h-full">
                  <LoadingSpinner text="Loading messages..." />
                </div>
              ) : messages && messages.length > 0 ? (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.is_teacher ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-md px-4 py-2 rounded-lg ${
                        msg.is_teacher
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-200 text-gray-900'
                      }`}
                    >
                      <p className="text-sm">{msg.message}</p>
                      <p className={`text-xs mt-1 ${msg.is_teacher ? 'text-green-100' : 'text-gray-600'}`}>
                        {formatTime(msg.created_at)}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  No messages yet. Start the conversation!
                </div>
              )}
            </div>

            {/* Message Input */}
            <div className="bg-white border-t border-gray-200 p-4">
              <form onSubmit={handleSendMessage} className="flex space-x-2">
                <input
                  type="text"
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  disabled={sending}
                />
                <button
                  type="submit"
                  disabled={sending || !messageText.trim()}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {sending ? 'Sending...' : 'Send'}
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            Select a conversation to view messages
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherMessaging;

