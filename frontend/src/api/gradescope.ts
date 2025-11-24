import { apiClient } from './client';
import type {
  GradescopeConnectRequest,
  GradescopeConnectionResponse,
  GradescopeStatus,
  SyncGradescopeResponse,
} from '../types';

export const gradescopeApi = {
  /**
   * Connect Gradescope account with credentials
   */
  connect: async (data: GradescopeConnectRequest): Promise<GradescopeConnectionResponse> => {
    const response = await apiClient.post<GradescopeConnectionResponse>('/gradescope/connect', data);
    return response.data;
  },

  /**
   * Disconnect Gradescope account
   */
  disconnect: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post('/gradescope/disconnect');
    return response.data;
  },

  /**
   * Get Gradescope connection status
   */
  getStatus: async (): Promise<GradescopeStatus> => {
    const response = await apiClient.get<GradescopeStatus>('/gradescope/status');
    return response.data;
  },

  /**
   * Sync courses and assignments from Gradescope
   */
  sync: async (): Promise<SyncGradescopeResponse> => {
    const response = await apiClient.post<SyncGradescopeResponse>('/gradescope/sync');
    return response.data;
  },
};
