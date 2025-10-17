import React, { useState, useEffect } from 'react';
import { useNotification } from '../../contexts/NotificationContext';
import api from '../../services/api';
import './SkillEditor.css';

const SkillEditor = ({ skill, onSave, onCancel }) => {
  const { showNotification } = useNotification();
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    subject_area: 'mathematics',
    grade_level: '',
    difficulty: 'beginner',
    prerequisites: '',
    learning_objectives: ''
  });

  useEffect(() => {
    if (skill) {
      setFormData({
        name: skill.name || '',
        description: skill.description || '',
        subject_area: skill.subject_area || 'mathematics',
        grade_level: skill.grade_level?.toString() || '',
        difficulty: skill.difficulty || 'beginner',
        prerequisites: skill.prerequisites || '',
        learning_objectives: skill.learning_objectives || ''
      });
    }
  }, [skill]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      showNotification('Skill name is required', 'error');
      return;
    }

    if (!formData.subject_area) {
      showNotification('Subject area is required', 'error');
      return;
    }

    try {
      setSaving(true);

      const payload = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        subject_area: formData.subject_area,
        grade_level: formData.grade_level ? parseInt(formData.grade_level) : null,
        difficulty: formData.difficulty,
        prerequisites: formData.prerequisites.trim() || null,
        learning_objectives: formData.learning_objectives.trim() || null,
        admin_id: 1 // In production, get from auth context
      };

      let response;
      if (skill) {
        // Update existing skill
        response = await api.put(`/api/admin/skills/${skill.id}`, payload);
      } else {
        // Create new skill
        response = await api.post('/api/admin/skills', payload);
      }

      if (response.data.success) {
        showNotification(
          skill ? 'Skill updated successfully!' : 'Skill created successfully!',
          'success'
        );
        onSave();
      } else {
        showNotification(response.data.error || 'Operation failed', 'error');
      }
    } catch (error) {
      console.error('Error saving skill:', error);
      showNotification('An error occurred', 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="skill-editor">
      <div className="form-section">
        <h3>Basic Information</h3>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="name">Skill Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., Addition with Regrouping"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Brief description of the skill"
              rows={3}
            />
          </div>
        </div>

        <div className="form-row-split">
          <div className="form-group">
            <label htmlFor="subject_area">Subject Area *</label>
            <select
              id="subject_area"
              name="subject_area"
              value={formData.subject_area}
              onChange={handleChange}
              required
            >
              <option value="mathematics">Mathematics</option>
              <option value="science">Science</option>
              <option value="english">English</option>
              <option value="history">History</option>
              <option value="art">Art</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="grade_level">Grade Level</label>
            <select
              id="grade_level"
              name="grade_level"
              value={formData.grade_level}
              onChange={handleChange}
            >
              <option value="">All Grades</option>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(grade => (
                <option key={grade} value={grade}>Grade {grade}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="difficulty">Difficulty Level *</label>
            <select
              id="difficulty"
              name="difficulty"
              value={formData.difficulty}
              onChange={handleChange}
              required
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>Learning Details</h3>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="prerequisites">Prerequisites</label>
            <textarea
              id="prerequisites"
              name="prerequisites"
              value={formData.prerequisites}
              onChange={handleChange}
              placeholder="Skills or knowledge required before learning this skill"
              rows={3}
            />
            <small className="form-hint">
              List any skills students should master before attempting this one
            </small>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="learning_objectives">Learning Objectives</label>
            <textarea
              id="learning_objectives"
              name="learning_objectives"
              value={formData.learning_objectives}
              onChange={handleChange}
              placeholder="What students will be able to do after mastering this skill"
              rows={4}
            />
            <small className="form-hint">
              Define clear, measurable learning outcomes
            </small>
          </div>
        </div>
      </div>

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
          {saving ? 'Saving...' : skill ? 'Update Skill' : 'Create Skill'}
        </button>
      </div>
    </form>
  );
};

export default SkillEditor;

