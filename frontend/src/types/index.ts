// User types
export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_premium: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Assignment types
export interface Assignment {
  id: number;
  user_id: number;
  course_id: number | null;
  title: string;
  description: string | null;
  course_name: string;
  assignment_type: string;
  due_date: string;
  created_at: string;
  completed_at: string | null;
  is_completed: boolean;
  completion_percentage: number;

  // AI Analysis
  complexity_score: number | null;
  blooms_level: string | null;
  estimated_hours: number | null;
  required_skills: string[];

  // Integration tracking
  source: string;
  source_id: string | null;
  source_url: string | null;
  approved: boolean;

  // Grading
  points_possible: number | null;
  points_earned: number | null;
  grade_percentage: number | null;
  submission_status: string | null;
}

export interface CreateAssignmentRequest {
  title: string;
  description?: string;
  course_name: string;
  assignment_type: string;
  due_date: string;
}

// Course types
export interface Course {
  id: number;
  user_id: number;
  name: string;
  code: string | null;
  semester: string | null;
  instructor: string | null;
  source: string;
  source_id: string | null;
  approved: boolean;
  is_active: boolean;
  created_at: string;
  last_synced: string | null;
}

// Job types
export interface JobListing {
  id: number;
  title: string;
  company: string;
  location: string;
  remote_type: string | null;
  job_type: string;
  description: string | null;
  salary_min: number | null;
  salary_max: number | null;
  application_url: string;
  source: string;
  posted_date: string | null;
}

export interface JobMatch {
  id: number;
  job_id: number;
  match_score: number;
  match_reasons: string[];
  status: string;
  created_at: string;
  job: JobListing;
}

// API Response types
export interface ApiError {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
