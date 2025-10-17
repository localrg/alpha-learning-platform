import React, { useState, useEffect } from 'react';
import './AchievementsPage.css';

const AchievementsPage = () => {
  const [achievements, setAchievements] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAchievements();
    fetchStats();
  }, [filter]);

  const fetchAchievements = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = filter === 'all' 
        ? '/api/achievements/student'
        : `/api/achievements/student?category=${filter}`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setAchievements(data.achievements);
      }
    } catch (error) {
      console.error('Error fetching achievements:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/achievements/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const toggleDisplay = async (achievementId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/achievements/${achievementId}/display`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchAchievements(); // Refresh
      }
    } catch (error) {
      console.error('Error toggling display:', error);
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      bronze: '#CD7F32',
      silver: '#C0C0C0',
      gold: '#FFD700',
      platinum: '#E5E4E2',
      diamond: '#B9F2FF'
    };
    return colors[tier] || '#gray';
  };

  const categories = [
    { value: 'all', label: 'All', emoji: '🏆' },
    { value: 'practice', label: 'Practice', emoji: '📝' },
    { value: 'mastery', label: 'Mastery', emoji: '🎯' },
    { value: 'accuracy', label: 'Accuracy', emoji: '🎪' },
    { value: 'streak', label: 'Streak', emoji: '🔥' },
    { value: 'review', label: 'Review', emoji: '📚' },
    { value: 'learning', label: 'Learning', emoji: '💡' },
    { value: 'time', label: 'Time', emoji: '⏰' },
    { value: 'speed', label: 'Speed', emoji: '⚡' },
    { value: 'special', label: 'Special', emoji: '🌟' }
  ];

  if (loading) {
    return <div className="achievements-page loading">Loading achievements...</div>;
  }

  return (
    <div className="achievements-page">
      <div className="achievements-header">
        <h1>🏆 Achievements</h1>
        {stats && (
          <div className="achievements-stats">
            <div className="stat-card">
              <div className="stat-value">{stats.unlocked_count}/{stats.total_achievements}</div>
              <div className="stat-label">Unlocked</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{Math.round(stats.completion_percentage)}%</div>
              <div className="stat-label">Complete</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.displayed_count}</div>
              <div className="stat-label">Displayed</div>
            </div>
          </div>
        )}
      </div>

      <div className="category-filters">
        {categories.map(cat => (
          <button
            key={cat.value}
            className={`category-filter ${filter === cat.value ? 'active' : ''}`}
            onClick={() => setFilter(cat.value)}
          >
            <span className="filter-emoji">{cat.emoji}</span>
            <span className="filter-label">{cat.label}</span>
          </button>
        ))}
      </div>

      <div className="achievements-grid">
        {achievements.map(achievement => {
          const isUnlocked = achievement.is_unlocked;
          const progress = achievement.progress_percentage || 0;
          
          return (
            <div
              key={achievement.achievement_id}
              className={`achievement-card ${isUnlocked ? 'unlocked' : 'locked'} ${achievement.is_displayed ? 'displayed' : ''}`}
              style={{ borderColor: isUnlocked ? getTierColor(achievement.achievement.tier) : '#ddd' }}
            >
              <div className="achievement-icon" style={{ opacity: isUnlocked ? 1 : 0.3 }}>
                {achievement.achievement.icon_emoji}
              </div>
              
              <div className="achievement-tier" style={{ 
                backgroundColor: getTierColor(achievement.achievement.tier),
                opacity: isUnlocked ? 1 : 0.5
              }}>
                {achievement.achievement.tier.toUpperCase()}
              </div>
              
              <h3 className="achievement-name">{achievement.achievement.name}</h3>
              <p className="achievement-description">{achievement.achievement.description}</p>
              
              {!isUnlocked && (
                <div className="achievement-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                  </div>
                  <div className="progress-text">
                    {achievement.progress}/{achievement.achievement.requirement_value}
                  </div>
                </div>
              )}
              
              {isUnlocked && (
                <div className="achievement-unlocked">
                  <div className="unlocked-badge">✓ UNLOCKED</div>
                  <div className="unlock-date">
                    {new Date(achievement.unlocked_at).toLocaleDateString()}
                  </div>
                  <button
                    className={`display-toggle ${achievement.is_displayed ? 'active' : ''}`}
                    onClick={() => toggleDisplay(achievement.achievement_id)}
                  >
                    {achievement.is_displayed ? '⭐ Displayed' : 'Display on Profile'}
                  </button>
                </div>
              )}
              
              <div className="achievement-reward">+{achievement.achievement.xp_reward} XP</div>
            </div>
          );
        })}
      </div>

      {achievements.length === 0 && (
        <div className="no-achievements">
          <p>No achievements found in this category.</p>
        </div>
      )}
    </div>
  );
};

export default AchievementsPage;

