import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useFetch } from '../../hooks/useApi';
import { teacherAPI } from '../../services/api';
import LoadingSpinner from '../shared/LoadingSpinner';
import EmptyState from '../shared/EmptyState';

const ClassList = () => {
  const navigate = useNavigate();
  const { data: classes, loading, error } = useFetch(teacherAPI.getClasses);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading classes..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load classes: {error}</p>
      </div>
    );
  }

  if (!classes || classes.length === 0) {
    return (
      <EmptyState
        icon="🎓"
        title="No Classes Yet"
        description="You haven't created any classes yet. Create your first class to get started."
        actionLabel="Create Class"
        onAction={() => navigate('/teacher/classes/new')}
      />
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Classes</h1>
          <p className="text-gray-600 mt-1">Manage your classes and students</p>
        </div>
        <button 
          onClick={() => navigate('/teacher/classes/new')}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          + Create Class
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((classItem) => (
          <div 
            key={classItem.id} 
            className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => navigate(`/teacher/classes/${classItem.id}`)}
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{classItem.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {classItem.grade_level} • {classItem.subject || 'Math'}
                  </p>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                  {classItem.student_count} students
                </span>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Average Accuracy</span>
                  <span className="font-semibold text-gray-900">
                    {Math.round((classItem.avg_accuracy || 0) * 100)}%
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Active Students</span>
                  <span className="font-semibold text-gray-900">
                    {classItem.active_students || 0}/{classItem.student_count}
                  </span>
                </div>

                {classItem.struggling_students > 0 && (
                  <div className="flex items-center justify-between p-2 bg-yellow-50 rounded">
                    <span className="text-sm text-yellow-700">⚠️ Need Help</span>
                    <span className="font-semibold text-yellow-700">
                      {classItem.struggling_students}
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>Invite Code:</span>
                  <code className="px-2 py-1 bg-gray-100 rounded font-mono">
                    {classItem.invite_code}
                  </code>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ClassList;

