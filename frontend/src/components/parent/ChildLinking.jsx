import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import Modal from '../shared/Modal';
import LoadingSpinner from '../shared/LoadingSpinner';
import EmptyState from '../shared/EmptyState';
import './ChildLinking.css';

const ChildLinking = () => {
  const { user } = useAuth();
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [children, setChildren] = useState([]);
  const [parentProfile, setParentProfile] = useState(null);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [linkMethod, setLinkMethod] = useState('code'); // 'code' or 'email'
  const [inviteCode, setInviteCode] = useState('');
  const [studentEmail, setStudentEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showRemoveModal, setShowRemoveModal] = useState(false);
  const [childToRemove, setChildToRemove] = useState(null);

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    if (!user) return;

    try {
      setLoading(true);

      // Get parent profile
      const profileResponse = await api.get(`/api/parents/profile?user_id=${user.id}`);
      if (profileResponse.data.success) {
        setParentProfile(profileResponse.data.parent);

        // Get linked children
        const childrenResponse = await api.get(`/api/parents/children?parent_id=${profileResponse.data.parent.id}`);
        if (childrenResponse.data.success) {
          setChildren(childrenResponse.data.children || []);
        }
      }
    } catch (error) {
      console.error('Error loading data:', error);
      showNotification('Failed to load children', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLinkChild = async () => {
    if (!parentProfile) return;

    if (linkMethod === 'code' && !inviteCode.trim()) {
      showNotification('Please enter an invite code', 'error');
      return;
    }

    if (linkMethod === 'email' && !studentEmail.trim()) {
      showNotification('Please enter student email', 'error');
      return;
    }

    try {
      setSubmitting(true);

      if (linkMethod === 'code') {
        const response = await api.post('/api/parents/link-child', {
          parent_id: parentProfile.id,
          invite_code: inviteCode.trim()
        });

        if (response.data.success) {
          showNotification('Child linked successfully!', 'success');
          setInviteCode('');
          setShowLinkModal(false);
          loadData();
        } else {
          showNotification(response.data.error || 'Failed to link child', 'error');
        }
      } else {
        const response = await api.post('/api/parents/request-link', {
          parent_id: parentProfile.id,
          student_email: studentEmail.trim()
        });

        if (response.data.success) {
          showNotification('Link request sent! Waiting for student approval.', 'success');
          setStudentEmail('');
          setShowLinkModal(false);
        } else {
          showNotification(response.data.error || 'Failed to send request', 'error');
        }
      }
    } catch (error) {
      console.error('Error linking child:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemoveChild = async () => {
    if (!parentProfile || !childToRemove) return;

    try {
      setSubmitting(true);

      const response = await api.delete(
        `/api/parents/children/${childToRemove.id}?parent_id=${parentProfile.id}`
      );

      if (response.data.success) {
        showNotification('Child removed successfully', 'success');
        setShowRemoveModal(false);
        setChildToRemove(null);
        loadData();
      } else {
        showNotification(response.data.error || 'Failed to remove child', 'error');
      }
    } catch (error) {
      console.error('Error removing child:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const openRemoveModal = (child) => {
    setChildToRemove(child);
    setShowRemoveModal(true);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="child-linking">
      <div className="child-linking-header">
        <div>
          <h2>Linked Children</h2>
          <p className="subtitle">Manage your linked student accounts</p>
        </div>
        <button className="btn-primary" onClick={() => setShowLinkModal(true)}>
          <span className="icon">➕</span>
          Link Child
        </button>
      </div>

      {children.length === 0 ? (
        <EmptyState
          icon="👨‍👩‍👧‍👦"
          title="No Children Linked"
          message="Link your child's account to view their progress and communicate with teachers."
          actionLabel="Link a Child"
          onAction={() => setShowLinkModal(true)}
        />
      ) : (
        <div className="children-grid">
          {children.map((child) => (
            <div key={child.id} className="child-card">
              <div className="child-avatar">
                {child.name?.charAt(0).toUpperCase() || 'S'}
              </div>
              <div className="child-info">
                <h3>{child.name}</h3>
                <p className="child-email">{child.email}</p>
                <div className="child-stats">
                  <div className="stat">
                    <span className="stat-label">Grade</span>
                    <span className="stat-value">{child.grade || 'N/A'}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Level</span>
                    <span className="stat-value">{child.level || 1}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">XP</span>
                    <span className="stat-value">{child.xp || 0}</span>
                  </div>
                </div>
                <div className="child-meta">
                  <span className="linked-date">
                    Linked {new Date(child.linked_at || Date.now()).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <button
                className="btn-remove"
                onClick={() => openRemoveModal(child)}
                title="Remove child"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Link Child Modal */}
      <Modal
        isOpen={showLinkModal}
        onClose={() => {
          setShowLinkModal(false);
          setInviteCode('');
          setStudentEmail('');
        }}
        title="Link Child Account"
      >
        <div className="link-modal-content">
          <div className="link-method-selector">
            <button
              className={`method-btn ${linkMethod === 'code' ? 'active' : ''}`}
              onClick={() => setLinkMethod('code')}
            >
              <span className="icon">🔑</span>
              Invite Code
            </button>
            <button
              className={`method-btn ${linkMethod === 'email' ? 'active' : ''}`}
              onClick={() => setLinkMethod('email')}
            >
              <span className="icon">📧</span>
              Email Request
            </button>
          </div>

          {linkMethod === 'code' ? (
            <div className="link-form">
              <p className="form-description">
                Enter the invite code provided by your child's student account.
              </p>
              <div className="form-group">
                <label htmlFor="inviteCode">Invite Code</label>
                <input
                  type="text"
                  id="inviteCode"
                  value={inviteCode}
                  onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  className="invite-code-input"
                />
              </div>
            </div>
          ) : (
            <div className="link-form">
              <p className="form-description">
                Send a link request to your child's email. They will need to approve the request.
              </p>
              <div className="form-group">
                <label htmlFor="studentEmail">Student Email</label>
                <input
                  type="email"
                  id="studentEmail"
                  value={studentEmail}
                  onChange={(e) => setStudentEmail(e.target.value)}
                  placeholder="student@example.com"
                />
              </div>
            </div>
          )}

          <div className="modal-actions">
            <button
              className="btn-secondary"
              onClick={() => {
                setShowLinkModal(false);
                setInviteCode('');
                setStudentEmail('');
              }}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              className="btn-primary"
              onClick={handleLinkChild}
              disabled={submitting}
            >
              {submitting ? 'Processing...' : linkMethod === 'code' ? 'Link Child' : 'Send Request'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Remove Child Modal */}
      <Modal
        isOpen={showRemoveModal}
        onClose={() => {
          setShowRemoveModal(false);
          setChildToRemove(null);
        }}
        title="Remove Child Link"
      >
        <div className="remove-modal-content">
          <p>
            Are you sure you want to remove <strong>{childToRemove?.name}</strong> from your linked children?
          </p>
          <p className="warning-text">
            You will no longer be able to view their progress or communicate with their teachers.
            You can re-link them later using a new invite code.
          </p>

          <div className="modal-actions">
            <button
              className="btn-secondary"
              onClick={() => {
                setShowRemoveModal(false);
                setChildToRemove(null);
              }}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              className="btn-danger"
              onClick={handleRemoveChild}
              disabled={submitting}
            >
              {submitting ? 'Removing...' : 'Remove Child'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ChildLinking;

