import React, { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import './SystemSettings.css';

const SystemSettings = () => {
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeCategory, setActiveCategory] = useState('general');
  const [settings, setSettings] = useState({});
  const [formData, setFormData] = useState({});

  useEffect(() => {
    loadSettings();
  }, [activeCategory]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/admin/settings?category=${activeCategory}`);
      
      if (response.data.success) {
        const settingsData = response.data.settings || [];
        const settingsObj = {};
        const formObj = {};
        
        settingsData.forEach(setting => {
          settingsObj[setting.key] = setting;
          formObj[setting.key] = setting.value;
        });
        
        setSettings(settingsObj);
        setFormData(formObj);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      showNotification('Failed to load settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (key, value) => {
    setFormData({
      ...formData,
      [key]: value
    });
  };

  const handleSave = async (key) => {
    try {
      setSaving(true);
      
      const response = await api.put(`/api/admin/settings/${key}`, {
        value: formData[key],
        admin_id: 1 // In production, get from auth context
      });

      if (response.data.success) {
        showNotification('Setting updated successfully!', 'success');
        loadSettings();
      } else {
        showNotification(response.data.error || 'Failed to update setting', 'error');
      }
    } catch (error) {
      console.error('Error saving setting:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAll = async () => {
    try {
      setSaving(true);
      
      const updates = Object.keys(formData).map(key => 
        api.put(`/api/admin/settings/${key}`, {
          value: formData[key],
          admin_id: 1
        })
      );

      await Promise.all(updates);
      
      showNotification('All settings updated successfully!', 'success');
      loadSettings();
    } catch (error) {
      console.error('Error saving settings:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSaving(false);
    }
  };

  const renderSettingInput = (key, setting) => {
    const value = formData[key] ?? '';

    // Determine input type based on value or key
    if (typeof value === 'boolean' || key.includes('enable') || key.includes('allow')) {
      return (
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={value === true || value === 'true'}
            onChange={(e) => handleChange(key, e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </label>
      );
    }

    if (typeof value === 'number' || key.includes('max') || key.includes('min') || key.includes('limit')) {
      return (
        <input
          type="number"
          value={value}
          onChange={(e) => handleChange(key, parseInt(e.target.value) || 0)}
          className="setting-input"
        />
      );
    }

    if (key.includes('email') || key.includes('mail')) {
      return (
        <input
          type="email"
          value={value}
          onChange={(e) => handleChange(key, e.target.value)}
          className="setting-input"
        />
      );
    }

    if (key.includes('url') || key.includes('link')) {
      return (
        <input
          type="url"
          value={value}
          onChange={(e) => handleChange(key, e.target.value)}
          className="setting-input"
        />
      );
    }

    // Default to text input
    return (
      <input
        type="text"
        value={value}
        onChange={(e) => handleChange(key, e.target.value)}
        className="setting-input"
      />
    );
  };

  const categories = [
    { id: 'general', name: 'General', icon: '⚙️' },
    { id: 'security', name: 'Security', icon: '🔒' },
    { id: 'notifications', name: 'Notifications', icon: '🔔' },
    { id: 'learning', name: 'Learning', icon: '📚' },
    { id: 'gamification', name: 'Gamification', icon: '🎮' },
    { id: 'integrations', name: 'Integrations', icon: '🔌' }
  ];

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="system-settings">
      <div className="settings-header">
        <div>
          <h2>System Settings</h2>
          <p className="subtitle">Configure platform-wide settings and preferences</p>
        </div>
        <button 
          className="btn-primary" 
          onClick={handleSaveAll}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save All Changes'}
        </button>
      </div>

      <div className="settings-container">
        {/* Category Sidebar */}
        <div className="settings-sidebar">
          {categories.map(category => (
            <button
              key={category.id}
              className={`category-btn ${activeCategory === category.id ? 'active' : ''}`}
              onClick={() => setActiveCategory(category.id)}
            >
              <span className="category-icon">{category.icon}</span>
              <span className="category-name">{category.name}</span>
            </button>
          ))}
        </div>

        {/* Settings Panel */}
        <div className="settings-panel">
          {Object.keys(settings).length === 0 ? (
            <div className="empty-settings">
              <p>No settings found for this category.</p>
              <p className="hint">Settings will appear here once they are configured in the system.</p>
            </div>
          ) : (
            <div className="settings-list">
              {Object.entries(settings).map(([key, setting]) => (
                <div key={key} className="setting-item">
                  <div className="setting-info">
                    <div className="setting-header">
                      <span className="setting-key">{key.replace(/_/g, ' ').toUpperCase()}</span>
                      <button
                        className="btn-save-single"
                        onClick={() => handleSave(key)}
                        disabled={saving}
                      >
                        Save
                      </button>
                    </div>
                    {setting.description && (
                      <p className="setting-description">{setting.description}</p>
                    )}
                  </div>
                  <div className="setting-control">
                    {renderSettingInput(key, setting)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemSettings;

