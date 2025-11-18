// app/profile/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { UserProfile } from '@/lib/types';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  // Form fields
  const [desiredJobTitles, setDesiredJobTitles] = useState('');
  const [desiredLocations, setDesiredLocations] = useState('');
  const [minSalary, setMinSalary] = useState('');
  const [experienceYears, setExperienceYears] = useState('');
  const [skills, setSkills] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const data = await api.getUserProfile();
      setProfile(data);

      // Populate form fields
      if (data.job_preferences) {
        setDesiredJobTitles(data.job_preferences.desired_job_titles?.join(', ') || '');
        setDesiredLocations(data.job_preferences.desired_locations?.join(', ') || '');
        setMinSalary(data.job_preferences.min_salary?.toString() || '');
      }
      setExperienceYears(data.experience_years?.toString() || '');
      setSkills(data.skills?.join(', ') || '');
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleResumeUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      setMessage('Please upload a PDF file');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setMessage('File size must be less than 5MB');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      await api.uploadResume(file);
      setMessage('Resume uploaded successfully!');
      await loadProfile(); // Reload to show new resume
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Failed to upload resume');
    } finally {
      setUploading(false);
    }
  }

  async function handleSavePreferences(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const preferences = {
        desired_job_titles: desiredJobTitles.split(',').map(s => s.trim()).filter(Boolean),
        desired_locations: desiredLocations.split(',').map(s => s.trim()).filter(Boolean),
        min_salary: minSalary ? parseInt(minSalary) : undefined,
      };

      const profileData = {
        experience_years: experienceYears ? parseInt(experienceYears) : undefined,
        skills: skills.split(',').map(s => s.trim()).filter(Boolean),
      };

      await Promise.all([
        api.updateJobPreferences(preferences),
        api.updateProfile(profileData),
      ]);

      setMessage('Preferences saved successfully!');
      await loadProfile();
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Failed to save preferences');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
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
              <span className="text-gray-600">{user?.email}</span>
              <button onClick={logout} className="text-gray-700 hover:text-indigo-600">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Profile Settings</h2>
          <p className="mt-2 text-gray-600">Manage your resume, preferences, and job search criteria</p>
        </div>

        {/* Message Banner */}
        {message && (
          <div className={`mb-6 rounded-lg p-4 ${
            message.includes('success')
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          }`}>
            <p className={`text-sm ${
              message.includes('success') ? 'text-green-800' : 'text-red-800'
            }`}>
              {message}
            </p>
          </div>
        )}

        {/* Resume Upload Section */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Resume</h3>
          </div>
          <div className="p-6">
            {profile?.resume_url ? (
              <div className="mb-4 p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-800">Resume uploaded</p>
                    <p className="text-xs text-green-600">
                      Last updated: {new Date(profile.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mb-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-sm text-yellow-800">
                  No resume uploaded yet. Upload your resume to start receiving job matches!
                </p>
              </div>
            )}

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 transition-colors">
              <input
                type="file"
                id="resume-upload"
                accept=".pdf"
                onChange={handleResumeUpload}
                className="hidden"
                disabled={uploading}
              />
              <label
                htmlFor="resume-upload"
                className="cursor-pointer"
              >
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">
                  {uploading ? 'Uploading...' : profile?.resume_url ? 'Upload new resume (PDF)' : 'Upload resume (PDF)'}
                </p>
                <p className="text-xs text-gray-500">Max 5MB</p>
              </label>
            </div>

            <div className="mt-4 text-sm text-gray-600">
              <p className="font-medium mb-2">Why we need your resume:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>AI analyzes your experience to find best-fit jobs</li>
                <li>Automatically generates personalized cover letters</li>
                <li>Pre-fills applications with your information</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Job Preferences Form */}
        <form onSubmit={handleSavePreferences}>
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Job Preferences</h3>
            </div>
            <div className="p-6 space-y-6">
              {/* Desired Job Titles */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Desired Job Titles
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g., Software Engineer, Data Analyst, Product Manager"
                  value={desiredJobTitles}
                  onChange={(e) => setDesiredJobTitles(e.target.value)}
                />
                <p className="mt-1 text-xs text-gray-500">Separate multiple titles with commas</p>
              </div>

              {/* Desired Locations */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Desired Locations
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g., San Francisco, Remote, New York"
                  value={desiredLocations}
                  onChange={(e) => setDesiredLocations(e.target.value)}
                />
                <p className="mt-1 text-xs text-gray-500">Separate multiple locations with commas</p>
              </div>

              {/* Min Salary */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Minimum Salary (USD/year)
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g., 80000"
                  value={minSalary}
                  onChange={(e) => setMinSalary(e.target.value)}
                />
              </div>

              {/* Experience Years */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Years of Experience
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g., 2"
                  value={experienceYears}
                  onChange={(e) => setExperienceYears(e.target.value)}
                />
              </div>

              {/* Skills */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Skills
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g., Python, JavaScript, React, SQL"
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                />
                <p className="mt-1 text-xs text-gray-500">Separate multiple skills with commas</p>
              </div>

              {/* Usage Stats */}
              {profile && (
                <div className="pt-6 border-t border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3">Usage Statistics</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-xs text-gray-600">Cover Letters Used</p>
                      <p className="text-2xl font-semibold text-gray-900">
                        {profile.cover_letters_used || 0}
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-xs text-gray-600">Monthly Limit</p>
                      <p className="text-2xl font-semibold text-gray-900">
                        10
                      </p>
                    </div>
                  </div>
                  <p className="mt-2 text-xs text-gray-500">
                    You have {10 - (profile.cover_letters_used || 0)} free cover letters remaining this month
                  </p>
                </div>
              )}

              {/* Save Button */}
              <div className="pt-4">
                <button
                  type="submit"
                  disabled={saving}
                  className="w-full px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Preferences'}
                </button>
              </div>
            </div>
          </div>
        </form>

        {/* How It Works Section */}
        <div className="mt-8 bg-indigo-50 rounded-lg p-6 border border-indigo-200">
          <h3 className="text-lg font-semibold text-indigo-900 mb-3">How the Auto-Prep System Works</h3>
          <ol className="space-y-3 text-sm text-indigo-800">
            <li className="flex items-start">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-600 text-white text-xs font-bold mr-3 flex-shrink-0">1</span>
              <span><strong>Daily Job Search:</strong> Every day at 8 AM, the system searches for jobs matching your preferences</span>
            </li>
            <li className="flex items-start">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-600 text-white text-xs font-bold mr-3 flex-shrink-0">2</span>
              <span><strong>AI Matching:</strong> Jobs are scored based on your resume, skills, and preferences</span>
            </li>
            <li className="flex items-start">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-600 text-white text-xs font-bold mr-3 flex-shrink-0">3</span>
              <span><strong>Auto-Prep:</strong> For top matches, AI generates a personalized cover letter and prepares the application</span>
            </li>
            <li className="flex items-start">
              <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-600 text-white text-xs font-bold mr-3 flex-shrink-0">4</span>
              <span><strong>Your Review:</strong> You review the prepared applications and tap "Submit" when ready</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
