import React, { useState } from 'react';
import { useFetch, useMutation } from '../../hooks/useApi';
import { communicationAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import { useNotification } from '../../contexts/NotificationContext';

const ParentMessaging = () => {
  const { showNotification } = useNotification();
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messageText, setMessageText] = useState('');
  const [filterChild, setFilterChild] = useState('all');

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
    if (filterChild === 'all') return true;
    return conv.child_id === filterChild;
  }) || [];

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

  // Get unique children from conversations
  const children = conversations ? 
    Array.from(new Set(conversations.map(c => c.child_id)))
      .map(id => conversations.find(c => c.child_id === id))
      .map(c => ({ id: c.child_id, name: c.child_name }))
    : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading messages..." />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-120px)] flex bg-gray-50 p-6">
      <div className="flex-1 flex bg-white rounded-lg shadow overflow-hidden">
        {/* Conversations List */}
        <div className="w-80 border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Messages</h2>
            
            {/* Filter by Child */}
            {children.length > 1 && (
              <select
                value={filterChild}
                onChange={(e) => setFilterChild(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500"
              >
                <option value="all">All Children</option>
                {children.map(child => (
                  <option key={child.id} value={child.id}>{child.name}</option>
                ))}
              </select>
            )}
          </div>

          <div className="flex-1 overflow-y-auto">
            {filteredConversations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">💬</div>
                <p>No conversations yet</p>
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
                    <span className="text-2xl">👨‍🏫</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-gray-900 truncate">
                          {conv.teacher_name}
                        </h3>
                        {conv.unread_count > 0 && (
                          <span className="ml-2 px-2 py-1 bg-green-600 text-white rounded-full text-xs">
                            {conv.unread_count}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Re: {conv.child_name}
                      </p>
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
                  <span className="text-2xl">👨‍🏫</span>
                  <div>
                    <h3 className="font-bold text-gray-900">{selectedConversation.teacher_name}</h3>
                    <p className="text-sm text-gray-600">Regarding: {selectedConversation.child_name}</p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {loadingMessages ? (
                  <div className="flex items-center justify-center h-full">
                    <LoadingSpinner text="Loading messages..." />
                  </div>
                ) : messages && messages.length > 0 ? (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.is_parent ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-md px-4 py-2 rounded-lg ${
                          msg.is_parent
                            ? 'bg-green-600 text-white'
                            : 'bg-white text-gray-900 border border-gray-200'
                        }`}
                      >
                        <p className="text-sm">{msg.message}</p>
                        <p className={`text-xs mt-1 ${msg.is_parent ? 'text-green-100' : 'text-gray-500'}`}>
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
              <div className="text-center">
                <div className="text-6xl mb-4">💬</div>
                <p className="text-lg">Select a conversation to view messages</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ParentMessaging;

