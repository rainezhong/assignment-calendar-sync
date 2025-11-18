// lib/api.ts
// API client for communicating with FastAPI backend

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  setToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem('access_token', token);
  }

  clearToken(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token');
  }

  // Auth endpoints
  async register(email: string, password: string, full_name?: string) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      full_name,
    });
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {
      email,
      password,
    });
    if (response.data.access_token) {
      this.setToken(response.data.access_token);
    }
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  logout() {
    this.clearToken();
  }

  // Career endpoints
  async getCareerProfile() {
    const response = await this.client.get('/career/profile');
    return response.data;
  }

  async getUserProfile() {
    // Alias for getCareerProfile for consistency
    return this.getCareerProfile();
  }

  async uploadResume(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/career/profile/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async setJobPreferences(preferences: any) {
    const response = await this.client.post('/career/profile/preferences', preferences);
    return response.data;
  }

  async updateJobPreferences(preferences: any) {
    // Alias for setJobPreferences for consistency
    return this.setJobPreferences(preferences);
  }

  async updateProfile(profileData: any) {
    const response = await this.client.patch('/career/profile', profileData);
    return response.data;
  }

  async searchJobs() {
    const response = await this.client.post('/career/jobs/search');
    return response.data;
  }

  async getJobMatches(params?: { status?: string; limit?: number }) {
    const response = await this.client.get('/career/jobs/matches', { params });
    return response.data;
  }

  async getApplicationStats() {
    const response = await this.client.get('/career/applications/stats');
    return response.data;
  }

  async getReadyToSubmitQueue() {
    const response = await this.client.get('/career/queue/ready');
    return response.data;
  }

  async approveApplication(applicationId: number) {
    const response = await this.client.post(`/career/queue/${applicationId}/approve`);
    return response.data;
  }

  async dismissApplication(applicationId: number) {
    const response = await this.client.delete(`/career/queue/${applicationId}/dismiss`);
    return response.data;
  }
}

export const api = new ApiClient();
