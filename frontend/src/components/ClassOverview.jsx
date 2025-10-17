import React, { useState, useEffect } from 'react';
import './ClassOverview.css';

function ClassOverview({ classId, onBack, onViewStudent }) {
  const [classData, setClassData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('performance'); // 'performance', 'activity', 'name'

  useEffect(() => {
    fetchClassData();
  }, [classId]);

  const fetchClassData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/teacher/class/${classId}/overview`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch class data');
      }

      const data = await response.json();
      if (data.success) {
        setClassData(data);
      } else {
        setError(data.error || 'Failed to load class');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSortedStudents = () => {
    if (!classData || !classData.students) return [];
    
    const students = [...classData.students];
    
    switch (sortBy) {
      case 'performance':
        return students.sort((a, b) => (b.avg_accuracy || 0) - (a.avg_accuracy || 0));
      case 'activity':
        return students.sort((a, b) => (b.questions_answered || 0) - (a.questions_answered || 0));
      case 'name':
        return students.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
      default:
        return students;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'on_track':
        return '#28a745';
      case 'needs_practice':
        return '#ff9800';
      case 'needs_help':
        return '#e74c3c';
      default:
        return '#666';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'on_track':
        return '✅ On Track';
      case 'needs_practice':
        return '⚡ Needs Practice';
      case 'needs_help':
        return '⚠️ Needs Help';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="class-overview">
        <div className="loading">Loading class data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="class-overview">
        <div className="error">Error: {error}</div>
        <button className="btn-back" onClick={onBack}>← Back to Dashboard</button>
      </div>
    );
  }

  if (!classData) {
    return (
      <div className="class-overview">
        <div className="error">No class data available</div>
        <button className="btn-back" onClick={onBack}>← Back to Dashboard</button>
      </div>
    );
  }

  const { class: classInfo, metrics, students, skill_performance } = classData;
  const sortedStudents = getSortedStudents();

  return (
    <div className="class-overview">
      {/* Header */}
      <div className="class-overview-header">
        <button className="btn-back" onClick={onBack}>← Back to Dashboard</button>
        <div className="class-title">
          <h1>{classInfo.name}</h1>
          <p>{classInfo.student_count} students | Grade {classInfo.grade_level}</p>
        </div>
      </div>

      {/* Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <div className="metric-value">{Math.round(metrics.avg_accuracy * 100)}%</div>
            <div className="metric-label">Avg Accuracy</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🎯</div>
          <div className="metric-content">
            <div className="metric-value">{Math.round(metrics.mastery_rate * 100)}%</div>
            <div className="metric-label">Mastery Rate</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⚡</div>
          <div className="metric-content">
            <div className="metric-value">{Math.round(metrics.engagement_rate * 100)}%</div>
            <div className="metric-label">Engagement</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">✅</div>
          <div className="metric-content">
            <div className="metric-value">{Math.round(metrics.avg_questions_per_student)}</div>
            <div className="metric-label">Qs/Student</div>
          </div>
        </div>
      </div>

      {/* Skill Performance */}
      {skill_performance && skill_performance.length > 0 && (
        <div className="skill-performance-section">
          <h2>📊 Skill Performance</h2>
          <div className="skill-list">
            {skill_performance.slice(0, 5).map((skill, index) => (
              <div key={index} className="skill-item">
                <div className="skill-info">
                  <span className="skill-name">{skill.skill_name}</span>
                  <span className="skill-stats">
                    {skill.students_mastered} mastered
                    {skill.students_struggling > 0 && (
                      <span className="struggling"> | {skill.students_struggling} struggling</span>
                    )}
                  </span>
                </div>
                <div className="skill-bar-container">
                  <div 
                    className="skill-bar" 
                    style={{ 
                      width: `${skill.avg_accuracy * 100}%`,
                      background: skill.avg_accuracy >= 0.8 ? '#28a745' : 
                                 skill.avg_accuracy >= 0.7 ? '#ff9800' : '#e74c3c'
                    }}
                  />
                  <span className="skill-percentage">{Math.round(skill.avg_accuracy * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Students */}
      <div className="students-section">
        <div className="students-header">
          <h2>👥 Students</h2>
          <div className="sort-controls">
            <label>Sort by:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="performance">Performance</option>
              <option value="activity">Activity</option>
              <option value="name">Name</option>
            </select>
          </div>
        </div>

        <div className="students-list">
          {sortedStudents.map((student) => (
            <div key={student.id} className="student-card">
              <div className="student-header">
                <div className="student-info">
                  <span className="student-avatar">{student.avatar || '😊'}</span>
                  <div>
                    <div className="student-name">{student.name}</div>
                    <div className="student-meta">
                      Level {student.level} | {student.total_xp} XP
                    </div>
                  </div>
                </div>
                <div 
                  className="student-status"
                  style={{ color: getStatusColor(student.status) }}
                >
                  {getStatusText(student.status)}
                </div>
              </div>

              <div className="student-metrics">
                <div className="student-metric">
                  <span className="metric-label">Accuracy:</span>
                  <span className="metric-value">{Math.round(student.avg_accuracy * 100)}%</span>
                </div>
                <div className="student-metric">
                  <span className="metric-label">Questions:</span>
                  <span className="metric-value">{student.questions_answered}</span>
                </div>
                <div className="student-metric">
                  <span className="metric-label">Streak:</span>
                  <span className="metric-value">{student.current_streak} days</span>
                </div>
                <div className="student-metric">
                  <span className="metric-label">Last Active:</span>
                  <span className="metric-value">{student.last_active}</span>
                </div>
              </div>

              <div className="student-actions">
                <button 
                  className="btn-view-student"
                  onClick={() => onViewStudent(student.id)}
                >
                  View Profile
                </button>
                <button className="btn-message">
                  Message
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ClassOverview;

