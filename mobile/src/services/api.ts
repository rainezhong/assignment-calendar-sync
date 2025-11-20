/**
 * API service layer for communicating with FastAPI backend.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Assignment, User, HealthScore, RiskAssessment, AuthTokens } from '../types';

// API Configuration
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'  // Development
  : 'https://your-production-api.com/api/v1';  // Production

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - Add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - Handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try refresh
          try {
            await this.refreshToken();
            // Retry original request
            return this.client.request(error.config!);
          } catch {
            // Refresh failed, logout user
            await this.logout();
            throw error;
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // ============ Authentication ============

  async register(email: string, password: string, full_name?: string): Promise<User> {
    const response = await this.client.post<User>('/auth/register', {
      email,
      password,
      full_name,
    });
    return response.data;
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const response = await this.client.post<AuthTokens>('/auth/login', {
      email,
      password,
    });

    // Store tokens
    await AsyncStorage.setItem('access_token', response.data.access_token);
    await AsyncStorage.setItem('refresh_token', response.data.refresh_token);

    return response.data;
  }

  async refreshToken(): Promise<void> {
    const refreshToken = await AsyncStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token');
    }

    // TODO: Implement refresh endpoint on backend
    // For now, just logout
    throw new Error('Token refresh not implemented');
  }

  async logout(): Promise<void> {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // ============ Assignments ============

  async getAssignments(params?: {
    skip?: number;
    limit?: number;
    course_name?: string;
    is_completed?: boolean;
  }): Promise<Assignment[]> {
    const response = await this.client.get<Assignment[]>('/assignments', { params });
    return response.data;
  }

  async getAssignment(id: number): Promise<Assignment> {
    const response = await this.client.get<Assignment>(`/assignments/${id}`);
    return response.data;
  }

  async createAssignment(data: {
    title: string;
    description?: string;
    course_name: string;
    assignment_type: string;
    due_date: string;
  }): Promise<Assignment> {
    const response = await this.client.post<Assignment>('/assignments', data);
    return response.data;
  }

  async updateAssignment(
    id: number,
    data: Partial<Assignment>
  ): Promise<Assignment> {
    const response = await this.client.patch<Assignment>(`/assignments/${id}`, data);
    return response.data;
  }

  async deleteAssignment(id: number): Promise<void> {
    await this.client.delete(`/assignments/${id}`);
  }

  // ============ Intelligence (Phase 4) ============

  async analyzeAssignment(id: number): Promise<any> {
    const response = await this.client.post(`/intelligence/${id}/analyze`);
    return response.data;
  }

  async getAssignmentSkills(id: number): Promise<string[]> {
    const response = await this.client.get<string[]>(`/intelligence/${id}/skills`);
    return response.data;
  }

  async getAssignmentResources(id: number): Promise<any[]> {
    const response = await this.client.get(`/intelligence/${id}/resources`);
    return response.data;
  }

  // ============ Analytics (Phase 4) ============

  async getHealthScore(): Promise<HealthScore> {
    const response = await this.client.get<HealthScore>('/analytics/health');
    return response.data;
  }

  async getPerformanceTrends(days: number = 30): Promise<any[]> {
    const response = await this.client.get('/analytics/trends', {
      params: { days },
    });
    return response.data;
  }

  async getAnalyticsSummary(): Promise<any> {
    const response = await this.client.get('/analytics/summary');
    return response.data;
  }

  // ============ Predictions (Phase 4) ============

  async assessRisk(assignmentId: number): Promise<RiskAssessment> {
    const response = await this.client.get<RiskAssessment>(
      `/predictions/risk/${assignmentId}`
    );
    return response.data;
  }

  async optimizeWorkload(maxHoursPerDay: number = 8): Promise<any> {
    const response = await this.client.post('/predictions/optimize-workload', null, {
      params: { max_hours_per_day: maxHoursPerDay },
    });
    return response.data;
  }

  async getSuggestions(): Promise<any[]> {
    const response = await this.client.get('/predictions/suggestions');
    return response.data;
  }

  // ============ Career (Assisted Apply) ============

  async uploadResume(file: any): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/career/profile/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getCareerProfile(): Promise<any> {
    const response = await this.client.get('/career/profile');
    return response.data;
  }

  async setJobPreferences(preferences: any): Promise<any> {
    const response = await this.client.post('/career/profile/preferences', preferences);
    return response.data;
  }

  async searchJobs(): Promise<any> {
    const response = await this.client.post('/career/jobs/search');
    return response.data;
  }

  async getJobMatches(params?: { status?: string; limit?: number }): Promise<any[]> {
    const response = await this.client.get('/career/jobs/matches', { params });
    return response.data;
  }

  async updateMatchStatus(matchId: number, status: string): Promise<any> {
    const response = await this.client.patch(`/career/jobs/matches/${matchId}/status`, null, {
      params: { status },
    });
    return response.data;
  }

  async createApplication(jobId: number, data?: any): Promise<any> {
    const response = await this.client.post('/career/applications', {
      job_id: jobId,
      ...data,
    });
    return response.data;
  }

  async getApplications(status?: string): Promise<any[]> {
    const response = await this.client.get('/career/applications', {
      params: { status },
    });
    return response.data;
  }

  async updateApplication(applicationId: number, data: any): Promise<any> {
    const response = await this.client.patch(`/career/applications/${applicationId}`, data);
    return response.data;
  }

  async getApplicationStats(): Promise<any> {
    const response = await this.client.get('/career/applications/stats');
    return response.data;
  }

  async generateCoverLetter(jobId: number): Promise<any> {
    const response = await this.client.post('/career/cover-letter/generate', null, {
      params: { job_id: jobId },
    });
    return response.data;
  }

  // Auto-Prep Queue
  async getReadyToSubmitQueue(): Promise<any[]> {
    const response = await this.client.get('/career/queue/ready');
    return response.data;
  }

  async approveApplication(applicationId: number): Promise<any> {
    const response = await this.client.post(`/career/queue/${applicationId}/approve`);
    return response.data;
  }

  async dismissApplication(applicationId: number): Promise<any> {
    const response = await this.client.delete(`/career/queue/${applicationId}/dismiss`);
    return response.data;
  }
}

// Export singleton instance
export default new ApiService();
