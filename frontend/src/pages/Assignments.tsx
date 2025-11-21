import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assignmentsApi } from '../api/assignments';
import { format } from 'date-fns';
import {
  Calendar,
  Clock,
  BookOpen,
  Plus,
  Check,
  X,
  ExternalLink,
  AlertCircle
} from 'lucide-react';

export default function Assignments() {
  const queryClient = useQueryClient();

  const { data: assignments, isLoading, error } = useQuery({
    queryKey: ['assignments'],
    queryFn: assignmentsApi.getAssignments,
  });

  // Approve assignment mutation
  const approveMutation = useMutation({
    mutationFn: (id: number) => assignmentsApi.approveAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
    },
  });

  // Delete assignment mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => assignmentsApi.deleteAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading assignments...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <p className="text-red-800">Failed to load assignments. Please try again.</p>
      </div>
    );
  }

  // Separate pending and approved assignments
  const pendingAssignments = assignments?.filter(a => !a.approved) || [];
  const approvedAssignments = assignments?.filter(a => a.approved) || [];

  // Sort approved assignments by due date
  const sortedAssignments = [...approvedAssignments].sort((a, b) =>
    new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
  );

  const handleApprove = (id: number) => {
    approveMutation.mutate(id);
  };

  const handleReject = (id: number) => {
    if (confirm('Are you sure you want to delete this assignment?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-1">
            {assignments?.length || 0} total assignments
            {pendingAssignments.length > 0 && (
              <span className="ml-2 text-orange-600">
                ({pendingAssignments.length} pending approval)
              </span>
            )}
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Assignment
        </button>
      </div>

      {/* Pending Approvals Section */}
      {pendingAssignments.length > 0 && (
        <div className="mb-6">
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-orange-600" />
              <h2 className="text-lg font-semibold text-orange-900">
                Pending Approvals
              </h2>
            </div>
            <p className="text-sm text-orange-700">
              Review assignments synced from Canvas. Approve to add them to your timeline or reject to remove them.
            </p>
          </div>

          <div className="space-y-4">
            {pendingAssignments.map((assignment) => {
              const dueDate = new Date(assignment.due_date);

              return (
                <div key={assignment.id} className="card border-2 border-orange-200 bg-orange-50/30">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          {assignment.source === 'canvas' ? '📘 Canvas' : assignment.source}
                        </span>
                        <span className="badge badge-warning">Pending Review</span>
                      </div>

                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {assignment.title}
                      </h3>

                      <p className="text-gray-600 text-sm mb-2">
                        {assignment.course_name}
                      </p>

                      {assignment.description && (
                        <p className="text-gray-700 text-sm mb-3 line-clamp-2">
                          {assignment.description}
                        </p>
                      )}

                      <div className="flex flex-wrap items-center gap-3 text-sm">
                        <div className="flex items-center gap-1.5 text-gray-600">
                          <Calendar className="w-4 h-4" />
                          <span>Due {format(dueDate, 'MMM d, yyyy')}</span>
                        </div>

                        {assignment.points_possible && (
                          <div className="text-gray-600">
                            {assignment.points_possible} points
                          </div>
                        )}

                        {assignment.source_url && (
                          <a
                            href={assignment.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                          >
                            View in Canvas
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 flex-shrink-0">
                      <button
                        onClick={() => handleApprove(assignment.id)}
                        disabled={approveMutation.isPending}
                        className="btn-primary flex items-center gap-2 text-sm px-4 py-2"
                      >
                        <Check className="w-4 h-4" />
                        Approve
                      </button>
                      <button
                        onClick={() => handleReject(assignment.id)}
                        disabled={deleteMutation.isPending}
                        className="btn-secondary text-red-600 hover:bg-red-50 text-sm px-4 py-2"
                      >
                        <X className="w-4 h-4 inline mr-1" />
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty State */}
      {assignments?.length === 0 && (
        <div className="card text-center py-12">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No assignments yet</h3>
          <p className="text-gray-600 mb-4">Get started by creating your first assignment or syncing from Canvas</p>
          <button className="btn-primary mx-auto">
            Create Assignment
          </button>
        </div>
      )}

      {/* Approved Assignments List */}
      {approvedAssignments.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Your Assignments
          </h2>
          <div className="space-y-4">
            {sortedAssignments.map((assignment) => {
              const dueDate = new Date(assignment.due_date);
              const isOverdue = dueDate < new Date() && !assignment.is_completed;
              const daysUntilDue = Math.ceil((dueDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));

              return (
                <div key={assignment.id} className="card hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-start gap-3">
                        <div className={`mt-1 w-2 h-2 rounded-full ${
                          assignment.is_completed
                            ? 'bg-green-500'
                            : isOverdue
                            ? 'bg-red-500'
                            : 'bg-yellow-500'
                        }`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {assignment.title}
                            </h3>
                            {assignment.source !== 'manual' && (
                              <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                                {assignment.source === 'canvas' ? '📘' : assignment.source}
                              </span>
                            )}
                          </div>

                          <p className="text-gray-600 text-sm mb-3">
                            {assignment.course_name}
                          </p>

                          {assignment.description && (
                            <p className="text-gray-700 text-sm mb-3">
                              {assignment.description}
                            </p>
                          )}

                          <div className="flex items-center gap-4 text-sm flex-wrap">
                            <div className="flex items-center gap-1.5 text-gray-600">
                              <Calendar className="w-4 h-4" />
                              <span>Due {format(dueDate, 'MMM d, yyyy')}</span>
                            </div>

                            {assignment.estimated_hours && (
                              <div className="flex items-center gap-1.5 text-gray-600">
                                <Clock className="w-4 h-4" />
                                <span>{assignment.estimated_hours}h estimated</span>
                              </div>
                            )}

                            <span className={`badge ${
                              assignment.is_completed
                                ? 'badge-success'
                                : isOverdue
                                ? 'badge-danger'
                                : 'badge-warning'
                            }`}>
                              {assignment.is_completed
                                ? 'Completed'
                                : isOverdue
                                ? 'Overdue'
                                : `${daysUntilDue} days left`}
                            </span>

                            {assignment.source_url && (
                              <a
                                href={assignment.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                              >
                                View Source
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="ml-4">
                      {assignment.grade_percentage !== null && (
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gray-900">
                            {assignment.grade_percentage}%
                          </div>
                          <div className="text-xs text-gray-500">Grade</div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
