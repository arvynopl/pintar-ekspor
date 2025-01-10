// src/services/analytics.service.ts
import axios, { AxiosRequestConfig } from 'axios';
import { api } from './api';
import { UiAnalyticsSummary } from '@/types';

// Type definitions
export interface DetailedAnalysis {
  trend: {
    direction: 'increasing' | 'decreasing' | 'stable' | 'unknown';
    strength: number | null;
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
  forecast?: {
    available: boolean;
    metrics: {
      mae: number | null;
      rmse: number | null;
      std_error: number | null;
    } | null;
  };
}

class AnalyticsService {
  private async request<T>(endpoint: string, options: AxiosRequestConfig = {}): Promise<T> {
    try {
        const response = await api({
            url: `/analytics${endpoint}`,
            ...options,
            headers: {
                ...options.headers,
                'Content-Type': options.headers?.['Content-Type'] || 'application/json',
            },
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            const message = error.response?.data?.detail || error.message;
            console.error('Analytics service error:', message);
            throw new Error(`Analytics service error: ${message}`);
        }
        throw error;
    }
  }

  // Get initial data using test.json
  async getSummary(): Promise<UiAnalyticsSummary> {
    try {
      // Fetch test.json from public folder
      const response = await fetch('/data/test.json');
      const blob = await response.blob();
      const file = new File([blob], 'test.json', { type: 'application/json' });
      
      // Use the existing analyze endpoint
      return this.uploadFile(file);
    } catch (error) {
      console.error('Failed to load initial data:', error);
      // Return empty data structure if initial load fails
      return {
        chartData: [],
        stats: []
      };
    }
  }

  // Upload file for analysis
  async uploadFile(file: File): Promise<UiAnalyticsSummary> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<UiAnalyticsSummary>('/analyze', {
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
  }

  // Quick analysis for specific category
  async quickAnalysis(file: File, category?: string): Promise<UiAnalyticsSummary> {
    const formData = new FormData();
    formData.append('file', file);

    const endpoint = category ? `/quick-analysis?category=${category}` : '/quick-analysis';
    
    return this.request<UiAnalyticsSummary>(endpoint, {
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // Get detailed analysis
  async getDetailedAnalysis(params: {
    startDate?: string;
    endDate?: string;
    category?: string;
  }): Promise<DetailedAnalysis> {
    return this.request<DetailedAnalysis>('/detailed', {
      method: 'GET',
      params,
    });
  }

  // Export analytics data
  async exportData(format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await this.request<Blob>('/export', {
      method: 'GET',
      params: { format },
      responseType: 'blob',
    });

    // Generate filename based on current date
    const date = new Date().toISOString().split('T')[0];
    const filename = `analytics_export_${date}.${format}`;

    // Trigger download
    const url = window.URL.createObjectURL(new Blob([response]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return response;
  }
}

export const analyticsService = new AnalyticsService();