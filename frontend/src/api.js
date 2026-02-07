/**
 * API Client for TRACES+
 * Handles all backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE_URL;
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(username, password) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async register(userData) {
    const response = await this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    this.setToken(response.access_token);
    return response;
  }

  async getCurrentUser() {
    return this.request('/api/auth/me');
  }

  // Student endpoints
  async getStudentDashboard() {
    return this.request('/api/student/dashboard');
  }

  async getStudentTimeline(days = 90) {
    return this.request(`/api/student/timeline?days=${days}`);
  }

  async getAgentAnalysis() {
    return this.request('/api/student/agent-analysis');
  }

  async getSupportResources() {
    return this.request('/api/student/support-resources');
  }

  // Counselor endpoints
  async getCounselorDashboard() {
    return this.request('/api/counselor/dashboard');
  }

  async getStudentsAtRisk(threshold = 0.45) {
    return this.request(`/api/counselor/students-at-risk?risk_threshold=${threshold}`);
  }

  async getStudentDetails(studentId) {
    return this.request(`/api/counselor/student/${studentId}/details`);
  }

  async createEscalation(data) {
    return this.request('/api/counselor/escalate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAnonymousSessions() {
    return this.request('/api/counselor/anonymous-sessions');
  }

  // Admin endpoints
  async getAdminDashboard() {
    return this.request('/api/admin/dashboard');
  }

  async getSystemInsights(insightType = null) {
    const query = insightType ? `?insight_type=${insightType}` : '';
    return this.request(`/api/admin/insights${query}`);
  }

  async generateInsights() {
    return this.request('/api/admin/generate-insights', {
      method: 'POST',
    });
  }

  async getFrictionPatterns(days = 90) {
    return this.request(`/api/admin/friction-patterns?days=${days}`);
  }

  async getEthicalSafeguards() {
    return this.request('/api/admin/ethical-safeguards');
  }

  // Community chat
  async getCommunityRooms() {
    return this.request('/api/community-chat/rooms');
  }

  // Calendar
  async getGoogleAuthUrl(redirectUri) {
    return this.request(`/api/calendar/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`);
  }

  async syncCalendar(formData) {
    // Note: formData doesn't use JSON stringify, and we let browser set Content-Type
    const headers = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}/api/calendar/sync`, {
      method: 'POST',
      headers: headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  // Document Assistant
  async generateDocument(data) {
    return this.request('/api/document/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Development/demo
  async initDemoData() {
    return this.request('/api/dev/init-demo-data', {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();
export default api;