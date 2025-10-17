import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ChallengeDetailPage.css';

const ChallengeDetailPage = () => {
  const { challengeId } = useParams();
  const [challenge, setChallenge] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchChallengeDetails();
    fetchLeaderboard();
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchLeaderboard();
    }, 30000);

    return () => clearInterval(interval);
  }, [challengeId]);

  const fetchChallengeDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/shared-challenges/${challengeId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.success) {
        setChallenge(data.challenge);
      }
    } catch (error) {
      console.error('Error fetching challenge:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/shared-challenges/${challengeId}/leaderboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.success) {
        setLeaderboard(data.leaderboard || []);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
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
      return `${days}d ${hours % 24}h`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getRankClass = (rank) => {
    if (rank === 1) return 'rank-gold';
    if (rank === 2) return 'rank-silver';
    if (rank === 3) return 'rank-bronze';
    return '';
  };

  if (loading) {
    return <div className="loading">Loading challenge...</div>;
  }

  if (!challenge) {
    return <div className="error">Challenge not found</div>;
  }

  const myParticipation = challenge.my_participation;
  const progress = myParticipation.questions_answered / challenge.target_questions;
  const progressPercent = Math.round(progress * 100);

  return (
    <div className="challenge-detail-page">
      <button className="back-btn" onClick={() => navigate('/shared-challenges')}>
        ← Back to Challenges
      </button>

      <div className="challenge-header-section">
        <div className="header-content">
          <h1>{challenge.title}</h1>
          <p className="challenge-creator">
            Created by {challenge.creator.display_name || challenge.creator.username}
          </p>
          {challenge.description && (
            <p className="challenge-description">{challenge.description}</p>
          )}
        </div>
        
        <div className="header-badges">
          <div className="badge">
            {challenge.challenge_type === 'class' ? '🎓 Class' : '👥 Friend'}
          </div>
          <div className="badge">
            {challenge.mode === 'competitive' ? '🏆 Competitive' : '🤝 Collaborative'}
          </div>
          <div className={`badge ${getTimeRemaining(challenge.end_time) === 'Expired' ? 'expired' : ''}`}>
            ⏰ {getTimeRemaining(challenge.end_time)}
          </div>
        </div>
      </div>

      <div className="challenge-info-grid">
        <div className="info-card">
          <div className="info-label">Target Questions</div>
          <div className="info-value">{challenge.target_questions}</div>
        </div>
        <div className="info-card">
          <div className="info-label">Target Accuracy</div>
          <div className="info-value">{Math.round(challenge.target_accuracy * 100)}%</div>
        </div>
        <div className="info-card">
          <div className="info-label">XP Reward</div>
          <div className="info-value">{challenge.xp_reward} XP</div>
        </div>
        <div className="info-card">
          <div className="info-label">Participants</div>
          <div className="info-value">{challenge.participant_count}</div>
        </div>
      </div>

      <div className="my-progress-section">
        <h2>Your Progress</h2>
        <div className="progress-card">
          <div className="progress-stats">
            <div className="stat">
              <span className="stat-label">Questions Answered</span>
              <span className="stat-value">
                {myParticipation.questions_answered} / {challenge.target_questions}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Accuracy</span>
              <span className="stat-value">
                {Math.round(myParticipation.accuracy * 100)}%
              </span>
            </div>
            {myParticipation.rank && (
              <div className="stat">
                <span className="stat-label">Current Rank</span>
                <span className={`stat-value rank-badge ${getRankClass(myParticipation.rank)}`}>
                  {getRankBadge(myParticipation.rank)}
                </span>
              </div>
            )}
          </div>

          <div className="progress-bar-container">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <span className="progress-percent">{progressPercent}% Complete</span>
          </div>

          {myParticipation.completed ? (
            <div className="completion-badge">
              ✅ Challenge Completed!
            </div>
          ) : (
            <button 
              className="btn-continue"
              onClick={() => navigate(`/practice?skill=${challenge.skill_id}&challenge=${challenge.id}`)}
            >
              Continue Challenge
            </button>
          )}
        </div>
      </div>

      <div className="leaderboard-section">
        <h2>🏆 Leaderboard</h2>
        <div className="leaderboard">
          {leaderboard.map((participant, index) => (
            <div 
              key={participant.id} 
              className={`leaderboard-item ${getRankClass(participant.rank)} ${participant.student_id === myParticipation.student_id ? 'my-rank' : ''}`}
            >
              <div className="rank-badge-large">
                {getRankBadge(participant.rank)}
              </div>
              
              <div className="participant-info">
                <div className="participant-name">
                  {participant.student.display_name || participant.student.username}
                  {participant.student_id === myParticipation.student_id && (
                    <span className="you-badge">You</span>
                  )}
                </div>
                <div className="participant-level">
                  Level {participant.student.current_level} • {participant.student.total_xp} XP
                </div>
              </div>

              <div className="participant-stats">
                <div className="stat-item">
                  <span className="stat-label">Questions</span>
                  <span className="stat-value">
                    {participant.questions_answered}/{challenge.target_questions}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Accuracy</span>
                  <span className="stat-value">
                    {Math.round(participant.accuracy * 100)}%
                  </span>
                </div>
                {participant.completed && (
                  <div className="completed-badge">✓</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChallengeDetailPage;

