import React, { useState, useEffect } from 'react';
import './ClassesPage.css';

function ClassesPage() {
  const [activeTab, setActiveTab] = useState('my-classes'); // 'my-classes', 'join', 'create'
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [loading, setLoading] = useState(true);
  const [inviteCode, setInviteCode] = useState('');
  const [newClass, setNewClass] = useState({ name: '', description: '', grade_level: 5 });
  const [members, setMembers] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/classes', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setClasses(data.classes || []);
      }
    } catch (error) {
      console.error('Error fetching classes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinClass = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/classes/join', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ invite_code: inviteCode })
      });

      if (response.ok) {
        alert('Joined class successfully!');
        setInviteCode('');
        fetchClasses();
        setActiveTab('my-classes');
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to join class');
      }
    } catch (error) {
      alert('Error joining class');
    }
  };

  const handleCreateClass = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/classes', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newClass)
      });

      if (response.ok) {
        alert('Class created successfully!');
        setNewClass({ name: '', description: '', grade_level: 5 });
        fetchClasses();
        setActiveTab('my-classes');
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to create class');
      }
    } catch (error) {
      alert('Error creating class');
    }
  };

  const handleLeaveClass = async (classId) => {
    if (!confirm('Are you sure you want to leave this class?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/classes/${classId}/leave`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Left class successfully');
        fetchClasses();
        setSelectedClass(null);
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to leave class');
      }
    } catch (error) {
      alert('Error leaving class');
    }
  };

  const viewClassDetails = async (classItem) => {
    setSelectedClass(classItem);

    // Fetch members
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/classes/${classItem.id}/members`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setMembers(data.members || []);
      }
    } catch (error) {
      console.error('Error fetching members:', error);
    }

    // Fetch leaderboard
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/classes/${classItem.id}/leaderboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data.leaderboard || []);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }

    // Fetch stats
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/classes/${classItem.id}/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  if (selectedClass) {
    return (
      <div className="classes-page">
        <div className="class-detail">
          <div className="class-header">
            <button onClick={() => setSelectedClass(null)} className="back-button">← Back to Classes</button>
            <h2>{selectedClass.name}</h2>
            <p className="class-description">{selectedClass.description}</p>
            <div className="class-meta">
              <span className="badge">Grade {selectedClass.grade_level}</span>
              <span className="badge">{selectedClass.member_count} Members</span>
              {selectedClass.role === 'teacher' && (
                <span className="badge badge-teacher">Teacher</span>
              )}
            </div>
            {selectedClass.role === 'teacher' && (
              <div className="invite-code-box">
                <strong>Invite Code:</strong> <code>{selectedClass.invite_code}</code>
              </div>
            )}
          </div>

          <div className="class-tabs">
            <div className="tab-buttons">
              <button className="active">📊 Leaderboard</button>
            </div>

            <div className="leaderboard-section">
              {stats && (
                <div className="class-stats-summary">
                  <div className="stat-card">
                    <div className="stat-value">{stats.member_count}</div>
                    <div className="stat-label">Members</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{stats.total_xp.toLocaleString()}</div>
                    <div className="stat-label">Total XP</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{stats.average_level}</div>
                    <div className="stat-label">Avg Level</div>
                  </div>
                </div>
              )}

              <div className="leaderboard-list">
                {leaderboard.map((member, index) => (
                  <div key={member.id} className={`leaderboard-item rank-${member.rank}`}>
                    <div className="rank-badge">#{member.rank}</div>
                    <div className="member-avatar">{member.avatar}</div>
                    <div className="member-info">
                      <div className="member-name">{member.name}</div>
                      <div className="member-meta">Grade {member.grade} • Level {member.level}</div>
                    </div>
                    <div className="member-xp">{member.xp.toLocaleString()} XP</div>
                  </div>
                ))}
              </div>
            </div>

            {selectedClass.role === 'student' && (
              <button onClick={() => handleLeaveClass(selectedClass.id)} className="leave-button">
                Leave Class
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="classes-page">
      <div className="classes-tabs">
        <button
          className={activeTab === 'my-classes' ? 'active' : ''}
          onClick={() => setActiveTab('my-classes')}
        >
          📚 My Classes
        </button>
        <button
          className={activeTab === 'join' ? 'active' : ''}
          onClick={() => setActiveTab('join')}
        >
          ➕ Join Class
        </button>
        <button
          className={activeTab === 'create' ? 'active' : ''}
          onClick={() => setActiveTab('create')}
        >
          🎓 Create Class
        </button>
      </div>

      <div className="classes-content">
        {activeTab === 'my-classes' && (
          <div className="my-classes">
            {loading ? (
              <p>Loading classes...</p>
            ) : classes.length === 0 ? (
              <div className="empty-state">
                <p>You haven't joined any classes yet.</p>
                <p>Use an invite code to join a class, or create your own!</p>
              </div>
            ) : (
              <div className="classes-grid">
                {classes.map((classItem) => (
                  <div key={classItem.id} className="class-card" onClick={() => viewClassDetails(classItem)}>
                    <h3>{classItem.name}</h3>
                    <p className="class-description">{classItem.description || 'No description'}</p>
                    <div className="class-info">
                      <span className="badge">Grade {classItem.grade_level}</span>
                      <span className="badge">{classItem.member_count} members</span>
                      {classItem.role === 'teacher' && <span className="badge badge-teacher">Teacher</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'join' && (
          <div className="join-class">
            <h3>Join a Class</h3>
            <p>Enter the invite code provided by your teacher:</p>
            <form onSubmit={handleJoinClass}>
              <input
                type="text"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                placeholder="INVITE CODE"
                maxLength={6}
                required
              />
              <button type="submit">Join Class</button>
            </form>
          </div>
        )}

        {activeTab === 'create' && (
          <div className="create-class">
            <h3>Create a Class</h3>
            <form onSubmit={handleCreateClass}>
              <div className="form-group">
                <label>Class Name</label>
                <input
                  type="text"
                  value={newClass.name}
                  onChange={(e) => setNewClass({ ...newClass, name: e.target.value })}
                  placeholder="e.g., Mrs. Smith's 5th Grade Math"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description (Optional)</label>
                <textarea
                  value={newClass.description}
                  onChange={(e) => setNewClass({ ...newClass, description: e.target.value })}
                  placeholder="Brief description of the class"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Grade Level</label>
                <select
                  value={newClass.grade_level}
                  onChange={(e) => setNewClass({ ...newClass, grade_level: parseInt(e.target.value) })}
                  required
                >
                  <option value={3}>Grade 3</option>
                  <option value={4}>Grade 4</option>
                  <option value={5}>Grade 5</option>
                  <option value={6}>Grade 6</option>
                  <option value={7}>Grade 7</option>
                  <option value={8}>Grade 8</option>
                </select>
              </div>
              <button type="submit">Create Class</button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default ClassesPage;

