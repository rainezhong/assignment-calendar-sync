import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle2, Circle, Clock, AlertCircle, ListTodo } from 'lucide-react';
import { tasksApi, Task } from '../api/tasks';

export default function Tasks() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('pending');

  // Get all tasks
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', filter],
    queryFn: () => {
      if (filter === 'all') {
        return tasksApi.getAllTasks();
      }
      return tasksApi.getAllTasks(filter);
    },
  });

  // Toggle task completion
  const toggleMutation = useMutation({
    mutationFn: ({ taskId, isCompleted }: { taskId: number; isCompleted: boolean }) =>
      tasksApi.updateTask(taskId, { is_completed: !isCompleted }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
    },
  });

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return 'text-red-600 bg-red-50 border-red-200';
      case 2:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 3:
        return 'text-gray-600 bg-gray-50 border-gray-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPriorityLabel = (priority: number) => {
    switch (priority) {
      case 1:
        return 'High';
      case 2:
        return 'Medium';
      case 3:
        return 'Low';
      default:
        return 'Medium';
    }
  };

  const getPriorityIcon = (priority: number) => {
    if (priority === 1) {
      return <AlertCircle className="w-4 h-4" />;
    }
    return <Clock className="w-4 h-4" />;
  };

  const formatDueDate = (dueDate: string) => {
    const date = new Date(dueDate);
    const now = new Date();
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) !== 1 ? 's' : ''}`;
    } else if (diffDays === 0) {
      return 'Due today';
    } else if (diffDays === 1) {
      return 'Due tomorrow';
    } else if (diffDays <= 7) {
      return `Due in ${diffDays} days`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const handleToggleTask = (task: Task) => {
    toggleMutation.mutate({
      taskId: task.id,
      isCompleted: task.is_completed,
    });
  };

  // Group tasks by assignment
  const groupedTasks = tasks?.reduce((acc, task) => {
    const key = task.assignment_id;
    if (!acc[key]) {
      acc[key] = {
        assignment_title: task.assignment_title || 'Unknown Assignment',
        assignment_course: task.assignment_course || '',
        tasks: [],
      };
    }
    acc[key].tasks.push(task);
    return acc;
  }, {} as Record<number, { assignment_title: string; assignment_course: string; tasks: Task[] }>);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
        <p className="text-gray-600 mt-1">
          Your assignments broken down into actionable tasks
        </p>
      </div>

      {/* Filter tabs */}
      <div className="card mb-6">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'pending'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'completed'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All
          </button>

          {tasks && (
            <span className="ml-auto text-sm text-gray-600">
              {tasks.length} task{tasks.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Tasks list */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading tasks...</p>
          </div>
        </div>
      ) : !tasks || tasks.length === 0 ? (
        <div className="card text-center py-12">
          <ListTodo className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
          <p className="text-gray-600 mb-4">
            {filter === 'pending'
              ? 'All caught up! No pending tasks.'
              : filter === 'completed'
              ? 'No completed tasks yet.'
              : 'Sync your assignments from Canvas or Gradescope to generate tasks.'}
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {groupedTasks &&
            Object.values(groupedTasks).map((group, idx) => (
              <div key={idx} className="card">
                {/* Assignment header */}
                <div className="mb-4 pb-3 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {group.assignment_title}
                  </h3>
                  {group.assignment_course && (
                    <p className="text-sm text-gray-600">{group.assignment_course}</p>
                  )}
                  <div className="mt-2 text-sm text-gray-600">
                    {group.tasks.filter((t) => t.is_completed).length} of {group.tasks.length}{' '}
                    tasks completed
                  </div>
                </div>

                {/* Tasks in assignment */}
                <div className="space-y-2">
                  {group.tasks.map((task) => (
                    <div
                      key={task.id}
                      className={`flex items-start gap-3 p-3 rounded-md border transition-all ${
                        task.is_completed
                          ? 'bg-gray-50 border-gray-200 opacity-60'
                          : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-sm'
                      }`}
                    >
                      {/* Checkbox */}
                      <button
                        onClick={() => handleToggleTask(task)}
                        disabled={toggleMutation.isPending}
                        className="mt-0.5 flex-shrink-0 hover:scale-110 transition-transform"
                      >
                        {task.is_completed ? (
                          <CheckCircle2 className="w-5 h-5 text-green-600" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-400 hover:text-blue-600" />
                        )}
                      </button>

                      {/* Task content */}
                      <div className="flex-1 min-w-0">
                        <h4
                          className={`text-sm font-medium ${
                            task.is_completed
                              ? 'text-gray-500 line-through'
                              : 'text-gray-900'
                          }`}
                        >
                          {task.title}
                        </h4>

                        {task.description && (
                          <p className="text-xs text-gray-600 mt-1">{task.description}</p>
                        )}

                        <div className="flex items-center gap-3 mt-2">
                          {/* Priority badge */}
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${getPriorityColor(
                              task.priority
                            )}`}
                          >
                            {getPriorityIcon(task.priority)}
                            {getPriorityLabel(task.priority)}
                          </span>

                          {/* Due date */}
                          <span className="text-xs text-gray-600">
                            {formatDueDate(task.due_date)}
                          </span>

                          {task.completed_at && (
                            <span className="text-xs text-gray-500">
                              Completed {new Date(task.completed_at).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
