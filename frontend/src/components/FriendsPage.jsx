import React, { useState, useEffect } from 'react';
import './FriendsPage.css';

function FriendsPage() {
  const [activeTab, setActiveTab] = useState('friends');
  const [friends, setFriends] = useState([]);
  const [receivedRequests, setReceivedRequests] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFriends();
    loadRequests();
  }, []);

  const loadFriends = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/friends', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok) {
        setFriends(data.friends || []);
      }
    } catch (error) {
      console.error('Error loading friends:', error);
    }
  };

  const loadRequests = async () => {
    try {
      const token = localStorage.getItem('token');
      const [receivedRes, sentRes] = await Promise.all([
        fetch('/api/friends/requests/received', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/friends/requests/sent', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);
      
      const receivedData = await receivedRes.json();
      const sentData = await sentRes.json();
      
      if (receivedRes.ok) setReceivedRequests(receivedData.requests || []);
      if (sentRes.ok) setSentRequests(sentData.requests || []);
    } catch (error) {
      console.error('Error loading requests:', error);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/friends/search?q=${encodeURIComponent(query)}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok) {
        setSearchResults(data.students || []);
      }
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendRequest = async (studentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/friends/request/${studentId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        // Update search results to show request sent
        setSearchResults(searchResults.map(s => 
          s.id === studentId ? { ...s, friendship_status: 'request_sent' } : s
        ));
        loadRequests();
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to send request');
      }
    } catch (error) {
      console.error('Error sending request:', error);
    }
  };

  const acceptRequest = async (friendshipId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/friends/request/${friendshipId}/accept`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        loadFriends();
        loadRequests();
      }
    } catch (error) {
      console.error('Error accepting request:', error);
    }
  };

  const rejectRequest = async (friendshipId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/friends/request/${friendshipId}/reject`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        loadRequests();
      }
    } catch (error) {
      console.error('Error rejecting request:', error);
    }
  };

  const cancelRequest = async (friendshipId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/friends/request/${friendshipId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        loadRequests();
      }
    } catch (error) {
      console.error('Error cancelling request:', error);
    }
  };

  const removeFriend = async (friendId) => {
    if (!window.confirm('Are you sure you want to remove this friend?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/friends/${friendId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        loadFriends();
      }
    } catch (error) {
      console.error('Error removing friend:', error);
    }
  };

  return (
    <div className="friends-page">
      <div className="friends-header">
        <h1>👥 Friends</h1>
        <div className="friends-stats">
          <span>{friends.length} Friends</span>
          {receivedRequests.length > 0 && (
            <span className="request-badge">{receivedRequests.length} Requests</span>
          )}
        </div>
      </div>

      <div className="friends-tabs">
        <button 
          className={`tab ${activeTab === 'friends' ? 'active' : ''}`}
          onClick={() => setActiveTab('friends')}
        >
          Friends ({friends.length})
        </button>
        <button 
          className={`tab ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          Requests ({receivedRequests.length})
        </button>
        <button 
          className={`tab ${activeTab === 'find' ? 'active' : ''}`}
          onClick={() => setActiveTab('find')}
        >
          Find Friends
        </button>
      </div>

      <div className="friends-content">
        {activeTab === 'friends' && (
          <div className="friends-list">
            {friends.length === 0 ? (
              <div className="empty-state">
                <p>No friends yet. Start by finding and adding friends!</p>
                <button onClick={() => setActiveTab('find')}>Find Friends</button>
              </div>
            ) : (
              <div className="friend-grid">
                {friends.map(friend => (
                  <div key={friend.id} className="friend-card">
                    <div className="friend-avatar">{friend.avatar}</div>
                    <div className="friend-info">
                      <h3>{friend.first_name} {friend.last_name}</h3>
                      <p>Grade {friend.grade} • Level {friend.level}</p>
                      <p className="friend-xp">{friend.xp.toLocaleString()} XP</p>
                    </div>
                    <div className="friend-actions">
                      <button className="btn-remove" onClick={() => removeFriend(friend.id)}>
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'requests' && (
          <div className="requests-list">
            <h2>Received Requests</h2>
            {receivedRequests.length === 0 ? (
              <p className="empty-message">No pending requests</p>
            ) : (
              <div className="request-grid">
                {receivedRequests.map(request => (
                  <div key={request.id} className="request-card">
                    <div className="request-avatar">{request.requester.avatar}</div>
                    <div className="request-info">
                      <h3>{request.requester.first_name} {request.requester.last_name}</h3>
                      <p>Grade {request.requester.grade} • Level {request.requester.level}</p>
                    </div>
                    <div className="request-actions">
                      <button className="btn-accept" onClick={() => acceptRequest(request.id)}>
                        ✓ Accept
                      </button>
                      <button className="btn-reject" onClick={() => rejectRequest(request.id)}>
                        ✕ Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <h2 style={{marginTop: '2rem'}}>Sent Requests</h2>
            {sentRequests.length === 0 ? (
              <p className="empty-message">No sent requests</p>
            ) : (
              <div className="request-grid">
                {sentRequests.map(request => (
                  <div key={request.id} className="request-card">
                    <div className="request-avatar">{request.addressee.avatar}</div>
                    <div className="request-info">
                      <h3>{request.addressee.first_name} {request.addressee.last_name}</h3>
                      <p>Grade {request.addressee.grade} • Level {request.addressee.level}</p>
                      <p className="pending-text">Pending...</p>
                    </div>
                    <div className="request-actions">
                      <button className="btn-cancel" onClick={() => cancelRequest(request.id)}>
                        Cancel
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'find' && (
          <div className="find-friends">
            <div className="search-box">
              <input
                type="text"
                placeholder="Search by name..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
              />
              {loading && <span className="loading-spinner">🔄</span>}
            </div>

            {searchQuery.length >= 2 && (
              <div className="search-results">
                {searchResults.length === 0 ? (
                  <p className="empty-message">No students found</p>
                ) : (
                  <div className="student-grid">
                    {searchResults.map(student => (
                      <div key={student.id} className="student-card">
                        <div className="student-avatar">{student.avatar}</div>
                        <div className="student-info">
                          <h3>{student.first_name} {student.last_name}</h3>
                          <p>Grade {student.grade} • Level {student.level}</p>
                        </div>
                        <div className="student-actions">
                          {student.friendship_status === 'none' && (
                            <button className="btn-add" onClick={() => sendRequest(student.id)}>
                              + Add Friend
                            </button>
                          )}
                          {student.friendship_status === 'request_sent' && (
                            <button className="btn-pending" disabled>
                              Request Sent
                            </button>
                          )}
                          {student.friendship_status === 'friends' && (
                            <button className="btn-friends" disabled>
                              ✓ Friends
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {searchQuery.length < 2 && (
              <p className="search-hint">Type at least 2 characters to search for students</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default FriendsPage;

