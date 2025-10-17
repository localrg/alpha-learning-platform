import React, { useState, useEffect } from 'react';
import './StreakDisplay.css';

const StreakDisplay = () => {
  const [streakData, setStreakData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStreakData();
    // Refresh every minute
    const interval = setInterval(fetchStreakData, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchStreakData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/streaks/current', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStreakData(data);
      }
    } catch (error) {
      console.error('Error fetching streak data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="streak-display loading">Loading streaks...</div>;
  }

  if (!streakData) {
    return null;
  }

  return (
    <div className="streak-display">
      <h3 className="streak-title">🔥 Your Streaks</h3>
      
      <div className="streak-cards">
        {/* Login Streak */}
        <div className="streak-card login-streak">
          <div className="streak-header">
            <span className="streak-icon">🌅</span>
            <span className="streak-label">Login Streak</span>
          </div>
          <div className="streak-value">
            {streakData.login_streak} {streakData.login_streak === 1 ? 'day' : 'days'}
          </div>
          <div className="streak-best">
            Best: {streakData.login_streak_best} {streakData.login_streak_best === 1 ? 'day' : 'days'}
          </div>
          {streakData.login_next_milestone && (
            <div className="streak-next">
              <div className="next-milestone-text">
                {streakData.login_next_milestone.remaining} more {streakData.login_next_milestone.remaining === 1 ? 'day' : 'days'} to {streakData.login_next_milestone.days}-day milestone
              </div>
              <div className="next-milestone-reward">
                +{streakData.login_next_milestone.xp} XP
              </div>
              <div className="milestone-progress-bar">
                <div 
                  className="milestone-progress-fill"
                  style={{
                    width: `${(streakData.login_streak / streakData.login_next_milestone.days) * 100}%`
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Practice Streak */}
        <div className="streak-card practice-streak">
          <div className="streak-header">
            <span className="streak-icon">📚</span>
            <span className="streak-label">Practice Streak</span>
          </div>
          <div className="streak-value">
            {streakData.practice_streak} {streakData.practice_streak === 1 ? 'day' : 'days'}
          </div>
          <div className="streak-best">
            Best: {streakData.practice_streak_best} {streakData.practice_streak_best === 1 ? 'day' : 'days'}
          </div>
          {streakData.practice_next_milestone && (
            <div className="streak-next">
              <div className="next-milestone-text">
                {streakData.practice_next_milestone.remaining} more {streakData.practice_next_milestone.remaining === 1 ? 'day' : 'days'} to {streakData.practice_next_milestone.days}-day milestone
              </div>
              <div className="next-milestone-reward">
                +{streakData.practice_next_milestone.xp} XP
              </div>
              <div className="milestone-progress-bar">
                <div 
                  className="milestone-progress-fill"
                  style={{
                    width: `${(streakData.practice_streak / streakData.practice_next_milestone.days) * 100}%`
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StreakDisplay;

