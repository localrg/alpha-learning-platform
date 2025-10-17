import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import XPDisplay from '../components/XPDisplay';
import StreakDisplay from '../components/StreakDisplay';

const StudentLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    { path: '/student/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/student/practice', label: 'Practice', icon: '📚' },
    { path: '/student/reviews', label: 'Reviews', icon: '🔄' },
    { path: '/student/resources', label: 'Resources', icon: '📖' },
    { path: '/student/achievements', label: 'Achievements', icon: '🏆' },
    { path: '/student/leaderboard', label: 'Leaderboard', icon: '🥇' },
    { path: '/student/profile', label: 'Profile', icon: '👤' },
    { path: '/student/friends', label: 'Friends', icon: '👥' },
    { path: '/student/classes', label: 'Classes', icon: '🎓' },
    { path: '/student/challenges', label: 'Challenges', icon: '⚔️' },
    { path: '/student/feed', label: 'Feed', icon: '📰' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">Alpha Learning</h1>
            </div>

            {/* User Info */}
            <div className="flex items-center space-x-4">
              <XPDisplay />
              <StreakDisplay />
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Welcome, {user?.name || user?.email}</span>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={logout}
                  className="text-red-600 hover:text-red-700"
                >
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-white shadow-sm min-h-screen">
          <div className="p-4">
            <div className="space-y-2">
              {navigationItems.map((item) => (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    isActive(item.path)
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default StudentLayout;
