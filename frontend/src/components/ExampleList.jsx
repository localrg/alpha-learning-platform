import { useState, useEffect } from 'react';
import axios from 'axios';
import InteractiveExample from './InteractiveExample';
import './ExampleList.css';

const ExampleList = ({ skillId, skillName }) => {
  const [examples, setExamples] = useState([]);
  const [selectedExample, setSelectedExample] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (skillId) {
      fetchExamples();
    }
  }, [skillId]);

  const fetchExamples = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.get(
        `http://localhost:5000/api/examples/skill/${skillId}`,
        config
      );

      setExamples(response.data.examples || []);
      
      // Auto-select first example if available
      if (response.data.examples && response.data.examples.length > 0) {
        setSelectedExample(response.data.examples[0]);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching examples:', err);
      setError('Failed to load interactive examples');
      setLoading(false);
    }
  };

  const handleExampleComplete = () => {
    // Refresh examples to update completion status
    fetchExamples();
  };

  if (loading) {
    return (
      <div className="example-list">
        <div className="loading">Loading interactive examples...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="example-list">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (examples.length === 0) {
    return (
      <div className="example-list">
        <div className="empty-state">
          <div className="empty-icon">🎮</div>
          <h3>No Interactive Examples Available</h3>
          <p>Interactive examples for {skillName} are coming soon!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="example-list">
      <div className="example-list-header">
        <h2>🎮 Interactive Examples</h2>
        <p className="example-list-subtitle">
          Explore and manipulate these examples to understand {skillName}
        </p>
      </div>

      {/* Current Example */}
      {selectedExample && (
        <div className="current-example">
          <InteractiveExample
            example={selectedExample}
            onComplete={handleExampleComplete}
          />
        </div>
      )}

      {/* Example Selection */}
      {examples.length > 1 && (
        <div className="example-selection">
          <h3 className="selection-title">All Examples ({examples.length})</h3>
          <div className="example-cards">
            {examples.map((example) => (
              <div
                key={example.id}
                className={`example-card ${selectedExample?.id === example.id ? 'active' : ''}`}
                onClick={() => setSelectedExample(example)}
              >
                <div className="card-header">
                  <h4 className="card-title">{example.title}</h4>
                  <span className={`card-badge ${example.difficulty}`}>
                    {example.difficulty}
                  </span>
                </div>
                
                {example.description && (
                  <p className="card-description">{example.description}</p>
                )}

                <div className="card-footer">
                  <span className="card-type">
                    {example.example_type.replace('_', ' ')}
                  </span>
                  {example.completed && (
                    <span className="card-completed">✓ Completed</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExampleList;

