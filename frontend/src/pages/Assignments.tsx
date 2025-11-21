import { useQuery } from '@tanstack/react-query';
import { assignmentsApi } from '../api/assignments';
import { format } from 'date-fns';
import { Calendar, Clock, BookOpen, Plus } from 'lucide-react';

export default function Assignments() {
  const { data: assignments, isLoading, error } = useQuery({
    queryKey: ['assignments'],
    queryFn: assignmentsApi.getAssignments,
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

  const sortedAssignments = [...(assignments || [])].sort((a, b) =>
    new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
  );

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600 mt-1">
            {assignments?.length || 0} total assignments
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Assignment
        </button>
      </div>

      {/* Empty State */}
      {assignments?.length === 0 && (
        <div className="card text-center py-12">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No assignments yet</h3>
          <p className="text-gray-600 mb-4">Get started by creating your first assignment</p>
          <button className="btn-primary mx-auto">
            Create Assignment
          </button>
        </div>
      )}

      {/* Assignments List */}
      {assignments && assignments.length > 0 && (
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
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {assignment.title}
                        </h3>
                        <p className="text-gray-600 text-sm mb-3">
                          {assignment.course_name}
                        </p>
                        {assignment.description && (
                          <p className="text-gray-700 text-sm mb-3">
                            {assignment.description}
                          </p>
                        )}
                        <div className="flex items-center gap-4 text-sm">
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
      )}
    </div>
  );
}
