// lib/types.ts
// TypeScript types for the application

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserProfile {
  id: number;
  user_id: number;
  skills: string[];
  education: Education[];
  experience: Experience[];
  desired_roles: string[];
  desired_locations: string[];
  job_type: string;
  min_salary?: number;
  max_salary?: number;
  cover_letters_generated: number;
  cover_letter_limit: number;
}

export interface Education {
  school: string;
  degree: string;
  major?: string;
  gpa?: number;
  graduation_year?: number;
}

export interface Experience {
  company: string;
  title: string;
  duration: string;
  description?: string;
}

export interface JobListing {
  id: number;
  external_id: string;
  source: string;
  title: string;
  company: string;
  location: string;
  salary_min?: number;
  salary_max?: number;
  job_type: string;
  application_url: string;
  posted_date?: string;
  description?: string;
}

export interface JobMatch {
  id: number;
  job: JobListing;
  match_score: number;
  match_reasons: string[];
  status: string;
  created_at: string;
}

export interface JobApplication {
  id: number;
  job: JobListing;
  status: string;
  application_date: string;
  cover_letter?: string;
  notes?: string;
  status_history: StatusHistory[];
  created_at: string;
}

export interface StatusHistory {
  status: string;
  date: string;
  notes: string;
}

export interface ApplicationStats {
  total: number;
  by_status: Record<string, number>;
  recent_applications: number;
}

export interface PreparedApplication {
  id: number;
  job: JobListing;
  cover_letter: string;
  prepared_answers?: string;
  created_at: string;
  status: string;
}
