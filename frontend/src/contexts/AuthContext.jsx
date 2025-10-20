import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient, { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('auth_user');
      
      if (token) {
        apiClient.setToken(token);
        
        // Try to use stored user first for immediate UI
        if (storedUser) {
          try {
            setUser(JSON.parse(storedUser));
          } catch (e) {
            console.error('Failed to parse stored user:', e);
          }
        }
        
        // Then verify with server
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
          localStorage.setItem('auth_user', JSON.stringify(userData));
        } catch (err) {
          console.error('Auth check failed:', err);
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
          apiClient.setToken(null);
          setUser(null);
        }
      }
      
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authAPI.login(credentials);
      
      // Handle different response formats
      let access_token, userData;
      if (response && typeof response === 'object') {
        access_token = response.access_token;
        userData = response.user;
      } else {
        throw new Error('Invalid response format from server');
      }
      
      if (!access_token || !userData) {
        throw new Error('Missing authentication data in response');
      }
      
      apiClient.setToken(access_token);
      setUser(userData);
      localStorage.setItem('auth_user', JSON.stringify(userData));
      
      return { success: true, user: userData };
    } catch (err) {
      console.error('Login error:', err);
      const errorMessage = err.message || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authAPI.register(userData);
      
      // Handle different response formats
      let access_token, newUser;
      if (response && typeof response === 'object') {
        access_token = response.access_token;
        newUser = response.user;
      } else {
        throw new Error('Invalid response format from server');
      }
      
      if (!access_token || !newUser) {
        throw new Error('Missing authentication data in response');
      }
      
      apiClient.setToken(access_token);
      setUser(newUser);
      localStorage.setItem('auth_user', JSON.stringify(newUser));
      
      return { success: true, user: newUser };
    } catch (err) {
      console.error('Registration error:', err);
      const errorMessage = err.message || 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      apiClient.setToken(null);
      setUser(null);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  };

  const updateUser = (updates) => {
    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem('auth_user', JSON.stringify(updatedUser));
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isStudent: user?.role === 'student',
    isTeacher: user?.role === 'teacher',
    isParent: user?.role === 'parent',
    isAdmin: user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

