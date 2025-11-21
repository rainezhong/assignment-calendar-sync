import { apiClient } from './client';
import type {
  GmailAuthResponse,
  GmailStatus,
  SyncGmailRequest,
  SyncGmailResponse,
} from '../types';

export const gmailApi = {
  /**
   * Get Gmail OAuth authorization URL
   */
  getAuthUrl: async (): Promise<GmailAuthResponse> => {
    const response = await apiClient.get<GmailAuthResponse>('/gmail/auth');
    return response.data;
  },

  /**
   * Get Gmail connection status
   */
  getStatus: async (): Promise<GmailStatus> => {
    const response = await apiClient.get<GmailStatus>('/gmail/status');
    return response.data;
  },

  /**
   * Sync emails from Gmail
   */
  sync: async (data?: SyncGmailRequest): Promise<SyncGmailResponse> => {
    const response = await apiClient.post<SyncGmailResponse>('/gmail/sync', data || {});
    return response.data;
  },

  /**
   * Disconnect Gmail account
   */
  disconnect: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post('/gmail/disconnect');
    return response.data;
  },
};
