import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CheckCircle2, XCircle, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { canvasApi } from '../api/canvas';
import { gmailApi } from '../api/gmail';
import { gradescopeApi } from '../api/gradescope';
import type { CanvasConnectRequest, GradescopeConnectRequest } from '../types';

export default function Settings() {
  const queryClient = useQueryClient();
  const [showCanvasForm, setShowCanvasForm] = useState(false);
  const [canvasToken, setCanvasToken] = useState('');
  const [canvasUrl, setCanvasUrl] = useState('');
  const [error, setError] = useState('');

  // Get Canvas connection status
  const { data: canvasStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['canvas-status'],
    queryFn: canvasApi.getStatus,
  });

  // Connect mutation
  const connectMutation = useMutation({
    mutationFn: (data: CanvasConnectRequest) => canvasApi.connect(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['canvas-status'] });
      setShowCanvasForm(false);
      setCanvasToken('');
      setCanvasUrl('');
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to connect Canvas account');
    },
  });

  // Disconnect mutation
  const disconnectMutation = useMutation({
    mutationFn: canvasApi.disconnect,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['canvas-status'] });
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
    },
  });

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: canvasApi.sync,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
      queryClient.invalidateQueries({ queryKey: ['canvas-status'] });
      alert(`Sync successful!\n\nCourses: ${data.courses_found} (${data.courses_new} new)\nAssignments: ${data.assignments_found} (${data.assignments_new} new)`);
    },
    onError: (err: any) => {
      alert(`Sync failed: ${err.response?.data?.detail || 'Unknown error'}`);
    },
  });

  const handleConnect = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!canvasToken.trim() || !canvasUrl.trim()) {
      setError('Please fill in all fields');
      return;
    }

    connectMutation.mutate({
      api_token: canvasToken,
      base_url: canvasUrl,
    });
  };

  const handleDisconnect = () => {
    if (confirm('Are you sure you want to disconnect your Canvas account?')) {
      disconnectMutation.mutate();
    }
  };

  const handleSync = () => {
    if (confirm('Start syncing courses and assignments from Canvas?')) {
      syncMutation.mutate();
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

      {/* Canvas Integration */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Canvas LMS</h2>
            <p className="text-sm text-gray-600">Connect your Canvas account to sync courses and assignments</p>
          </div>
          {statusLoading ? (
            <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          ) : canvasStatus?.connected ? (
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          ) : (
            <XCircle className="w-5 h-5 text-gray-400" />
          )}
        </div>

        {canvasStatus?.connected ? (
          <div className="space-y-4">
            {/* Connection Info */}
            <div className="bg-green-50 border border-green-200 rounded-md p-4">
              <div className="flex items-start">
                <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-green-800">Connected to Canvas</p>
                  <p className="text-sm text-green-700 mt-1 break-all">
                    {canvasStatus.institution_url}
                  </p>
                  {canvasStatus.last_synced && (
                    <p className="text-xs text-green-600 mt-2">
                      Last synced: {new Date(canvasStatus.last_synced).toLocaleString()}
                    </p>
                  )}
                  {canvasStatus.last_sync_status === 'failed' && canvasStatus.last_error && (
                    <div className="mt-2 text-xs text-red-600">
                      Last sync error: {canvasStatus.last_error}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={handleSync}
                disabled={syncMutation.isPending}
                className="btn-primary flex items-center"
              >
                {syncMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Syncing...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Sync Now
                  </>
                )}
              </button>
              <button
                onClick={handleDisconnect}
                disabled={disconnectMutation.isPending}
                className="btn-secondary text-red-600 hover:bg-red-50"
              >
                {disconnectMutation.isPending ? 'Disconnecting...' : 'Disconnect'}
              </button>
            </div>

            {/* Sync Instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <div className="flex">
                <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
                <div className="text-sm text-blue-700">
                  <p className="font-medium mb-1">After syncing:</p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>New courses and assignments will appear in your dashboard</li>
                    <li>Review and approve synced items before they appear in your timeline</li>
                    <li>Check the Assignments page to manage your synced data</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div>
            {!showCanvasForm ? (
              <button
                onClick={() => setShowCanvasForm(true)}
                className="btn-primary"
              >
                Connect Canvas
              </button>
            ) : (
              <form onSubmit={handleConnect} className="space-y-4">
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-start">
                    <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-red-700">{error}</span>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Canvas Institution URL
                  </label>
                  <input
                    type="text"
                    value={canvasUrl}
                    onChange={(e) => setCanvasUrl(e.target.value)}
                    placeholder="e.g., umich.instructure.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={connectMutation.isPending}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Enter your Canvas institution URL (without https://)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    API Access Token
                  </label>
                  <input
                    type="password"
                    value={canvasToken}
                    onChange={(e) => setCanvasToken(e.target.value)}
                    placeholder="Your Canvas API token"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={connectMutation.isPending}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get your token from Canvas: Account → Settings → New Access Token
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={connectMutation.isPending}
                    className="btn-primary"
                  >
                    {connectMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
                        Connecting...
                      </>
                    ) : (
                      'Connect'
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCanvasForm(false);
                      setError('');
                      setCanvasToken('');
                      setCanvasUrl('');
                    }}
                    disabled={connectMutation.isPending}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        )}
      </div>

      {/* Gmail Integration */}
      <GmailIntegration />

      {/* Gradescope Integration */}
      <GradescopeIntegration />
    </div>
  );
}

// Gmail Integration Component
function GmailIntegration() {
  const queryClient = useQueryClient();

  const { data: gmailStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['gmail-status'],
    queryFn: gmailApi.getStatus,
  });

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: () => gmailApi.sync({ days_back: 30, max_results: 100 }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['gmail-status'] });
      alert(`Sync successful!\n\nEmails: ${data.emails_found} (${data.emails_new} new, ${data.emails_updated} updated)`);
    },
    onError: (err: any) => {
      alert(`Sync failed: ${err.response?.data?.detail || 'Unknown error'}`);
    },
  });

  // Disconnect mutation
  const disconnectMutation = useMutation({
    mutationFn: gmailApi.disconnect,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gmail-status'] });
    },
  });

  const handleConnect = async () => {
    try {
      const { auth_url } = await gmailApi.getAuthUrl();
      // Open OAuth URL in current window
      window.location.href = auth_url;
    } catch (err: any) {
      alert(`Failed to connect Gmail: ${err.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const handleDisconnect = () => {
    if (confirm('Are you sure you want to disconnect your Gmail account?')) {
      disconnectMutation.mutate();
    }
  };

  const handleSync = () => {
    if (confirm('Start syncing emails from Gmail?')) {
      syncMutation.mutate();
    }
  };

  return (
    <div className="card mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Gmail</h2>
          <p className="text-sm text-gray-600">Connect Gmail to sync assignment-related emails</p>
        </div>
        {statusLoading ? (
          <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
        ) : gmailStatus?.connected ? (
          <CheckCircle2 className="w-5 h-5 text-green-500" />
        ) : (
          <XCircle className="w-5 h-5 text-gray-400" />
        )}
      </div>

      {gmailStatus?.connected ? (
        <div className="space-y-4">
          {/* Connection Info */}
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-start">
              <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-green-800">Connected to Gmail</p>
                {gmailStatus.email && (
                  <p className="text-sm text-green-700 mt-1 break-all">
                    {gmailStatus.email}
                  </p>
                )}
                {gmailStatus.last_synced && (
                  <p className="text-xs text-green-600 mt-2">
                    Last synced: {new Date(gmailStatus.last_synced).toLocaleString()}
                  </p>
                )}
                {gmailStatus.emails_count !== undefined && (
                  <p className="text-xs text-green-600 mt-1">
                    {gmailStatus.emails_count} emails synced
                  </p>
                )}
                {gmailStatus.last_sync_status === 'failed' && gmailStatus.last_error && (
                  <div className="mt-2 text-xs text-red-600">
                    Last sync error: {gmailStatus.last_error}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleSync}
              disabled={syncMutation.isPending}
              className="btn-primary flex items-center"
            >
              {syncMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync Now
                </>
              )}
            </button>
            <button
              onClick={handleDisconnect}
              disabled={disconnectMutation.isPending}
              className="btn-secondary text-red-600 hover:bg-red-50"
            >
              {disconnectMutation.isPending ? 'Disconnecting...' : 'Disconnect'}
            </button>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">What gets synced:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Emails with keywords: assignment, homework, due, deadline, exam, quiz</li>
                  <li>Only academic emails from .edu domains and learning platforms</li>
                  <li>Emails from the last 30 days</li>
                  <li>Maximum 100 emails per sync</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <button onClick={handleConnect} className="btn-primary">
            Connect Gmail
          </button>
          <p className="text-xs text-gray-500 mt-2">
            We'll only access emails related to assignments and coursework
          </p>
        </div>
      )}
    </div>
  );
}

// Gradescope Integration Component
function GradescopeIntegration() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const { data: gradescopeStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['gradescope-status'],
    queryFn: gradescopeApi.getStatus,
  });

  // Connect mutation
  const connectMutation = useMutation({
    mutationFn: (data: GradescopeConnectRequest) => gradescopeApi.connect(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gradescope-status'] });
      setShowForm(false);
      setEmail('');
      setPassword('');
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to connect Gradescope account');
    },
  });

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: () => gradescopeApi.sync(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['gradescope-status'] });
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
      alert(`Sync successful!\n\nCourses: ${data.courses_found} (${data.courses_new} new)\nAssignments: ${data.assignments_found} (${data.assignments_new} new)`);
    },
    onError: (err: any) => {
      alert(`Sync failed: ${err.response?.data?.detail || 'Unknown error'}`);
    },
  });

  // Disconnect mutation
  const disconnectMutation = useMutation({
    mutationFn: gradescopeApi.disconnect,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gradescope-status'] });
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
    },
  });

  const handleConnect = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields');
      return;
    }

    connectMutation.mutate({ email, password });
  };

  const handleDisconnect = () => {
    if (confirm('Are you sure you want to disconnect your Gradescope account?')) {
      disconnectMutation.mutate();
    }
  };

  const handleSync = () => {
    if (confirm('Start syncing courses and assignments from Gradescope? This may take a minute.')) {
      syncMutation.mutate();
    }
  };

  return (
    <div className="card mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Gradescope</h2>
          <p className="text-sm text-gray-600">Connect Gradescope to sync assignments and grades</p>
        </div>
        {statusLoading ? (
          <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
        ) : gradescopeStatus?.connected ? (
          <CheckCircle2 className="w-5 h-5 text-green-500" />
        ) : (
          <XCircle className="w-5 h-5 text-gray-400" />
        )}
      </div>

      {gradescopeStatus?.connected ? (
        <div className="space-y-4">
          {/* Connection Info */}
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-start">
              <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-green-800">Connected to Gradescope</p>
                {gradescopeStatus.email && (
                  <p className="text-sm text-green-700 mt-1 break-all">
                    {gradescopeStatus.email}
                  </p>
                )}
                {gradescopeStatus.last_synced && (
                  <p className="text-xs text-green-600 mt-2">
                    Last synced: {new Date(gradescopeStatus.last_synced).toLocaleString()}
                  </p>
                )}
                {gradescopeStatus.courses_count !== undefined && gradescopeStatus.assignments_count !== undefined && (
                  <p className="text-xs text-green-600 mt-1">
                    {gradescopeStatus.courses_count} courses, {gradescopeStatus.assignments_count} assignments
                  </p>
                )}
                {gradescopeStatus.last_sync_status === 'failed' && gradescopeStatus.last_error && (
                  <div className="mt-2 text-xs text-red-600">
                    Last sync error: {gradescopeStatus.last_error}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleSync}
              disabled={syncMutation.isPending}
              className="btn-primary flex items-center"
            >
              {syncMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync Now
                </>
              )}
            </button>
            <button
              onClick={handleDisconnect}
              disabled={disconnectMutation.isPending}
              className="btn-secondary text-red-600 hover:bg-red-50"
            >
              {disconnectMutation.isPending ? 'Disconnecting...' : 'Disconnect'}
            </button>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">Note about syncing:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Syncing uses web scraping and may take 30-60 seconds</li>
                  <li>All courses and assignments will be fetched</li>
                  <li>Review and approve synced items in Assignments page</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div>
          {!showForm ? (
            <button onClick={() => setShowForm(true)} className="btn-primary">
              Connect Gradescope
            </button>
          ) : (
            <form onSubmit={handleConnect} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
                  <span className="text-sm text-red-700">{error}</span>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Gradescope Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@university.edu"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={connectMutation.isPending}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Gradescope Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Your Gradescope password"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={connectMutation.isPending}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Your password is encrypted and stored securely
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={connectMutation.isPending}
                  className="btn-primary"
                >
                  {connectMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin inline" />
                      Connecting...
                    </>
                  ) : (
                    'Connect'
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setError('');
                    setEmail('');
                    setPassword('');
                  }}
                  disabled={connectMutation.isPending}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
