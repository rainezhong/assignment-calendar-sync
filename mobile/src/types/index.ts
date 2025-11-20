/**
 * TypeScript type definitions for the app.
 */

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_premium: boolean;
  created_at: string;
}

export interface Assignment {
  id: number;
  title: string;
  description: string | null;
  course_name: string;
  assignment_type: string;
  due_date: string;
  is_completed: boolean;
  completion_percentage: number;
  complexity_score: number | null;
  blooms_level: string | null;
  estimated_hours: number | null;
  actual_hours_spent: number;
  created_at: string;
}

export interface ComplexityAnalysis {
  complexity_score: number;
  blooms_level: string;
  cognitive_score: number;
  estimated_hours: number;
  factors: Record<string, any>;
  required_skills: string[];
}

export interface ResourceRecommendation {
  title: string;
  type: string;
  url: string | null;
  relevance_score: number;
  description: string | null;
}

export interface HealthScore {
  overall_score: number;
  completion_rate: number;
  time_management_score: number;
  stress_level: number;
  productivity_score: number;
  trend: string;
}

export interface RiskAssessment {
  assignment_id: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  probability: number;
  confidence: number;
  risk_factors: Array<{
    factor: string;
    score: number;
    description: string;
  }>;
  suggested_actions: string[];
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
