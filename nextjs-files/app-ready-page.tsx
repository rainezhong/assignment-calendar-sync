// app/ready/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { PreparedApplication } from '@/lib/types';

export default function ReadyToSubmitPage() {
  const { logout } = useAuth();
  const router = useRouter();
  const [applications, setApplications] = useState<PreparedApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<number | null>(null);

  useEffect(() => {
    loadApplications();
  }, []);

  async function loadApplications() {
    try {
      const data = await api.getReadyToSubmitQueue();
      setApplications(data);
    } catch (error) {
      console.error('Failed to load applications:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(id: number) {
    if (!confirm('Submit this application?')) return;

    setSubmitting(id);
    try {
      await api.approveApplication(id);
      alert('Application submitted successfully! 🎉');
      // Remove from list
      setApplications(applications.filter(app => app.id !== id));
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit application');
    } finally {
      setSubmitting(null);
    }
  }

  async function handleDismiss(id: number) {
    if (!confirm("Dismiss this application? You won't apply to this job.")) return;

    try {
      await api.dismissApplication(id);
      setApplications(applications.filter(app => app.id !== id));
    } catch (error) {
      alert('Failed to dismiss application');
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading applications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-2xl font-bold text-indigo-600">College Assistant</h1>
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-700 hover:text-indigo-600"
              >
                ← Back to Dashboard
              </button>
            </div>
            <div className="flex items-center space-x-4">
              <button onClick={logout} className="text-gray-700 hover:text-indigo-600">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Ready to Submit</h2>
              <p className="mt-2 text-gray-600">{applications.length} applications prepared</p>
            </div>
            <div className="bg-indigo-600 text-white px-4 py-2 rounded-full font-semibold">
              {applications.length}
            </div>
          </div>
        </div>

        {/* Info Banner */}
        {applications.length > 0 && (
          <div className="mb-6 bg-indigo-50 border border-indigo-200 rounded-lg p-4 flex items-start">
            <svg className="h-5 w-5 text-indigo-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <p className="text-sm text-indigo-800">
              These applications were automatically prepared for you. Review the details and cover letter, then tap Submit when ready!
            </p>
          </div>
        )}

        {/* Applications List */}
        {applications.length > 0 ? (
          <div className="space-y-6">
            {applications.map((app, index) => (
              <div key={app.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                          #{index + 1}
                        </span>
                        <span className="text-xs text-gray-500">
                          Prepared {new Date(app.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900">{app.job.title}</h3>
                      <p className="text-base text-indigo-600 font-medium">{app.job.company}</p>
                      <p className="text-sm text-gray-600">{app.job.location}</p>
                    </div>
                  </div>

                  {/* Salary */}
                  {app.job.salary_min && (
                    <div className="mb-4 flex items-center text-sm text-gray-600">
                      <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      ${app.job.salary_min.toLocaleString()}
                      {app.job.salary_max && ` - $${app.job.salary_max.toLocaleString()}`}
                    </div>
                  )}

                  {/* Cover Letter */}
                  <div className="mb-4 bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-semibold text-gray-700">AI-Generated Cover Letter</h4>
                      <span className="text-xs text-gray-500">Ready to use</span>
                    </div>
                    <p className="text-sm text-gray-700 whitespace-pre-line line-clamp-4">
                      {app.cover_letter}
                    </p>
                    <button className="mt-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium">
                      Read full letter →
                    </button>
                  </div>

                  {/* Status */}
                  <div className="mb-4 flex items-center text-sm text-green-600">
                    <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    All fields pre-filled and ready
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-3">
                    <button
                      onClick={() => handleApprove(app.id)}
                      disabled={submitting === app.id}
                      className="flex-1 inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submitting === app.id ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Submitting...
                        </>
                      ) : (
                        <>
                          <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                          </svg>
                          Submit Application
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleDismiss(app.id)}
                      disabled={submitting === app.id}
                      className="inline-flex justify-center items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          // Empty State
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">All Caught Up!</h3>
            <p className="mt-1 text-sm text-gray-500">
              New applications will appear here automatically when jobs matching your profile are found.
            </p>
            <p className="mt-2 text-xs text-gray-400">
              The system searches for jobs daily at 8 AM and prepares applications for you.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
