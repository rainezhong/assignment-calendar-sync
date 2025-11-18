// app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { ApplicationStats, PreparedApplication, JobMatch } from '@/lib/types';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<ApplicationStats | null>(null);
  const [readyQueue, setReadyQueue] = useState<PreparedApplication[]>([]);
  const [topMatches, setTopMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statsData, queueData, matchesData] = await Promise.all([
        api.getApplicationStats().catch(() => ({ total: 0, by_status: {}, recent_applications: 0 })),
        api.getReadyToSubmitQueue().catch(() => []),
        api.getJobMatches({ limit: 5 }).catch(() => []),
      ]);

      setStats(statsData);
      setReadyQueue(queueData);
      setTopMatches(matchesData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
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
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-indigo-600">College Assistant</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/profile')}
                className="text-gray-700 hover:text-indigo-600"
              >
                Profile
              </button>
              <span className="text-gray-600">{user?.email}</span>
              <button
                onClick={logout}
                className="px-4 py-2 text-sm text-gray-700 hover:text-indigo-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Ready to Submit Alert */}
        {readyQueue.length > 0 && (
          <div
            onClick={() => router.push('/ready')}
            className="mb-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3">
                  <span className="text-4xl">🚀</span>
                  <div>
                    <h2 className="text-2xl font-bold text-white">
                      {readyQueue.length} Application{readyQueue.length > 1 ? 's' : ''} Ready to Submit!
                    </h2>
                    <p className="text-indigo-100 mt-1">
                      Auto-prepared with AI cover letters - just review and tap submit
                    </p>
                  </div>
                </div>
              </div>
              <div>
                <span className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50">
                  Review Now →
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-indigo-100 rounded-md p-3">
                <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Applications</dt>
                  <dd className="text-3xl font-semibold text-gray-900">{stats?.total || 0}</dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Interviews</dt>
                  <dd className="text-3xl font-semibold text-gray-900">
                    {stats?.by_status?.interviewing || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
                <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Offers</dt>
                  <dd className="text-3xl font-semibold text-gray-900">
                    {stats?.by_status?.offer || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Top Matches */}
        {topMatches.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Top Job Matches</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {topMatches.map((match) => (
                <div key={match.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-base font-medium text-gray-900">{match.job.title}</h4>
                      <p className="text-sm text-gray-600">{match.job.company}</p>
                      <p className="text-sm text-gray-500">{match.job.location}</p>
                      {match.match_reasons.length > 0 && (
                        <p className="text-sm text-indigo-600 mt-1">
                          {match.match_reasons[0]}
                        </p>
                      )}
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                        {Math.round(match.match_score * 100)}% match
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {topMatches.length === 0 && readyQueue.length === 0 && stats?.total === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Get Started</h3>
            <p className="mt-1 text-sm text-gray-500">
              Upload your resume and set job preferences to start finding opportunities!
            </p>
            <div className="mt-6">
              <button
                onClick={() => router.push('/profile')}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Set Up Profile
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
