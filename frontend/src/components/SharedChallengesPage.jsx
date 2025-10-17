import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './SharedChallengesPage.css';

const SharedChallengesPage = () => {
  const [activeTab, setActiveTab] = useState('active');
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchChallenges();
  }, [activeTab]);

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const statusParam = activeTab === 'all' ? '' : `?status=${activeTab}`;
      
      const response = await fetch(`/api/shared-challenges${statusParam}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.success) {
        setChallenges(data.challenges || []);
      }
    } catch (error) {
      console.error('Error fetching challenges:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptChallenge = async (challengeId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/shared-challenges/${challengeId}/accept`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchChallenges();
      }
    } catch (error) {
      console.error('Error accepting challenge:', error);
    }
  };

  const handleDeclineChallenge = async (challengeId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/shared-challenges/${challengeId}/decline`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchChallenges();
      }
    } catch (error) {
      console.error('Error declining challenge:', error);
    }
  };

  const getTimeRemaining = (endTime) => {
    const end = new Date(endTime);
    const now = new Date();
    const diff = end - now;

    if (diff <= 0) return 'Expired';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h remaining`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m remaining`;
    } else {
      return `${minutes}m remaining`;
    }
  };

  const renderChallengeCard = (challenge) => {
    const participation = challenge.my_participation;
    const progress = participation.questions_answered / challenge.target_questions;
    const progressPercent = Math.round(progress * 100);

    return (
      <div key={challenge.id} className="challenge-card">
        <div className="challenge-header">
          <div>
            <h3>{challenge.title}</h3>
            <p className="challenge-creator">
              Created by {challenge.creator.display_name || challenge.creator.username}
            </p>
          </div>
          <div className="challenge-type-badge">
            {challenge.challenge_type === 'class' ? '🎓 Class' : '👥 Friend'}
          </div>
        </div>

        {challenge.description && (
          <p className="challenge-description">{challenge.description}</p>
        )}

        <div className="challenge-details">
          <div className="detail-item">
            <span className="detail-label">Goal:</span>
            <span>{challenge.target_questions} questions @ {Math.round(challenge.target_accuracy * 100)}% accuracy</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Mode:</span>
            <span>{challenge.mode === 'competitive' ? '🏆 Competitive' : '🤝 Collaborative'}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Reward:</span>
            <span>{challenge.xp_reward} XP</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Time:</span>
            <span className={getTimeRemaining(challenge.end_time) === 'Expired' ? 'expired' : ''}>
              {getTimeRemaining(challenge.end_time)}
            </span>
          </div>
        </div>

        {participation.status === 'invited' ? (
          <div className="challenge-actions">
            <button 
              className="btn-accept"
              onClick={() => handleAcceptChallenge(challenge.id)}
            >
              Accept Challenge
            </button>
            <button 
              className="btn-decline"
              onClick={() => handleDeclineChallenge(challenge.id)}
            >
              Decline
            </button>
          </div>
        ) : (
          <>
            <div className="challenge-progress">
              <div className="progress-header">
                <span>Your Progress: {participation.questions_answered}/{challenge.target_questions}</span>
                <span>{Math.round(participation.accuracy * 100)}% accuracy</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>

            {participation.rank && (
              <div className="challenge-rank">
                Rank: #{participation.rank} of {challenge.participant_count}
              </div>
            )}

            <div className="challenge-actions">
              {participation.completed ? (
                <button 
                  className="btn-view"
                  onClick={() => navigate(`/shared-challenges/${challenge.id}`)}
                >
                  View Results
                </button>
              ) : (
                <>
                  <button 
                    className="btn-continue"
                    onClick={() => navigate(`/practice?skill=${challenge.skill_id}&challenge=${challenge.id}`)}
                  >
                    Continue Challenge
                  </button>
                  <button 
                    className="btn-view"
                    onClick={() => navigate(`/shared-challenges/${challenge.id}`)}
                  >
                    View Leaderboard
                  </button>
                </>
              )}
            </div>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="shared-challenges-page">
      <div className="page-header">
        <h1>🎯 Challenges</h1>
        <button 
          className="btn-create"
          onClick={() => setShowCreateModal(true)}
        >
          + Create Challenge
        </button>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'active' ? 'active' : ''}`}
          onClick={() => setActiveTab('active')}
        >
          Active
        </button>
        <button
          className={`tab ${activeTab === 'invited' ? 'active' : ''}`}
          onClick={() => setActiveTab('invited')}
        >
          Invitations
        </button>
        <button
          className={`tab ${activeTab === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveTab('completed')}
        >
          Completed
        </button>
      </div>

      <div className="challenges-container">
        {loading ? (
          <div className="loading">Loading challenges...</div>
        ) : challenges.length === 0 ? (
          <div className="empty-state">
            <p>No {activeTab} challenges found.</p>
            {activeTab === 'active' && (
              <button 
                className="btn-create"
                onClick={() => setShowCreateModal(true)}
              >
                Create Your First Challenge
              </button>
            )}
          </div>
        ) : (
          <div className="challenges-grid">
            {challenges.map(renderChallengeCard)}
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateChallengeModal 
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchChallenges();
          }}
        />
      )}
    </div>
  );
};

const CreateChallengeModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    challenge_type: 'friend',
    mode: 'competitive',
    skill_id: 1,
    target_questions: 20,
    target_accuracy: 0.9,
    duration_hours: 24,
    participant_ids: [],
    class_id: null
  });
  const [friends, setFriends] = useState([]);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFriends();
    fetchClasses();
  }, []);

  const fetchFriends = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/friends', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.success) {
        setFriends(data.friends || []);
      }
    } catch (error) {
      console.error('Error fetching friends:', error);
    }
  };

  const fetchClasses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/classes', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.success) {
        setClasses(data.classes || []);
      }
    } catch (error) {
      console.error('Error fetching classes:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/shared-challenges', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      if (data.success) {
        onSuccess();
      } else {
        alert(data.error || 'Failed to create challenge');
      }
    } catch (error) {
      console.error('Error creating challenge:', error);
      alert('Failed to create challenge');
    } finally {
      setLoading(false);
    }
  };

  const toggleParticipant = (studentId) => {
    setFormData(prev => ({
      ...prev,
      participant_ids: prev.participant_ids.includes(studentId)
        ? prev.participant_ids.filter(id => id !== studentId)
        : [...prev.participant_ids, studentId]
    }));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create Challenge</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="challenge-form">
          <div className="form-group">
            <label>Challenge Title *</label>
            <input
              type="text"
              value={formData.title}
              onChange={e => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Multiplication Mastery"
              required
              maxLength={200}
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              placeholder="Optional description..."
              rows={3}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Challenge Type *</label>
              <select
                value={formData.challenge_type}
                onChange={e => setFormData({ ...formData, challenge_type: e.target.value })}
              >
                <option value="friend">Friend Challenge</option>
                <option value="class">Class Challenge</option>
              </select>
            </div>

            <div className="form-group">
              <label>Mode *</label>
              <select
                value={formData.mode}
                onChange={e => setFormData({ ...formData, mode: e.target.value })}
              >
                <option value="competitive">Competitive</option>
                <option value="collaborative">Collaborative</option>
              </select>
            </div>
          </div>

          {formData.challenge_type === 'friend' ? (
            <div className="form-group">
              <label>Select Friends *</label>
              <div className="participant-list">
                {friends.length === 0 ? (
                  <p className="no-friends">No friends yet. Add friends to challenge them!</p>
                ) : (
                  friends.map(friend => (
                    <label key={friend.student.id} className="participant-item">
                      <input
                        type="checkbox"
                        checked={formData.participant_ids.includes(friend.student.id)}
                        onChange={() => toggleParticipant(friend.student.id)}
                      />
                      <span>{friend.student.display_name || friend.student.username}</span>
                    </label>
                  ))
                )}
              </div>
            </div>
          ) : (
            <div className="form-group">
              <label>Select Class *</label>
              <select
                value={formData.class_id || ''}
                onChange={e => setFormData({ ...formData, class_id: parseInt(e.target.value) })}
                required
              >
                <option value="">Choose a class...</option>
                {classes.map(cls => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name} ({cls.member_count} members)
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label>Target Questions *</label>
              <input
                type="number"
                value={formData.target_questions}
                onChange={e => setFormData({ ...formData, target_questions: parseInt(e.target.value) })}
                min={5}
                max={50}
                required
              />
            </div>

            <div className="form-group">
              <label>Target Accuracy *</label>
              <select
                value={formData.target_accuracy}
                onChange={e => setFormData({ ...formData, target_accuracy: parseFloat(e.target.value) })}
              >
                <option value={0.7}>70%</option>
                <option value={0.8}>80%</option>
                <option value={0.9}>90%</option>
                <option value={0.95}>95%</option>
                <option value={1.0}>100%</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Duration *</label>
            <select
              value={formData.duration_hours}
              onChange={e => setFormData({ ...formData, duration_hours: parseInt(e.target.value) })}
            >
              <option value={1}>1 hour</option>
              <option value={6}>6 hours</option>
              <option value={24}>24 hours</option>
              <option value={72}>3 days</option>
              <option value={168}>1 week</option>
            </select>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-submit" 
              disabled={loading || (formData.challenge_type === 'friend' && formData.participant_ids.length === 0)}
            >
              {loading ? 'Creating...' : 'Create Challenge'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SharedChallengesPage;

