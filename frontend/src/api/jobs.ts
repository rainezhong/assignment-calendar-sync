import { apiClient } from './client';
import type {
  ScrapeJobsRequest,
  ScrapeJobsResponse,
  JobListingResponse,
  JobMatchDetailResponse,
} from '../types';

export const jobsApi = {
  /**
   * Scrape jobs from LinkedIn search URL
   */
  scrapeJobs: async (data: ScrapeJobsRequest): Promise<ScrapeJobsResponse> => {
    const response = await apiClient.post<ScrapeJobsResponse>('/jobs/scrape', data);
    return response.data;
  },

  /**
   * Get all jobs with match scores
   */
  getJobs: async (params?: {
    sort_by?: string;
    job_type?: string;
    remote_type?: string;
  }): Promise<JobListingResponse[]> => {
    const response = await apiClient.get<JobListingResponse[]>('/jobs', { params });
    return response.data;
  },

  /**
   * Get single job details
   */
  getJob: async (jobId: number): Promise<JobListingResponse> => {
    const response = await apiClient.get<JobListingResponse>(`/jobs/${jobId}`);
    return response.data;
  },

  /**
   * Get detailed match breakdown
   */
  getJobMatch: async (jobId: number): Promise<JobMatchDetailResponse> => {
    const response = await apiClient.get<JobMatchDetailResponse>(`/jobs/${jobId}/match`);
    return response.data;
  },

  /**
   * Mark job as applied
   */
  applyToJob: async (jobId: number, notes?: string): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post(`/jobs/${jobId}/apply`, { notes });
    return response.data;
  },
};
