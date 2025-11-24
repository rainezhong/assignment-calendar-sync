import { apiClient } from './client';

export interface Task {
  id: number;
  assignment_id: number;
  user_id: number;
  title: string;
  description?: string;
  priority: number; // 1=high, 2=medium, 3=low
  due_date: string;
  completed_at?: string;
  is_completed: boolean;
  order: number;
  created_at: string;
  // Additional context
  assignment_title?: string;
  assignment_course?: string;
}

export interface GenerateTasksRequest {
  regenerate?: boolean;
}

export interface TaskCalendarEvent {
  id: number;
  title: string;
  start: string;
  end: string;
  priority: number;
  is_completed: boolean;
  assignment_title: string;
  assignment_id: number;
  type: string;
}

export const tasksApi = {
  /**
   * Generate tasks for an assignment using AI
   */
  generateTasks: async (assignmentId: number, data: GenerateTasksRequest = {}) => {
    const response = await apiClient.post<Task[]>(
      `/assignments/${assignmentId}/generate-tasks`,
      data
    );
    return response.data;
  },

  /**
   * Get tasks for a specific assignment
   */
  getAssignmentTasks: async (assignmentId: number) => {
    const response = await apiClient.get<Task[]>(`/assignments/${assignmentId}/tasks`);
    return response.data;
  },

  /**
   * Get all tasks for current user
   */
  getAllTasks: async (status?: 'pending' | 'completed') => {
    const response = await apiClient.get<Task[]>('/tasks', {
      params: status ? { status } : {},
    });
    return response.data;
  },

  /**
   * Update a task
   */
  updateTask: async (
    taskId: number,
    data: {
      is_completed?: boolean;
      priority?: number;
      due_date?: string;
    }
  ) => {
    const response = await apiClient.patch<Task>(`/tasks/${taskId}`, data);
    return response.data;
  },

  /**
   * Mark task as complete (convenience method)
   */
  completeTask: async (taskId: number) => {
    const response = await apiClient.post<Task>(`/tasks/${taskId}/complete`);
    return response.data;
  },

  /**
   * Delete a task
   */
  deleteTask: async (taskId: number) => {
    const response = await apiClient.delete(`/tasks/${taskId}`);
    return response.data;
  },

  /**
   * Get tasks as calendar events
   */
  getTasksCalendar: async (startDate: string, endDate: string) => {
    const response = await apiClient.get<TaskCalendarEvent[]>('/tasks/calendar', {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    });
    return response.data;
  },
};
