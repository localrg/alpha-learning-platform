import React, { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import DataTable from '../shared/DataTable';
import Modal from '../shared/Modal';
import LoadingSpinner from '../shared/LoadingSpinner';
import UserEditor from './UserEditor';
import UserDetail from './UserDetail';
import './UserManagement.css';

const UserManagement = () => {
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [searchQuery, roleFilter, users]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/admin/users/search?limit=1000');
      
      if (response.data.success) {
        setUsers(response.data.users || []);
      }
    } catch (error) {
      console.error('Error loading users:', error);
      showNotification('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filterUsers = () => {
    let filtered = [...users];

    // Apply role filter
    if (roleFilter !== 'all') {
      filtered = filtered.filter(user => user.role === roleFilter);
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(user => 
        user.email?.toLowerCase().includes(query) ||
        user.username?.toLowerCase().includes(query) ||
        user.id?.toString().includes(query)
      );
    }

    setFilteredUsers(filtered);
  };

  const handleCreateUser = () => {
    setSelectedUser(null);
    setShowCreateModal(true);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleViewUser = async (user) => {
    try {
      const response = await api.get(`/api/admin/users/${user.id}`);
      if (response.data.success) {
        setSelectedUser(response.data.user);
        setShowDetailModal(true);
      }
    } catch (error) {
      console.error('Error loading user details:', error);
      showNotification('Failed to load user details', 'error');
    }
  };

  const handleDeleteUser = (user) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedUser) return;

    try {
      setDeleting(true);
      const response = await api.delete(`/api/admin/users/${selectedUser.id}?admin_id=1`);
      
      if (response.data.success) {
        showNotification('User deleted successfully', 'success');
        setShowDeleteModal(false);
        setSelectedUser(null);
        loadUsers();
      } else {
        showNotification(response.data.error || 'Failed to delete user', 'error');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setDeleting(false);
    }
  };

  const handleUserSaved = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setSelectedUser(null);
    loadUsers();
  };

  const getRoleBadgeClass = (role) => {
    const classes = {
      'student': 'role-badge-student',
      'teacher': 'role-badge-teacher',
      'parent': 'role-badge-parent',
      'admin': 'role-badge-admin'
    };
    return classes[role] || 'role-badge-default';
  };

  const getStatusBadgeClass = (isActive) => {
    return isActive ? 'status-badge-active' : 'status-badge-inactive';
  };

  const columns = [
    {
      key: 'id',
      label: 'ID',
      sortable: true,
      width: '80px'
    },
    {
      key: 'email',
      label: 'Email',
      sortable: true,
      render: (user) => (
        <div className="user-cell">
          <span className="user-email">{user.email}</span>
          {user.username && <span className="user-username">@{user.username}</span>}
        </div>
      )
    },
    {
      key: 'role',
      label: 'Role',
      sortable: true,
      width: '120px',
      render: (user) => (
        <span className={`role-badge ${getRoleBadgeClass(user.role)}`}>
          {user.role}
        </span>
      )
    },
    {
      key: 'created_at',
      label: 'Created',
      sortable: true,
      width: '150px',
      render: (user) => new Date(user.created_at).toLocaleDateString()
    },
    {
      key: 'is_active',
      label: 'Status',
      sortable: true,
      width: '100px',
      render: (user) => (
        <span className={`status-badge ${getStatusBadgeClass(user.is_active)}`}>
          {user.is_active ? 'Active' : 'Inactive'}
        </span>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      width: '180px',
      render: (user) => (
        <div className="action-buttons">
          <button
            className="btn-action btn-view"
            onClick={() => handleViewUser(user)}
            title="View details"
          >
            👁️
          </button>
          <button
            className="btn-action btn-edit"
            onClick={() => handleEditUser(user)}
            title="Edit user"
          >
            ✏️
          </button>
          <button
            className="btn-action btn-delete"
            onClick={() => handleDeleteUser(user)}
            title="Delete user"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="user-management">
      <div className="management-header">
        <div>
          <h2>User Management</h2>
          <p className="subtitle">Manage all platform users</p>
        </div>
        <button className="btn-primary" onClick={handleCreateUser}>
          <span className="icon">➕</span>
          Create User
        </button>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by email, username, or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="roleFilter">Role:</label>
          <select
            id="roleFilter"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Roles</option>
            <option value="student">Students</option>
            <option value="teacher">Teachers</option>
            <option value="parent">Parents</option>
            <option value="admin">Admins</option>
          </select>
        </div>

        <div className="results-count">
          {filteredUsers.length} {filteredUsers.length === 1 ? 'user' : 'users'}
        </div>
      </div>

      {/* User Table */}
      <div className="table-container">
        <DataTable
          data={filteredUsers}
          columns={columns}
          emptyMessage="No users found"
        />
      </div>

      {/* Create User Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setSelectedUser(null);
        }}
        title="Create New User"
        size="large"
      >
        <UserEditor
          onSave={handleUserSaved}
          onCancel={() => {
            setShowCreateModal(false);
            setSelectedUser(null);
          }}
        />
      </Modal>

      {/* Edit User Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedUser(null);
        }}
        title="Edit User"
        size="large"
      >
        <UserEditor
          user={selectedUser}
          onSave={handleUserSaved}
          onCancel={() => {
            setShowEditModal(false);
            setSelectedUser(null);
          }}
        />
      </Modal>

      {/* User Detail Modal */}
      <Modal
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedUser(null);
        }}
        title="User Details"
        size="large"
      >
        {selectedUser && <UserDetail user={selectedUser} />}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedUser(null);
        }}
        title="Delete User"
      >
        <div className="delete-confirmation">
          <p>
            Are you sure you want to delete the user <strong>{selectedUser?.email}</strong>?
          </p>
          <p className="warning-text">
            This action cannot be undone. All user data, including progress, achievements,
            and activity history will be permanently deleted.
          </p>

          <div className="modal-actions">
            <button
              className="btn-secondary"
              onClick={() => {
                setShowDeleteModal(false);
                setSelectedUser(null);
              }}
              disabled={deleting}
            >
              Cancel
            </button>
            <button
              className="btn-danger"
              onClick={confirmDelete}
              disabled={deleting}
            >
              {deleting ? 'Deleting...' : 'Delete User'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default UserManagement;

