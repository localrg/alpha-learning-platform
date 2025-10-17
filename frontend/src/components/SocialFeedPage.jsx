import React, { useState, useEffect } from 'react';
import ActivityCard from './ActivityCard';
import './SocialFeedPage.css';

const SocialFeedPage = () => {
  const [activeTab, setActiveTab] = useState('all');
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    fetchActivities(true);
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchActivities(true);
    }, 30000);

    return () => clearInterval(interval);
  }, [activeTab]);

  const fetchActivities = async (reset = false) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const currentOffset = reset ? 0 : offset;
      
      let url = `/api/feed?limit=20&offset=${currentOffset}`;
      if (activeTab !== 'all') {
        url += `&type=${activeTab}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.success) {
        if (reset) {
          setActivities(data.activities || []);
          setOffset(20);
        } else {
          setActivities(prev => [...prev, ...(data.activities || [])]);
          setOffset(prev => prev + 20);
        }
        setHasMore(data.has_more || false);
      }
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchActivities(false);
    }
  };

  const handleDeleteActivity = async (activityId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/feed/${activityId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setActivities(prev => prev.filter(a => a.id !== activityId));
      }
    } catch (error) {
      console.error('Error deleting activity:', error);
    }
  };

  return (
    <div className="social-feed-page">
      <div className="feed-header">
        <h1>📰 Activity Feed</h1>
        <p className="feed-subtitle">See what your friends and classmates are achieving!</p>
      </div>

      <div className="feed-tabs">
        <button
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          All
        </button>
        <button
          className={`tab ${activeTab === 'friends' ? 'active' : ''}`}
          onClick={() => setActiveTab('friends')}
        >
          Friends
        </button>
        <button
          className={`tab ${activeTab === 'classes' ? 'active' : ''}`}
          onClick={() => setActiveTab('classes')}
        >
          Classes
        </button>
        <button
          className={`tab ${activeTab === 'me' ? 'active' : ''}`}
          onClick={() => setActiveTab('me')}
        >
          Me
        </button>
      </div>

      <div className="feed-container">
        {loading && activities.length === 0 ? (
          <div className="loading">Loading activities...</div>
        ) : activities.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No activities yet</h3>
            <p>
              {activeTab === 'friends' && "Add friends to see their activities!"}
              {activeTab === 'classes' && "Join a class to see classmate activities!"}
              {activeTab === 'me' && "Start practicing to create your first activity!"}
              {activeTab === 'all' && "No activities to show yet."}
            </p>
          </div>
        ) : (
          <>
            <div className="activities-list">
              {activities.map(activity => (
                <ActivityCard
                  key={activity.id}
                  activity={activity}
                  onDelete={handleDeleteActivity}
                />
              ))}
            </div>

            {hasMore && (
              <div className="load-more">
                <button
                  className="btn-load-more"
                  onClick={loadMore}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Load More'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SocialFeedPage;

