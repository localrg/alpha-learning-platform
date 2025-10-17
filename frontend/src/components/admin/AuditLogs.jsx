import React, { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import DataTable from '../shared/DataTable';
import LoadingSpinner from '../shared/LoadingSpinner';
import './AuditLogs.css';

const AuditLogs = () => {
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [actionFilter, setActionFilter] = useState('all');
  const [entityFilter, setEntityFilter] = useState('all');
  const [dateRange, setDateRange] = useState('7');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadLogs();
  }, [actionFilter, entityFilter, dateRange]);

  useEffect(() => {
    filterLogs();
  }, [searchQuery, logs]);

  const loadLogs = async () => {
    try {
      setLoading(true);

      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - parseInt(dateRange));

      const params = new URLSearchParams({
        limit: 500
      });

      if (actionFilter !== 'all') {
        params.append('action_type', actionFilter);
      }

      if (entityFilter !== 'all') {
        params.append('entity_type', entityFilter);
      }

      if (dateRange !== 'all') {
        params.append('start_date', startDate.toISOString());
        params.append('end_date', endDate.toISOString());
      }

      const response = await api.get(`/api/admin/audit/logs?${params.toString()}`);
      
      if (response.data.success) {
        setLogs(response.data.logs || []);
      }
    } catch (error) {
      console.error('Error loading logs:', error);
      showNotification('Failed to load audit logs', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filterLogs = () => {
    let filtered = [...logs];

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(log => 
        log.description?.toLowerCase().includes(query) ||
        log.admin_name?.toLowerCase().includes(query) ||
        log.action_type?.toLowerCase().includes(query) ||
        log.entity_type?.toLowerCase().includes(query)
      );
    }

    setFilteredLogs(filtered);
  };

  const getActionIcon = (actionType) => {
    const icons = {
      'create': '➕',
      'update': '✏️',
      'delete': '🗑️',
      'login': '🔐',
      'logout': '🚪',
      'view': '👁️',
      'export': '📤',
      'import': '📥',
      'configure': '⚙️'
    };
    return icons[actionType] || '📌';
  };

  const getActionBadgeClass = (actionType) => {
    const classes = {
      'create': 'action-create',
      'update': 'action-update',
      'delete': 'action-delete',
      'login': 'action-login',
      'logout': 'action-logout',
      'view': 'action-view',
      'export': 'action-export',
      'import': 'action-import',
      'configure': 'action-configure'
    };
    return classes[actionType] || 'action-default';
  };

  const handleExport = () => {
    // Create CSV content
    const headers = ['Timestamp', 'Admin', 'Action', 'Entity', 'Description'];
    const rows = filteredLogs.map(log => [
      new Date(log.timestamp).toLocaleString(),
      log.admin_name || 'Unknown',
      log.action_type,
      log.entity_type,
      log.description || ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    showNotification('Audit logs exported successfully', 'success');
  };

  const columns = [
    {
      key: 'timestamp',
      label: 'Timestamp',
      sortable: true,
      width: '180px',
      render: (log) => new Date(log.timestamp).toLocaleString()
    },
    {
      key: 'admin_name',
      label: 'Admin',
      sortable: true,
      width: '150px',
      render: (log) => log.admin_name || 'System'
    },
    {
      key: 'action_type',
      label: 'Action',
      sortable: true,
      width: '120px',
      render: (log) => (
        <span className={`action-badge ${getActionBadgeClass(log.action_type)}`}>
          <span className="action-icon">{getActionIcon(log.action_type)}</span>
          {log.action_type}
        </span>
      )
    },
    {
      key: 'entity_type',
      label: 'Entity',
      sortable: true,
      width: '120px',
      render: (log) => (
        <span className="entity-badge">
          {log.entity_type}
        </span>
      )
    },
    {
      key: 'description',
      label: 'Description',
      sortable: true,
      render: (log) => (
        <div className="log-description">
          {log.description}
          {log.entity_id && (
            <span className="entity-id">ID: {log.entity_id}</span>
          )}
        </div>
      )
    },
    {
      key: 'ip_address',
      label: 'IP Address',
      sortable: true,
      width: '140px',
      render: (log) => log.ip_address || 'N/A'
    }
  ];

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="audit-logs">
      <div className="logs-header">
        <div>
          <h2>Audit Logs</h2>
          <p className="subtitle">Track all administrative actions and system changes</p>
        </div>
        <button className="btn-export" onClick={handleExport}>
          <span className="icon">📤</span>
          Export Logs
        </button>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="actionFilter">Action:</label>
          <select
            id="actionFilter"
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Actions</option>
            <option value="create">Create</option>
            <option value="update">Update</option>
            <option value="delete">Delete</option>
            <option value="login">Login</option>
            <option value="logout">Logout</option>
            <option value="configure">Configure</option>
            <option value="export">Export</option>
            <option value="import">Import</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="entityFilter">Entity:</label>
          <select
            id="entityFilter"
            value={entityFilter}
            onChange={(e) => setEntityFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Entities</option>
            <option value="user">User</option>
            <option value="skill">Skill</option>
            <option value="question">Question</option>
            <option value="setting">Setting</option>
            <option value="class">Class</option>
            <option value="assignment">Assignment</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="dateRange">Period:</label>
          <select
            id="dateRange"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="filter-select"
          >
            <option value="1">Last 24 hours</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="all">All time</option>
          </select>
        </div>

        <div className="results-count">
          {filteredLogs.length} {filteredLogs.length === 1 ? 'log' : 'logs'}
        </div>
      </div>

      {/* Logs Table */}
      <div className="table-container">
        <DataTable
          data={filteredLogs}
          columns={columns}
          emptyMessage="No audit logs found"
        />
      </div>
    </div>
  );
};

export default AuditLogs;

