import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ReviewDashboard.css';

const ReviewDashboard = () => {
  const [reviewsDue, setReviewsDue] = useState([]);
  const [upcomingReviews, setUpcomingReviews] = useState([]);
  const [reviewHistory, setReviewHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('due'); // 'due', 'upcoming', 'history'
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchReviewData();
  }, []);

  const fetchReviewData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      // Fetch reviews due
      const dueResponse = await axios.get('http://localhost:5000/api/reviews/due', config);
      setReviewsDue(dueResponse.data.reviews_due || []);

      // Fetch upcoming reviews
      const upcomingResponse = await axios.get('http://localhost:5000/api/reviews/upcoming', config);
      setUpcomingReviews(upcomingResponse.data.upcoming_reviews || []);

      // Fetch review history
      const historyResponse = await axios.get('http://localhost:5000/api/reviews/history', config);
      setReviewHistory(historyResponse.data.review_history || []);

      setLoading(false);
    } catch (err) {
      console.error('Error fetching review data:', err);
      setError('Failed to load review data');
      setLoading(false);
    }
  };

  const startReview = (learningPathId) => {
    navigate(`/review/${learningPathId}`);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getDaysText = (days) => {
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    return `in ${days} days`;
  };

  if (loading) {
    return (
      <div className="review-dashboard">
        <div className="loading">Loading reviews...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="review-dashboard">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="review-dashboard">
      <div className="review-header">
        <h1>📚 Skill Reviews</h1>
        <p className="review-subtitle">Keep your mastered skills sharp with spaced repetition</p>
      </div>

      <div className="review-tabs">
        <button
          className={`tab ${activeTab === 'due' ? 'active' : ''}`}
          onClick={() => setActiveTab('due')}
        >
          Due Now {reviewsDue.length > 0 && <span className="badge">{reviewsDue.length}</span>}
        </button>
        <button
          className={`tab ${activeTab === 'upcoming' ? 'active' : ''}`}
          onClick={() => setActiveTab('upcoming')}
        >
          Upcoming
        </button>
        <button
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
      </div>

      {/* Reviews Due Tab */}
      {activeTab === 'due' && (
        <div className="review-section">
          {reviewsDue.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✅</div>
              <h3>No reviews due!</h3>
              <p>All your skills are up to date. Great job!</p>
              <button onClick={() => navigate('/dashboard')} className="btn-primary">
                Back to Dashboard
              </button>
            </div>
          ) : (
            <div className="reviews-list">
              {reviewsDue.map((review) => (
                <div key={review.learning_path_id} className="review-card">
                  <div className="review-card-header">
                    <h3>⭐ {review.skill_name}</h3>
                    <span className="review-number">Review #{review.review_number}</span>
                  </div>
                  <p className="skill-description">{review.skill_description}</p>
                  <div className="review-meta">
                    <div className="meta-item">
                      <span className="meta-label">Mastered:</span>
                      <span className="meta-value">{formatDate(review.mastery_date)}</span>
                    </div>
                    {review.last_reviewed_at && (
                      <div className="meta-item">
                        <span className="meta-label">Last reviewed:</span>
                        <span className="meta-value">{formatDate(review.last_reviewed_at)}</span>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => startReview(review.learning_path_id)}
                    className="btn-review"
                  >
                    Start Review
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Upcoming Reviews Tab */}
      {activeTab === 'upcoming' && (
        <div className="review-section">
          {upcomingReviews.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📅</div>
              <h3>No upcoming reviews</h3>
              <p>Keep mastering new skills to build your review schedule!</p>
            </div>
          ) : (
            <div className="upcoming-list">
              {upcomingReviews.map((review) => (
                <div key={review.learning_path_id} className="upcoming-card">
                  <div className="upcoming-icon">📌</div>
                  <div className="upcoming-content">
                    <h4>{review.skill_name}</h4>
                    <p className="upcoming-date">
                      {getDaysText(review.days_until)} • Review #{review.review_number}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="review-section">
          {reviewHistory.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📖</div>
              <h3>No review history yet</h3>
              <p>Complete some reviews to see your history here!</p>
            </div>
          ) : (
            <div className="history-list">
              {reviewHistory.map((session) => (
                <div key={session.id} className="history-card">
                  <div className="history-header">
                    <h4>{session.skill_name}</h4>
                    <span className={`status-badge ${session.passed ? 'passed' : 'failed'}`}>
                      {session.passed ? '✓ Passed' : '✗ Needs Work'}
                    </span>
                  </div>
                  <div className="history-details">
                    <div className="detail-item">
                      <span className="detail-label">Accuracy:</span>
                      <span className="detail-value">{session.accuracy}%</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Score:</span>
                      <span className="detail-value">
                        {session.correct_answers}/{session.questions_answered}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Date:</span>
                      <span className="detail-value">{formatDate(session.completed_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ReviewDashboard;

