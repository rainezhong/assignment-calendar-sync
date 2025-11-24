import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Briefcase, Search, Loader2, ExternalLink, MapPin, Building2, TrendingUp, Check } from 'lucide-react';
import { jobsApi } from '../api/jobs';
import type { ScrapeJobsRequest } from '../types';

export default function Jobs() {
  const queryClient = useQueryClient();
  const [searchUrl, setSearchUrl] = useState('');
  const [error, setError] = useState('');

  // Get all jobs
  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.getJobs({ sort_by: 'match_score' }),
  });

  // Scrape mutation
  const scrapeMutation = useMutation({
    mutationFn: (data: ScrapeJobsRequest) => jobsApi.scrapeJobs(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setSearchUrl('');
      setError('');
      alert(`Success! Found ${data.jobs_found} jobs (${data.jobs_new} new)`);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to scrape jobs');
    },
  });

  // Apply mutation
  const applyMutation = useMutation({
    mutationFn: (jobId: number) => jobsApi.applyToJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  const handleScrape = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!searchUrl.trim()) {
      setError('Please enter a LinkedIn job search URL');
      return;
    }

    if (!searchUrl.includes('linkedin.com')) {
      setError('Please enter a valid LinkedIn URL');
      return;
    }

    scrapeMutation.mutate({ search_url: searchUrl, max_jobs: 25 });
  };

  const getMatchScoreColor = (score?: number) => {
    if (!score) return 'bg-gray-100 text-gray-800';
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getMatchScoreBadge = (score?: number) => {
    if (!score) return 'No Match';
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    return 'Possible Match';
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Job Matches</h1>
        <p className="text-gray-600 mt-1">
          Find jobs that match your skills and coursework
        </p>
      </div>

      {/* Scrape Form */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Add Jobs</h2>
        <form onSubmit={handleScrape} className="space-y-3">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              LinkedIn Job Search URL
            </label>
            <input
              type="url"
              value={searchUrl}
              onChange={(e) => setSearchUrl(e.target.value)}
              placeholder="https://www.linkedin.com/jobs/search/?keywords=software%20engineer"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={scrapeMutation.isPending}
            />
            <p className="text-xs text-gray-500 mt-1">
              Search for jobs on LinkedIn, then copy and paste the URL here
            </p>
          </div>

          <button
            type="submit"
            disabled={scrapeMutation.isPending}
            className="btn-primary flex items-center"
          >
            {scrapeMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Scraping Jobs...
              </>
            ) : (
              <>
                <Search className="w-4 h-4 mr-2" />
                Scrape Jobs
              </>
            )}
          </button>
        </form>
      </div>

      {/* Jobs List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading jobs...</p>
          </div>
        </div>
      ) : jobs && jobs.length > 0 ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {jobs.length} Jobs Found
            </h2>
            <p className="text-sm text-gray-600">Sorted by match score</p>
          </div>

          {jobs.map((job) => (
            <div key={job.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  {/* Match Score Badge */}
                  {job.match_score !== undefined && (
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getMatchScoreColor(job.match_score)}`}>
                        <TrendingUp className="w-3 h-3 mr-1" />
                        {job.match_score}% Match
                      </span>
                      <span className="text-xs text-gray-600">
                        {getMatchScoreBadge(job.match_score)}
                      </span>
                    </div>
                  )}

                  {/* Job Title */}
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {job.title}
                  </h3>

                  {/* Company and Location */}
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                    <div className="flex items-center gap-1.5">
                      <Building2 className="w-4 h-4" />
                      <span>{job.company}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-4 h-4" />
                      <span>{job.location}</span>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className="badge badge-secondary">{job.job_type}</span>
                    <span className="badge badge-secondary">{job.remote_type}</span>
                    {job.source && (
                      <span className="badge badge-secondary">
                        {job.source === 'linkedin' ? 'LinkedIn' : job.source}
                      </span>
                    )}
                  </div>

                  {/* Matched Skills */}
                  {job.matched_skills && job.matched_skills.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs font-medium text-gray-700 mb-1">Matched Skills:</p>
                      <div className="flex flex-wrap gap-1">
                        {job.matched_skills.slice(0, 5).map((skill, idx) => (
                          <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700">
                            <Check className="w-3 h-3 mr-1" />
                            {skill}
                          </span>
                        ))}
                        {job.matched_skills.length > 5 && (
                          <span className="text-xs text-gray-500">
                            +{job.matched_skills.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Description */}
                  {job.description && (
                    <p className="text-sm text-gray-700 line-clamp-2 mb-3">
                      {job.description}
                    </p>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <a
                      href={job.application_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-primary text-sm flex items-center"
                    >
                      View on LinkedIn
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                    <button
                      onClick={() => applyMutation.mutate(job.id)}
                      disabled={applyMutation.isPending}
                      className="btn-secondary text-sm"
                    >
                      Mark as Applied
                    </button>
                  </div>
                </div>

                {/* Salary (if available) */}
                {(job.salary_min || job.salary_max) && (
                  <div className="text-right flex-shrink-0">
                    <div className="text-lg font-bold text-gray-900">
                      {job.salary_min && job.salary_max
                        ? `$${(job.salary_min / 1000).toFixed(0)}K - $${(job.salary_max / 1000).toFixed(0)}K`
                        : job.salary_min
                        ? `$${(job.salary_min / 1000).toFixed(0)}K+`
                        : `Up to $${(job.salary_max / 1000).toFixed(0)}K`}
                    </div>
                    <div className="text-xs text-gray-500">Salary</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <Briefcase className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs yet</h3>
          <p className="text-gray-600 mb-4">
            Paste a LinkedIn job search URL above to get started
          </p>
          <p className="text-sm text-gray-500">
            We'll match jobs with your courses and skills
          </p>
        </div>
      )}
    </div>
  );
}
