import { apiClient } from './client';
import type { Assignment, CreateAssignmentRequest } from '../types';

export const assignmentsApi = {
  async getAssignments(): Promise<Assignment[]> {
    const response = await apiClient.get<Assignment[]>('/assignments');
    return response.data;
  },

  async getAssignment(id: number): Promise<Assignment> {
    const response = await apiClient.get<Assignment>(`/assignments/${id}`);
    return response.data;
  },

  async createAssignment(data: CreateAssignmentRequest): Promise<Assignment> {
    const response = await apiClient.post<Assignment>('/assignments', data);
    return response.data;
  },

  async updateAssignment(id: number, data: Partial<CreateAssignmentRequest>): Promise<Assignment> {
    const response = await apiClient.patch<Assignment>(`/assignments/${id}`, data);
    return response.data;
  },

  async deleteAssignment(id: number): Promise<void> {
    await apiClient.delete(`/assignments/${id}`);
  },

  async approveAssignment(id: number): Promise<Assignment> {
    const response = await apiClient.post<Assignment>(`/assignments/${id}/approve`);
    return response.data;
  },
};
