// src/types/index.ts
export enum UserRole {
  PUBLIC = "public",
  DEVELOPER = "developer",
  ADMIN = "admin"
}

export interface User {
  id: number;
  email: string;
  role: UserRole;
  created_at: string;
  api_key?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  content: string;
  created_at: string;
  updated_at?: string;
}

export interface ChartDataPoint {
  date: string;
  value: number;
  forecast?: number;
}

export interface Stat {
  label: string;
  value: string | number;
}

export interface AnalysisResult {
  trend: {
      direction: string;
      strength: number;
      significant: boolean;
  };
  growth: {
      total: string | null;
      recent: string | null;
  };
  current_stats: {
      last_value: number | null;
      mean: number | null;
      std: number | null;
  };
}

// This represents what the API returns
export interface ApiAnalyticsSummary {
  timestamp: string;
  analysis: {
      [key: string]: AnalysisResult;
  };
  quality_metrics: {
      [key: string]: any;
  };
  visualizations?: {
      [key: string]: any;
  };
}

// This represents what our UI components expect
export interface UiAnalyticsSummary {
  chartData: ChartDataPoint[];
  stats: Stat[];
}