import React, { useState, useEffect } from 'react';
import './DailyChallengesCard.css';

const DailyChallengesCard = () => {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadChallenges();
    // Refresh challenges every minute to update time remaining
    const interval = setInterval(loadChallenges, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadChallenges = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/challenges/daily', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load challenges');
      
      const data = await response.json();
      setChallenges(data.challenges || []);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const getChallengeIcon = (type) => {
    const icons = {
      'question_marathon': '🏃',
      'skill_focus': '📚',
      'perfect_streak': '🔥',
      'speed_challenge': '⚡',
      'review_master': '📝',
      'resource_explorer': '🔍'
    };
    return icons[type] || '🎯';
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      'easy': '#27ae60',
      'medium': '#f39c12',
      'hard': '#e74c3c'
    };
    return colors[difficulty] || '#95a5a6';
  };

  if (loading) {
    return (
      <div className="daily-challenges-card">
        <div className="challenges-header">
          <h3>🎯 Daily Challenges</h3>
        </div>
        <div className="loading">Loading challenges...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="daily-challenges-card">
        <div className="challenges-header">
          <h3>🎯 Daily Challenges</h3>
        </div>
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  const completedCount = challenges.filter(c => c.status === 'completed').length;
  const totalXP = challenges.reduce((sum, c) => sum + c.bonus_xp, 0);
  const earnedXP = challenges.filter(c => c.status === 'completed').reduce((sum, c) => sum + c.bonus_xp, 0);

  return (
    <div className="daily-challenges-card">
      <div className="challenges-header">
        <div>
          <h3>🎯 Daily Challenges</h3>
          <p className="challenges-subtitle">
            {completedCount}/{challenges.length} completed • {earnedXP}/{totalXP} XP earned
          </p>
        </div>
        {challenges.length > 0 && challenges[0].time_remaining && (
          <div className="time-remaining">
            ⏰ {challenges[0].time_remaining}
          </div>
        )}
      </div>

      <div className="challenges-list">
        {challenges.length === 0 && (
          <div className="empty-state">
            <p>No challenges available. Check back tomorrow!</p>
          </div>
        )}

        {challenges.map((challenge) => (
          <div
            key={challenge.id}
            className={`challenge-item ${challenge.status}`}
          >
            <div className="challenge-icon">
              {challenge.status === 'completed' ? '✅' : getChallengeIcon(challenge.type)}
            </div>
            
            <div className="challenge-content">
              <div className="challenge-title">
                {challenge.description}
                <span
                  className="difficulty-badge"
                  style={{ backgroundColor: getDifficultyColor(challenge.difficulty) }}
                >
                  {challenge.difficulty}
                </span>
              </div>
              
              {challenge.status === 'active' && (
                <div className="challenge-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${challenge.completion_percentage}%` }}
                    />
                  </div>
                  <div className="progress-text">
                    {challenge.progress}/{challenge.target} ({challenge.completion_percentage}%)
                  </div>
                </div>
              )}
              
              {challenge.status === 'completed' && (
                <div className="challenge-completed">
                  COMPLETED! +{challenge.bonus_xp} XP
                </div>
              )}
            </div>
            
            <div className="challenge-xp">
              +{challenge.bonus_xp} XP
            </div>
          </div>
        ))}
      </div>

      {completedCount === challenges.length && challenges.length > 0 && (
        <div className="all-completed-banner">
          🎉 All challenges completed! Great work!
        </div>
      )}
    </div>
  );
};

export default DailyChallengesCard;

