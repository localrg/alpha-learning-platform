import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useFetch, useMutation } from '../../hooks/useApi';
import { assignmentAPI, teacherAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import { useNotification } from '../../contexts/NotificationContext';

const CreateAssignment = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showNotification } = useNotification();
  
  const preselectedClass = searchParams.get('class');
  const preselectedStudent = searchParams.get('student');
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assignment_type: preselectedStudent ? 'individual' : 'class',
    class_id: preselectedClass || '',
    student_id: preselectedStudent || '',
    skills: [],
    question_count: 10,
    difficulty: 'mixed',
    due_date: '',
    time_limit: null
  });

  const { data: classes, loading: loadingClasses } = useFetch(teacherAPI.getClasses);
  const { data: skills, loading: loadingSkills } = useFetch(() => assignmentAPI.getSkills());

  const { mutate: createAssignment, loading: creating } = useMutation(
    (data) => assignmentAPI.createAssignment(data),
    {
      onSuccess: (response) => {
        showNotification('Assignment created successfully!', 'success');
        navigate(`/teacher/assignments/${response.id}`);
      },
      onError: (error) => {
        showNotification(`Failed to create assignment: ${error}`, 'error');
      }
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.title.trim()) {
      showNotification('Please enter an assignment title', 'error');
      return;
    }
    
    if (formData.assignment_type === 'class' && !formData.class_id) {
      showNotification('Please select a class', 'error');
      return;
    }
    
    if (formData.assignment_type === 'individual' && !formData.student_id) {
      showNotification('Please select a student', 'error');
      return;
    }
    
    if (formData.skills.length === 0) {
      showNotification('Please select at least one skill', 'error');
      return;
    }
    
    createAssignment(formData);
  };

  const handleSkillToggle = (skillId) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.includes(skillId)
        ? prev.skills.filter(id => id !== skillId)
        : [...prev.skills, skillId]
    }));
  };

  if (loadingClasses || loadingSkills) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading..." />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <button 
          onClick={() => navigate('/teacher/assignments')}
          className="text-gray-600 hover:text-gray-900 mb-4 flex items-center"
        >
          ← Back to Assignments
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Create Assignment</h1>
        <p className="text-gray-600 mt-1">Create a new practice assignment for your students</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Basic Information</h2>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Assignment Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="e.g., Algebra Practice - Week 5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Optional description or instructions..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Assignment Type *
              </label>
              <select
                value={formData.assignment_type}
                onChange={(e) => setFormData({ ...formData, assignment_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="class">Class Assignment</option>
                <option value="individual">Individual Assignment</option>
              </select>
            </div>

            {formData.assignment_type === 'class' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Class *
                </label>
                <select
                  value={formData.class_id}
                  onChange={(e) => setFormData({ ...formData, class_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Choose a class...</option>
                  {classes?.map(cls => (
                    <option key={cls.id} value={cls.id}>{cls.name}</option>
                  ))}
                </select>
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Student ID *
                </label>
                <input
                  type="text"
                  value={formData.student_id}
                  onChange={(e) => setFormData({ ...formData, student_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Enter student ID"
                />
              </div>
            )}
          </div>
        </div>

        {/* Skills Selection */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Skills to Practice *</h2>
          <p className="text-sm text-gray-600">Select one or more skills for this assignment</p>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-64 overflow-y-auto p-2">
            {skills?.map(skill => (
              <label
                key={skill.id}
                className={`flex items-center space-x-2 p-3 border rounded-lg cursor-pointer transition-colors ${
                  formData.skills.includes(skill.id)
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input
                  type="checkbox"
                  checked={formData.skills.includes(skill.id)}
                  onChange={() => handleSkillToggle(skill.id)}
                  className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                />
                <span className="text-sm text-gray-900">{skill.name}</span>
              </label>
            ))}
          </div>
          
          <div className="text-sm text-gray-600">
            Selected: {formData.skills.length} skill{formData.skills.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Assignment Settings */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Assignment Settings</h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Questions
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={formData.question_count}
                onChange={(e) => setFormData({ ...formData, question_count: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level
              </label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Due Date
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Limit (minutes)
              </label>
              <input
                type="number"
                min="0"
                value={formData.time_limit || ''}
                onChange={(e) => setFormData({ ...formData, time_limit: e.target.value ? parseInt(e.target.value) : null })}
                placeholder="No limit"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/teacher/assignments')}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={creating}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={creating}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {creating ? 'Creating...' : 'Create Assignment'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateAssignment;

