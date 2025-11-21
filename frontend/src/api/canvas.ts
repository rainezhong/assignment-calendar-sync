import { apiClient } from './client';
import type {
  CanvasConnectRequest,
  CanvasConnectionResponse,
  CanvasStatus,
  SyncResponse,
} from '../types';

export const canvasApi = {
  /**
   * Connect Canvas account with API token
   */
  connect: async (data: CanvasConnectRequest): Promise<CanvasConnectionResponse> => {
    const response = await apiClient.post<CanvasConnectionResponse>('/canvas/connect', data);
    return response.data;
  },

  /**
   * Disconnect Canvas account
   */
  disconnect: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post('/canvas/disconnect');
    return response.data;
  },

  /**
   * Get Canvas connection status
   */
  getStatus: async (): Promise<CanvasStatus> => {
    const response = await apiClient.get<CanvasStatus>('/canvas/status');
    return response.data;
  },

  /**
   * Sync courses and assignments from Canvas
   */
  sync: async (): Promise<SyncResponse> => {
    const response = await apiClient.post<SyncResponse>('/canvas/sync');
    return response.data;
  },
};
