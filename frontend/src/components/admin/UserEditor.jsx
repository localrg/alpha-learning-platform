import React, { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import './UserEditor.css';

const UserEditor = ({ user, onSave, onCancel }) => {
  const { showNotification } = useNotification();
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    role: 'student',
    is_active: true,
    // Student-specific fields
    grade: '',
    // Teacher-specific fields
    subject: '',
    // Parent-specific fields
    phone: ''
  });

  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || '',
        username: user.username || '',
        password: '', // Never pre-fill password
        role: user.role || 'student',
        is_active: user.is_active !== undefined ? user.is_active : true,
        grade: user.grade || '',
        subject: user.subject || '',
        phone: user.phone || ''
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.email.trim()) {
      showNotification('Email is required', 'error');
      return;
    }

    if (!user && !formData.password) {
      showNotification('Password is required for new users', 'error');
      return;
    }

    try {
      setSaving(true);

      const payload = {
        email: formData.email.trim(),
        username: formData.username.trim() || null,
        role: formData.role,
        is_active: formData.is_active,
        admin_id: 1 // In production, get from auth context
      };

      // Add password only if provided
      if (formData.password) {
        payload.password = formData.password;
      }

      // Add role-specific fields
      if (formData.role === 'student' && formData.grade) {
        payload.grade = parseInt(formData.grade);
      }

      if (formData.role === 'teacher' && formData.subject) {
        payload.subject = formData.subject.trim();
      }

      if (formData.role === 'parent' && formData.phone) {
        payload.phone = formData.phone.trim();
      }

      let response;
      if (user) {
        // Update existing user
        response = await api.put(`/api/admin/users/${user.id}`, payload);
      } else {
        // Create new user
        response = await api.post('/api/admin/users', payload);
      }

      if (response.data.success) {
        showNotification(
          user ? 'User updated successfully!' : 'User created successfully!',
          'success'
        );
        onSave();
      } else {
        showNotification(response.data.error || 'Operation failed', 'error');
      }
    } catch (error) {
      console.error('Error saving user:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="user-editor">
      <div className="form-section">
        <h3>Basic Information</h3>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="user@example.com"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Optional username"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="password">
              Password {user ? '(leave blank to keep current)' : '*'}
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder={user ? 'Enter new password' : 'Enter password'}
              required={!user}
            />
            <small className="form-hint">
              Minimum 6 characters
            </small>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="role">Role *</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
              <option value="parent">Parent</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
              />
              <span>Active Account</span>
            </label>
            <small className="form-hint">
              Inactive accounts cannot log in
            </small>
          </div>
        </div>
      </div>

      {/* Role-specific fields */}
      {formData.role === 'student' && (
        <div className="form-section">
          <h3>Student Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="grade">Grade Level</label>
              <select
                id="grade"
                name="grade"
                value={formData.grade}
                onChange={handleChange}
              >
                <option value="">Select grade</option>
                <option value="1">1st Grade</option>
                <option value="2">2nd Grade</option>
                <option value="3">3rd Grade</option>
                <option value="4">4th Grade</option>
                <option value="5">5th Grade</option>
                <option value="6">6th Grade</option>
                <option value="7">7th Grade</option>
                <option value="8">8th Grade</option>
                <option value="9">9th Grade</option>
                <option value="10">10th Grade</option>
                <option value="11">11th Grade</option>
                <option value="12">12th Grade</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {formData.role === 'teacher' && (
        <div className="form-section">
          <h3>Teacher Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="subject">Subject/Specialty</label>
              <input
                type="text"
                id="subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                placeholder="e.g., Mathematics, Science"
              />
            </div>
          </div>
        </div>
      )}

      {formData.role === 'parent' && (
        <div className="form-section">
          <h3>Parent Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="(555) 123-4567"
              />
            </div>
          </div>
        </div>
      )}

      <div className="form-actions">
        <button
          type="button"
          className="btn-secondary"
          onClick={onCancel}
          disabled={saving}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={saving}
        >
          {saving ? 'Saving...' : user ? 'Update User' : 'Create User'}
        </button>
      </div>
    </form>
  );
};

export default UserEditor;

