import React, { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import DataTable from '../shared/DataTable';
import Modal from '../shared/Modal';
import LoadingSpinner from '../shared/LoadingSpinner';
import SkillEditor from './SkillEditor';
import './ContentManagement.css';

const ContentManagement = () => {
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [skills, setSkills] = useState([]);
  const [filteredSkills, setFilteredSkills] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('all');
  const [gradeFilter, setGradeFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadSkills();
  }, []);

  useEffect(() => {
    filterSkills();
  }, [searchQuery, subjectFilter, gradeFilter, skills]);

  const loadSkills = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/admin/skills?limit=1000');
      
      if (response.data.success) {
        setSkills(response.data.skills || []);
      }
    } catch (error) {
      console.error('Error loading skills:', error);
      showNotification('Failed to load skills', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filterSkills = () => {
    let filtered = [...skills];

    // Apply subject filter
    if (subjectFilter !== 'all') {
      filtered = filtered.filter(skill => skill.subject_area === subjectFilter);
    }

    // Apply grade filter
    if (gradeFilter !== 'all') {
      filtered = filtered.filter(skill => skill.grade_level === parseInt(gradeFilter));
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(skill => 
        skill.name?.toLowerCase().includes(query) ||
        skill.description?.toLowerCase().includes(query) ||
        skill.id?.toString().includes(query)
      );
    }

    setFilteredSkills(filtered);
  };

  const handleCreateSkill = () => {
    setSelectedSkill(null);
    setShowCreateModal(true);
  };

  const handleEditSkill = (skill) => {
    setSelectedSkill(skill);
    setShowEditModal(true);
  };

  const handleDeleteSkill = (skill) => {
    setSelectedSkill(skill);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedSkill) return;

    try {
      setDeleting(true);
      const response = await api.delete(`/api/admin/skills/${selectedSkill.id}?admin_id=1`);
      
      if (response.data.success) {
        showNotification('Skill deleted successfully', 'success');
        setShowDeleteModal(false);
        setSelectedSkill(null);
        loadSkills();
      } else {
        showNotification(response.data.error || 'Failed to delete skill', 'error');
      }
    } catch (error) {
      console.error('Error deleting skill:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setDeleting(false);
    }
  };

  const handleSkillSaved = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setSelectedSkill(null);
    loadSkills();
  };

  const getDifficultyBadgeClass = (difficulty) => {
    const classes = {
      'beginner': 'difficulty-beginner',
      'intermediate': 'difficulty-intermediate',
      'advanced': 'difficulty-advanced'
    };
    return classes[difficulty] || 'difficulty-default';
  };

  const columns = [
    {
      key: 'id',
      label: 'ID',
      sortable: true,
      width: '80px'
    },
    {
      key: 'name',
      label: 'Skill Name',
      sortable: true,
      render: (skill) => (
        <div className="skill-cell">
          <span className="skill-name">{skill.name}</span>
          {skill.description && (
            <span className="skill-description">{skill.description}</span>
          )}
        </div>
      )
    },
    {
      key: 'subject_area',
      label: 'Subject',
      sortable: true,
      width: '150px',
      render: (skill) => (
        <span className="subject-badge">
          {skill.subject_area || 'N/A'}
        </span>
      )
    },
    {
      key: 'grade_level',
      label: 'Grade',
      sortable: true,
      width: '100px',
      render: (skill) => skill.grade_level ? `Grade ${skill.grade_level}` : 'All'
    },
    {
      key: 'difficulty',
      label: 'Difficulty',
      sortable: true,
      width: '130px',
      render: (skill) => (
        <span className={`difficulty-badge ${getDifficultyBadgeClass(skill.difficulty)}`}>
          {skill.difficulty || 'N/A'}
        </span>
      )
    },
    {
      key: 'question_count',
      label: 'Questions',
      sortable: true,
      width: '100px',
      render: (skill) => skill.question_count || 0
    },
    {
      key: 'actions',
      label: 'Actions',
      width: '120px',
      render: (skill) => (
        <div className="action-buttons">
          <button
            className="btn-action btn-edit"
            onClick={() => handleEditSkill(skill)}
            title="Edit skill"
          >
            ✏️
          </button>
          <button
            className="btn-action btn-delete"
            onClick={() => handleDeleteSkill(skill)}
            title="Delete skill"
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
    <div className="content-management">
      <div className="management-header">
        <div>
          <h2>Content Management</h2>
          <p className="subtitle">Manage skills, subjects, and learning content</p>
        </div>
        <button className="btn-primary" onClick={handleCreateSkill}>
          <span className="icon">➕</span>
          Create Skill
        </button>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="subjectFilter">Subject:</label>
          <select
            id="subjectFilter"
            value={subjectFilter}
            onChange={(e) => setSubjectFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Subjects</option>
            <option value="mathematics">Mathematics</option>
            <option value="science">Science</option>
            <option value="english">English</option>
            <option value="history">History</option>
            <option value="art">Art</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="gradeFilter">Grade:</label>
          <select
            id="gradeFilter"
            value={gradeFilter}
            onChange={(e) => setGradeFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Grades</option>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(grade => (
              <option key={grade} value={grade}>Grade {grade}</option>
            ))}
          </select>
        </div>

        <div className="results-count">
          {filteredSkills.length} {filteredSkills.length === 1 ? 'skill' : 'skills'}
        </div>
      </div>

      {/* Skills Table */}
      <div className="table-container">
        <DataTable
          data={filteredSkills}
          columns={columns}
          emptyMessage="No skills found"
        />
      </div>

      {/* Create Skill Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setSelectedSkill(null);
        }}
        title="Create New Skill"
        size="large"
      >
        <SkillEditor
          onSave={handleSkillSaved}
          onCancel={() => {
            setShowCreateModal(false);
            setSelectedSkill(null);
          }}
        />
      </Modal>

      {/* Edit Skill Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedSkill(null);
        }}
        title="Edit Skill"
        size="large"
      >
        <SkillEditor
          skill={selectedSkill}
          onSave={handleSkillSaved}
          onCancel={() => {
            setShowEditModal(false);
            setSelectedSkill(null);
          }}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedSkill(null);
        }}
        title="Delete Skill"
      >
        <div className="delete-confirmation">
          <p>
            Are you sure you want to delete the skill <strong>{selectedSkill?.name}</strong>?
          </p>
          <p className="warning-text">
            This action cannot be undone. All associated questions and student progress
            for this skill will be permanently deleted.
          </p>

          <div className="modal-actions">
            <button
              className="btn-secondary"
              onClick={() => {
                setShowDeleteModal(false);
                setSelectedSkill(null);
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
              {deleting ? 'Deleting...' : 'Delete Skill'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ContentManagement;

