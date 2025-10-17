import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import './ParentSettings.css';

const ParentSettings = () => {
  const { user } = useAuth();
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [parentProfile, setParentProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');

  // Profile form state
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');

  // Notification preferences state
  const [notificationPrefs, setNotificationPrefs] = useState({
    email_notifications: true,
    sms_notifications: false,
    daily_summary: true,
    weekly_report: true,
    achievement_alerts: true,
    struggle_alerts: true,
    assignment_reminders: true,
    teacher_messages: true,
    goal_updates: true,
    low_activity_alerts: true
  });

  useEffect(() => {
    loadParentProfile();
  }, [user]);

  const loadParentProfile = async () => {
    if (!user) return;

    try {
      setLoading(true);

      const response = await api.get(`/api/parents/profile?user_id=${user.id}`);
      if (response.data.success) {
        const profile = response.data.parent;
        setParentProfile(profile);
        setName(profile.name || '');
        setPhone(profile.phone || '');

        // Load notification preferences
        if (profile.notification_preferences) {
          setNotificationPrefs({
            ...notificationPrefs,
            ...profile.notification_preferences
          });
        }
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      showNotification('Failed to load profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();

    if (!name.trim()) {
      showNotification('Name is required', 'error');
      return;
    }

    try {
      setSaving(true);

      const response = await api.put(`/api/parents/profile/${parentProfile.id}`, {
        name: name.trim(),
        phone: phone.trim()
      });

      if (response.data.success) {
        showNotification('Profile updated successfully!', 'success');
        setParentProfile(response.data.parent);
      } else {
        showNotification(response.data.error || 'Failed to update profile', 'error');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveNotifications = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);

      const response = await api.put(`/api/parents/notifications/${parentProfile.id}`, {
        preferences: notificationPrefs
      });

      if (response.data.success) {
        showNotification('Notification preferences updated!', 'success');
      } else {
        showNotification(response.data.error || 'Failed to update preferences', 'error');
      }
    } catch (error) {
      console.error('Error updating notifications:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleNotificationToggle = (key) => {
    setNotificationPrefs({
      ...notificationPrefs,
      [key]: !notificationPrefs[key]
    });
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="parent-settings">
      <div className="settings-header">
        <h2>Account Settings</h2>
        <p className="subtitle">Manage your profile and notification preferences</p>
      </div>

      <div className="settings-tabs">
        <button
          className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <span className="icon">👤</span>
          Profile
        </button>
        <button
          className={`tab-btn ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          <span className="icon">🔔</span>
          Notifications
        </button>
        <button
          className={`tab-btn ${activeTab === 'privacy' ? 'active' : ''}`}
          onClick={() => setActiveTab('privacy')}
        >
          <span className="icon">🔒</span>
          Privacy
        </button>
      </div>

      <div className="settings-content">
        {activeTab === 'profile' && (
          <div className="settings-section">
            <h3>Profile Information</h3>
            <p className="section-description">
              Update your personal information and contact details.
            </p>

            <form onSubmit={handleSaveProfile} className="settings-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    value={user?.email || ''}
                    disabled
                    className="disabled-input"
                  />
                  <small className="form-hint">Email cannot be changed</small>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="name">Full Name *</label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your full name"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="phone">Phone Number</label>
                  <input
                    type="tel"
                    id="phone"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="(555) 123-4567"
                  />
                  <small className="form-hint">For SMS notifications (optional)</small>
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="settings-section">
            <h3>Notification Preferences</h3>
            <p className="section-description">
              Choose how you want to be notified about your children's progress and activities.
            </p>

            <form onSubmit={handleSaveNotifications} className="settings-form">
              <div className="notification-group">
                <h4>Delivery Methods</h4>
                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Email Notifications</strong>
                    <p>Receive notifications via email</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.email_notifications}
                      onChange={() => handleNotificationToggle('email_notifications')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>

                <div className="notification-item">
                  <div className="notification-info">
                    <strong>SMS Notifications</strong>
                    <p>Receive notifications via text message</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.sms_notifications}
                      onChange={() => handleNotificationToggle('sms_notifications')}
                      disabled={!phone}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="notification-group">
                <h4>Progress Updates</h4>
                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Daily Summary</strong>
                    <p>Daily recap of your children's learning activities</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.daily_summary}
                      onChange={() => handleNotificationToggle('daily_summary')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>

                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Weekly Report</strong>
                    <p>Comprehensive weekly progress report</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.weekly_report}
                      onChange={() => handleNotificationToggle('weekly_report')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>

                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Goal Updates</strong>
                    <p>Notifications when goals are achieved or updated</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.goal_updates}
                      onChange={() => handleNotificationToggle('goal_updates')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="notification-group">
                <h4>Alerts</h4>
                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Achievement Alerts</strong>
                    <p>Notify when your child earns achievements or levels up</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.achievement_alerts}
                      onChange={() => handleNotificationToggle('achievement_alerts')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>

                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Struggle Alerts</strong>
                    <p>Notify when your child is struggling with a topic</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.struggle_alerts}
                      onChange={() => handleNotificationToggle('struggle_alerts')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>

                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Low Activity Alerts</strong>
                    <p>Notify when your child hasn't been active recently</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.low_activity_alerts}
                      onChange={() => handleNotificationToggle('low_activity_alerts')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>

                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Assignment Reminders</strong>
                    <p>Reminders about upcoming assignments and deadlines</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.assignment_reminders}
                      onChange={() => handleNotificationToggle('assignment_reminders')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="notification-group">
                <h4>Communication</h4>
                <div className="notification-item">
                  <div className="notification-info">
                    <strong>Teacher Messages</strong>
                    <p>Notify when teachers send you messages</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notificationPrefs.teacher_messages}
                      onChange={() => handleNotificationToggle('teacher_messages')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Preferences'}
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className="settings-section">
            <h3>Privacy & Security</h3>
            <p className="section-description">
              Manage your privacy settings and account security.
            </p>

            <div className="privacy-section">
              <h4>Data Privacy</h4>
              <div className="privacy-item">
                <div className="privacy-info">
                  <strong>Data Collection</strong>
                  <p>
                    We collect data about your children's learning progress to provide
                    personalized insights and recommendations. All data is encrypted and
                    stored securely.
                  </p>
                </div>
              </div>

              <div className="privacy-item">
                <div className="privacy-info">
                  <strong>Data Sharing</strong>
                  <p>
                    Your children's data is only shared with their assigned teachers and
                    administrators. We never share data with third parties without your
                    explicit consent.
                  </p>
                </div>
              </div>
            </div>

            <div className="privacy-section">
              <h4>Account Security</h4>
              <div className="privacy-item">
                <div className="privacy-info">
                  <strong>Password</strong>
                  <p>Last changed: Never</p>
                </div>
                <button className="btn-secondary">Change Password</button>
              </div>

              <div className="privacy-item">
                <div className="privacy-info">
                  <strong>Two-Factor Authentication</strong>
                  <p>Add an extra layer of security to your account</p>
                </div>
                <button className="btn-secondary">Enable 2FA</button>
              </div>
            </div>

            <div className="privacy-section danger-zone">
              <h4>Danger Zone</h4>
              <div className="privacy-item">
                <div className="privacy-info">
                  <strong>Delete Account</strong>
                  <p>
                    Permanently delete your account and all associated data. This action
                    cannot be undone.
                  </p>
                </div>
                <button className="btn-danger">Delete Account</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ParentSettings;

