const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://zmhqivckvvnn.manus.space';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      let data;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        throw new Error(data.message || data || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // HTTP Methods
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // File upload
  async upload(endpoint, formData) {
    const headers = {};
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return this.request(endpoint, {
      method: 'POST',
      headers,
      body: formData,
    });
  }
}

// Create singleton instance
const apiClient = new ApiClient();

export default apiClient;

// Specific API service functions
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  getCurrentUser: () => apiClient.get('/auth/me'),
  refreshToken: () => apiClient.post('/auth/refresh'),
};

export const studentAPI = {
  getProfile: () => apiClient.get('/students/profile'),
  updateProfile: (data) => apiClient.put('/students/profile', data),
  getProgress: () => apiClient.get('/students/progress'),
  getSkills: () => apiClient.get('/students/skills'),
  getAchievements: () => apiClient.get('/students/achievements'),
  getLeaderboard: () => apiClient.get('/students/leaderboard'),
  getFriends: () => apiClient.get('/students/friends'),
  addFriend: (friendId) => apiClient.post('/students/friends', { friend_id: friendId }),
  removeFriend: (friendId) => apiClient.delete(`/students/friends/${friendId}`),
};

export const assessmentAPI = {
  startAssessment: () => apiClient.post('/assessment/start'),
  getQuestion: (sessionId) => apiClient.get(`/assessment/${sessionId}/question`),
  submitAnswer: (sessionId, data) => apiClient.post(`/assessment/${sessionId}/answer`, data),
  completeAssessment: (sessionId) => apiClient.post(`/assessment/${sessionId}/complete`),
};

export const practiceAPI = {
  startSession: (skillId) => apiClient.post('/practice/start', { skill_id: skillId }),
  getQuestion: (sessionId) => apiClient.get(`/practice/${sessionId}/question`),
  submitAnswer: (sessionId, data) => apiClient.post(`/practice/${sessionId}/answer`, data),
  completeSession: (sessionId) => apiClient.post(`/practice/${sessionId}/complete`),
};

export const reviewAPI = {
  getReviewItems: () => apiClient.get('/review/items'),
  startReviewSession: () => apiClient.post('/review/start'),
  submitReviewAnswer: (sessionId, data) => apiClient.post(`/review/${sessionId}/answer`, data),
  completeReviewSession: (sessionId) => apiClient.post(`/review/${sessionId}/complete`),
};

export const resourceAPI = {
  getResources: (params) => apiClient.get('/resources', params),
  getResource: (id) => apiClient.get(`/resources/${id}`),
  searchResources: (query) => apiClient.get('/resources/search', { q: query }),
};

export const classAPI = {
  getClasses: () => apiClient.get('/classes'),
  joinClass: (inviteCode) => apiClient.post('/classes/join', { invite_code: inviteCode }),
  leaveClass: (classId) => apiClient.delete(`/classes/${classId}/leave`),
  getClassMembers: (classId) => apiClient.get(`/classes/${classId}/members`),
};

export const challengeAPI = {
  getChallenges: () => apiClient.get('/shared-challenges'),
  createChallenge: (data) => apiClient.post('/shared-challenges', data),
  joinChallenge: (challengeId) => apiClient.post(`/shared-challenges/${challengeId}/join`),
  getChallenge: (challengeId) => apiClient.get(`/shared-challenges/${challengeId}`),
  getChallengeLeaderboard: (challengeId) => apiClient.get(`/shared-challenges/${challengeId}/leaderboard`),
};

export const feedAPI = {
  getActivityFeed: (params) => apiClient.get('/activity-feed', params),
  getMyActivity: () => apiClient.get('/activity-feed/me'),
};

// Teacher APIs
export const teacherAPI = {
  getDashboard: () => apiClient.get('/teacher/dashboard'),
  getClasses: () => apiClient.get('/teacher/classes'),
  getClassOverview: (classId) => apiClient.get(`/teacher/classes/${classId}`),
  getStudentSummary: (studentId) => apiClient.get(`/teacher/students/${studentId}`),
  createAssignment: (data) => apiClient.post('/assignments', data),
  getAssignments: () => apiClient.get('/assignments'),
  updateAssignment: (id, data) => apiClient.put(`/assignments/${id}`, data),
  deleteAssignment: (id) => apiClient.delete(`/assignments/${id}`),
};

// Parent APIs
export const parentAPI = {
  getProfile: () => apiClient.get('/parent/profile'),
  getChildren: () => apiClient.get('/parent/children'),
  linkChild: (inviteCode) => apiClient.post('/parent/link-child', { invite_code: inviteCode }),
  getChildProgress: (childId) => apiClient.get(`/parent/children/${childId}/progress`),
  getChildReports: (childId, params) => apiClient.get(`/parent/children/${childId}/reports`, params),
};

// Communication APIs (for parent-teacher messaging)
export const communicationAPI = {
  getMessages: (params) => apiClient.get('/communication/messages', params),
  sendMessage: (data) => apiClient.post('/communication/messages', data),
  markAsRead: (messageId) => apiClient.put(`/communication/messages/${messageId}/read`),
  getConversation: (teacherId) => apiClient.get(`/communication/conversation/${teacherId}`),
};

// Goal APIs (for parent goal management)
export const goalAPI = {
  getGoals: (studentId) => apiClient.get(`/goals/${studentId}`),
  createGoal: (data) => apiClient.post('/goals', data),
  updateGoal: (goalId, data) => apiClient.put(`/goals/${goalId}`, data),
  deleteGoal: (goalId) => apiClient.delete(`/goals/${goalId}`),
  updateProgress: (goalId, progress) => apiClient.put(`/goals/${goalId}/progress`, { progress }),
};

// Admin APIs
export const adminAPI = {
  getDashboard: () => apiClient.get('/admin/dashboard'),
  getUsers: (params) => apiClient.get('/admin/users', params),
  createUser: (data) => apiClient.post('/admin/users', data),
  updateUser: (id, data) => apiClient.put(`/admin/users/${id}`, data),
  deleteUser: (id) => apiClient.delete(`/admin/users/${id}`),
  getAuditLogs: (params) => apiClient.get('/admin/audit-logs', params),
  getSettings: () => apiClient.get('/admin/settings'),
  updateSettings: (data) => apiClient.put('/admin/settings', data),
};
