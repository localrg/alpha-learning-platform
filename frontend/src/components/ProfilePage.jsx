import React, { useState, useEffect } from 'react';
import './ProfilePage.css';

const ProfilePage = ({ studentId, isOwnProfile = false }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    fetchProfile();
  }, [studentId]);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = isOwnProfile 
        ? 'http://localhost:5000/api/profiles/me'
        : `http://localhost:5000/api/profiles/${studentId}`;
      
      const response = await fetch(url, {
        headers: token ? {
          'Authorization': `Bearer ${token}`
        } : {}
      });
      
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData({
          bio: data.bio || '',
          avatar: data.avatar || '😊',
          profile_visibility: data.profile_visibility || 'public',
          show_stats: data.show_stats !== false,
          show_achievements: data.show_achievements !== false,
          show_activity: data.show_activity !== false
        });
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/profiles/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        await fetchProfile();
        setEditing(false);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  if (loading) {
    return <div className="profile-page loading">Loading profile...</div>;
  }

  if (!profile) {
    return <div className="profile-page error">Profile not found</div>;
  }

  if (profile.error) {
    return <div className="profile-page error">{profile.error}</div>;
  }

  return (
    <div className="profile-page">
      {/* Header */}
      <div className="profile-header">
        <div className="profile-avatar-large">{profile.avatar || '😊'}</div>
        <div className="profile-header-info">
          <h1 className="profile-name">{profile.name}</h1>
          <div className="profile-meta">
            <span className="profile-grade">Grade {profile.grade}</span>
            {profile.stats && (
              <span className="profile-level">Level {profile.stats.level}</span>
            )}
          </div>
          {profile.bio && <p className="profile-bio">{profile.bio}</p>}
        </div>
        {isOwnProfile && (
          <button 
            className="edit-profile-btn"
            onClick={() => setEditing(!editing)}
          >
            {editing ? '✕ Cancel' : '✏️ Edit Profile'}
          </button>
        )}
      </div>

      {/* Edit Form */}
      {editing && (
        <div className="profile-edit-form">
          <h3>Edit Profile</h3>
          
          <div className="form-group">
            <label>Avatar (Emoji)</label>
            <input
              type="text"
              value={formData.avatar}
              onChange={(e) => setFormData({...formData, avatar: e.target.value})}
              placeholder="😊"
              maxLength="2"
            />
          </div>

          <div className="form-group">
            <label>Bio</label>
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({...formData, bio: e.target.value})}
              placeholder="Tell us about yourself..."
              maxLength="200"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>Profile Visibility</label>
            <select
              value={formData.profile_visibility}
              onChange={(e) => setFormData({...formData, profile_visibility: e.target.value})}
            >
              <option value="public">Public - Anyone can view</option>
              <option value="friends">Friends Only</option>
              <option value="private">Private - Only me</option>
            </select>
          </div>

          <div className="form-group-checkboxes">
            <label>
              <input
                type="checkbox"
                checked={formData.show_stats}
                onChange={(e) => setFormData({...formData, show_stats: e.target.checked})}
              />
              Show Statistics
            </label>
            <label>
              <input
                type="checkbox"
                checked={formData.show_achievements}
                onChange={(e) => setFormData({...formData, show_achievements: e.target.checked})}
              />
              Show Achievements
            </label>
            <label>
              <input
                type="checkbox"
                checked={formData.show_activity}
                onChange={(e) => setFormData({...formData, show_activity: e.target.checked})}
              />
              Show Activity
            </label>
          </div>

          <button className="save-profile-btn" onClick={handleSave}>
            💾 Save Changes
          </button>
        </div>
      )}

      {/* Stats Section */}
      {profile.stats && (
        <div className="profile-section">
          <h2 className="section-title">📊 Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{profile.stats.level}</div>
              <div className="stat-label">Level</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{profile.stats.xp?.toLocaleString()}</div>
              <div className="stat-label">Total XP</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{profile.stats.mastered_skills}</div>
              <div className="stat-label">Skills Mastered</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{profile.stats.total_questions?.toLocaleString()}</div>
              <div className="stat-label">Questions Answered</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{profile.stats.accuracy}%</div>
              <div className="stat-label">Accuracy</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{profile.stats.practice_streak}</div>
              <div className="stat-label">Practice Streak</div>
            </div>
          </div>
        </div>
      )}

      {/* Achievements Section */}
      {profile.achievements && (
        <div className="profile-section">
          <h2 className="section-title">🏆 Achievements ({profile.achievements.total})</h2>
          <div className="achievements-grid">
            {profile.achievements.featured.map((achievement) => (
              <div key={achievement.id} className={`achievement-card ${achievement.tier}`}>
                <div className="achievement-icon">{achievement.icon}</div>
                <div className="achievement-name">{achievement.name}</div>
                <div className="achievement-tier">{achievement.tier}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Section */}
      {profile.activity && profile.activity.length > 0 && (
        <div className="profile-section">
          <h2 className="section-title">📅 Recent Activity</h2>
          <div className="activity-list">
            {profile.activity.map((item, index) => (
              <div key={index} className="activity-item">
                <span className="activity-icon">{item.icon}</span>
                <span className="activity-title">{item.title}</span>
                <span className="activity-time">
                  {new Date(item.timestamp).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;

