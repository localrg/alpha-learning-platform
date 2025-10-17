import React, { useState, useEffect } from 'react';
import './LeaderboardPage.css';

const LeaderboardPage = () => {
  const [activeTab, setActiveTab] = useState('global');
  const [leaderboard, setLeaderboard] = useState([]);
  const [myRank, setMyRank] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadLeaderboard();
    loadMyRank();
  }, [activeTab]);

  const loadLeaderboard = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      let endpoint = '';
      
      switch (activeTab) {
        case 'global':
          endpoint = '/api/leaderboards/global';
          break;
        case 'skills':
          endpoint = '/api/leaderboards/skills';
          break;
        case 'achievements':
          endpoint = '/api/leaderboards/achievements';
          break;
        default:
          endpoint = '/api/leaderboards/global';
      }
      
      const response = await fetch(`http://localhost:5000${endpoint}?limit=50`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load leaderboard');
      
      const data = await response.json();
      setLeaderboard(data.leaderboard || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadMyRank = async () => {
    try {
      const token = localStorage.getItem('token');
      const leaderboardType = activeTab === 'global' ? 'global_xp' : activeTab;
      
      const response = await fetch(`http://localhost:5000/api/leaderboards/my-rank/${leaderboardType}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMyRank(data.rank_info);
      }
    } catch (err) {
      console.error('Failed to load rank:', err);
    }
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    if (rank <= 10) return '⭐';
    return '👤';
  };

  const getTierBadge = (tier) => {
    const badges = {
      'champion': '👑',
      'master': '⚡',
      'expert': '💎',
      'intermediate': '🔷',
      'beginner': '🔹'
    };
    return badges[tier] || '🔹';
  };

  const getTierColor = (tier) => {
    const colors = {
      'champion': '#FFD700',
      'master': '#C0C0C0',
      'expert': '#CD7F32',
      'intermediate': '#4A90E2',
      'beginner': '#95A5A6'
    };
    return colors[tier] || '#95A5A6';
  };

  const getMetricDisplay = (entry) => {
    switch (activeTab) {
      case 'global':
        return `${entry.total_xp?.toLocaleString() || 0} XP`;
      case 'skills':
        return `${entry.skills_mastered || 0} skills`;
      case 'achievements':
        return `${entry.achievements_unlocked || 0} achievements`;
      default:
        return '';
    }
  };

  return (
    <div className="leaderboard-page">
      <div className="leaderboard-header">
        <h1>🏆 Leaderboards</h1>
        <p>See how you rank against other students!</p>
      </div>

      {/* My Rank Card */}
      {myRank && (
        <div className="my-rank-card">
          <div className="rank-badge-large">
            {getRankBadge(myRank.rank)}
          </div>
          <div className="rank-info">
            <div className="rank-number">#{myRank.rank}</div>
            <div className="rank-details">
              <div className="rank-metric">{myRank.metric_value?.toLocaleString()} {myRank.metric_name}</div>
              <div className="rank-percentile">Top {myRank.percentile?.toFixed(1)}%</div>
              <div className="rank-tier" style={{ color: getTierColor(myRank.tier) }}>
                {getTierBadge(myRank.tier)} {myRank.tier?.charAt(0).toUpperCase() + myRank.tier?.slice(1)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="leaderboard-tabs">
        <button
          className={`tab ${activeTab === 'global' ? 'active' : ''}`}
          onClick={() => setActiveTab('global')}
        >
          🌍 Global XP
        </button>
        <button
          className={`tab ${activeTab === 'skills' ? 'active' : ''}`}
          onClick={() => setActiveTab('skills')}
        >
          📚 Skills Mastered
        </button>
        <button
          className={`tab ${activeTab === 'achievements' ? 'active' : ''}`}
          onClick={() => setActiveTab('achievements')}
        >
          🏅 Achievements
        </button>
      </div>

      {/* Leaderboard List */}
      <div className="leaderboard-content">
        {loading && <div className="loading">Loading leaderboard...</div>}
        {error && <div className="error">Error: {error}</div>}
        
        {!loading && !error && leaderboard.length === 0 && (
          <div className="empty-state">
            <p>No rankings available yet. Be the first to earn XP!</p>
          </div>
        )}
        
        {!loading && !error && leaderboard.length > 0 && (
          <div className="leaderboard-list">
            {leaderboard.map((entry) => (
              <div
                key={entry.student_id}
                className={`leaderboard-entry ${entry.rank <= 3 ? 'top-three' : ''} ${myRank && entry.rank === myRank.rank ? 'my-entry' : ''}`}
              >
                <div className="entry-rank">
                  <span className="rank-badge">{getRankBadge(entry.rank)}</span>
                  <span className="rank-number">#{entry.rank}</span>
                </div>
                
                <div className="entry-info">
                  <div className="entry-name">{entry.student_name}</div>
                  <div className="entry-details">
                    {entry.grade && <span className="entry-grade">Grade {entry.grade}</span>}
                    {entry.level && <span className="entry-level">Level {entry.level}</span>}
                  </div>
                </div>
                
                <div className="entry-metric">
                  <div className="metric-value">{getMetricDisplay(entry)}</div>
                  <div className="tier-badge" style={{ color: getTierColor(entry.tier) }}>
                    {getTierBadge(entry.tier)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="leaderboard-actions">
        <button className="refresh-button" onClick={loadLeaderboard} disabled={loading}>
          🔄 Refresh
        </button>
      </div>
    </div>
  );
};

export default LeaderboardPage;

