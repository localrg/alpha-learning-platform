import { useState, useEffect } from 'react';
import axios from 'axios';
import './ResourceLibrary.css';

export default function ResourceLibrary() {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    type: '',
    grade: '',
    difficulty: '',
    search: ''
  });
  const [availableFilters, setAvailableFilters] = useState({
    types: [],
    grades: [],
    difficulties: []
  });

  useEffect(() => {
    loadResources();
  }, [filters]);

  const loadResources = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.type) params.append('type', filters.type);
      if (filters.grade) params.append('grade', filters.grade);
      if (filters.difficulty) params.append('difficulty', filters.difficulty);
      if (filters.search) params.append('search', filters.search);

      const response = await axios.get(`/api/resources?${params.toString()}`);
      setResources(response.data.resources);
      setAvailableFilters(response.data.filters);
    } catch (error) {
      console.error('Error loading resources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (resource) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `/api/resources/${resource.id}/download`,
        { download_method: 'direct' },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Open download URL in new tab
      window.open(response.data.download_url, '_blank');
    } catch (error) {
      console.error('Error downloading resource:', error);
      alert('Error downloading resource. Please try again.');
    }
  };

  const clearFilters = () => {
    setFilters({
      type: '',
      grade: '',
      difficulty: '',
      search: ''
    });
  };

  const getResourceTypeIcon = (type) => {
    switch (type) {
      case 'worksheet':
        return '📝';
      case 'reference':
        return '📚';
      case 'practice':
        return '✏️';
      case 'study_guide':
        return '📖';
      case 'answer_key':
        return '✓';
      default:
        return '📄';
    }
  };

  const getResourceTypeColor = (type) => {
    switch (type) {
      case 'worksheet':
        return 'blue';
      case 'reference':
        return 'green';
      case 'practice':
        return 'purple';
      case 'study_guide':
        return 'orange';
      case 'answer_key':
        return 'gray';
      default:
        return 'gray';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'green';
      case 'medium':
        return 'orange';
      case 'hard':
        return 'red';
      default:
        return 'gray';
    }
  };

  const formatFileSize = (sizeKb) => {
    if (sizeKb < 1024) {
      return `${sizeKb} KB`;
    } else {
      return `${(sizeKb / 1024).toFixed(1)} MB`;
    }
  };

  return (
    <div className="resource-library">
      {/* Header */}
      <div className="library-header">
        <h1>📚 Resource Library</h1>
        <p>Download worksheets, reference guides, and practice materials</p>
      </div>

      {/* Filters */}
      <div className="library-filters">
        <div className="filter-group">
          <label>Search</label>
          <input
            type="text"
            placeholder="Search resources..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="filter-input"
          />
        </div>

        <div className="filter-group">
          <label>Type</label>
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
            className="filter-select"
          >
            <option value="">All Types</option>
            {availableFilters.types.map((type) => (
              <option key={type} value={type}>
                {type.replace('_', ' ')}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Grade</label>
          <select
            value={filters.grade}
            onChange={(e) => setFilters({ ...filters, grade: e.target.value })}
            className="filter-select"
          >
            <option value="">All Grades</option>
            {availableFilters.grades.map((grade) => (
              <option key={grade} value={grade}>
                Grade {grade}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Difficulty</label>
          <select
            value={filters.difficulty}
            onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
            className="filter-select"
          >
            <option value="">All Levels</option>
            {availableFilters.difficulties.map((difficulty) => (
              <option key={difficulty} value={difficulty}>
                {difficulty}
              </option>
            ))}
          </select>
        </div>

        {(filters.type || filters.grade || filters.difficulty || filters.search) && (
          <button onClick={clearFilters} className="clear-filters-btn">
            Clear Filters
          </button>
        )}
      </div>

      {/* Results Count */}
      <div className="results-count">
        {loading ? 'Loading...' : `${resources.length} resources found`}
      </div>

      {/* Resources Grid */}
      {loading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading resources...</p>
        </div>
      ) : resources.length === 0 ? (
        <div className="no-resources">
          <p>No resources found matching your filters.</p>
          <button onClick={clearFilters} className="clear-filters-btn">
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="resources-grid">
          {resources.map((resource) => (
            <div key={resource.id} className="resource-card">
              {/* Thumbnail */}
              <div className="resource-thumbnail">
                {resource.thumbnail_url ? (
                  <img src={resource.thumbnail_url} alt={resource.title} />
                ) : (
                  <div className="thumbnail-placeholder">
                    <span className="resource-icon">
                      {getResourceTypeIcon(resource.resource_type)}
                    </span>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="resource-content">
                <div className="resource-header">
                  <span className={`resource-type-badge ${getResourceTypeColor(resource.resource_type)}`}>
                    {getResourceTypeIcon(resource.resource_type)} {resource.resource_type.replace('_', ' ')}
                  </span>
                  <span className={`difficulty-badge ${getDifficultyColor(resource.difficulty)}`}>
                    {resource.difficulty}
                  </span>
                </div>

                <h3 className="resource-title">{resource.title}</h3>
                <p className="resource-description">{resource.description}</p>

                <div className="resource-meta">
                  <span className="meta-item">📊 Grade {resource.grade_level}</span>
                  <span className="meta-item">📁 {resource.file_type.toUpperCase()}</span>
                  <span className="meta-item">💾 {formatFileSize(resource.file_size_kb)}</span>
                  <span className="meta-item">⬇️ {resource.download_count} downloads</span>
                </div>

                {resource.tags && resource.tags.length > 0 && (
                  <div className="resource-tags">
                    {resource.tags.slice(0, 3).map((tag, index) => (
                      <span key={index} className="tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="resource-actions">
                <button
                  onClick={() => handleDownload(resource)}
                  className="download-btn"
                >
                  ⬇️ Download
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

