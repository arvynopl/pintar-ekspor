// src/components/analytics/Dashboard.tsx
import { useState, useEffect, ChangeEvent } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsService } from '../../services/analytics.service';
import { ChartDataPoint, Stat } from '@/types';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';

// Type definitions
interface FileUploaderProps {
  onUpload: (file: File) => Promise<void>;
  isLoading: boolean;
}

interface AnalyticsChartProps {
  data: ChartDataPoint[] | null;
  isLoading: boolean;
  error: string;
}

interface QuickStatsProps {
  stats: Stat[] | null;
  isLoading: boolean;
  error: string;
}

const ALLOWED_FILE_TYPES = {
  'text/csv': ['.csv'],
  'application/json': ['.json']
};

const FileUploader = ({ onUpload, isLoading }: FileUploaderProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');

  const validateFile = (file: File): string => {
    // Check file type
    const validTypes = Object.keys(ALLOWED_FILE_TYPES);
    if (!validTypes.includes(file.type)) {
      return 'Invalid file type. Please upload CSV or JSON files only.';
    }
    
    // Check file size (max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      return 'File size too large. Maximum size is 5MB.';
    }

    return '';
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      const error = validateFile(selectedFile);
      if (error) {
        setError(error);
        setFile(null);
      } else {
        setError('');
        setFile(selectedFile);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    try {
      await onUpload(file);
      setError('');
    } catch (err) {
      setError('Failed to upload file. Please try again.');
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Upload Data</h3>
      <input
        type="file"
        onChange={handleFileChange}
        accept=".csv,.json"
        className="block w-full text-sm text-gray-500 mb-4
          file:mr-4 file:py-2 file:px-4
          file:rounded-full file:border-0
          file:text-sm file:font-semibold
          file:bg-blue-50 file:text-blue-700
          hover:file:bg-blue-100"
        disabled={isLoading}
      />
      {error && (
        <div className="text-red-600 text-sm mb-4">
          {error}
        </div>
      )}
      <button
        onClick={handleUpload}
        disabled={!file || isLoading}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg 
          hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
};

const AnalyticsChart = ({ data, isLoading, error }: AnalyticsChartProps) => {
  if (isLoading) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm h-96 flex items-center justify-center">
        <div className="text-gray-500">Loading chart data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm h-96 flex items-center justify-center">
        <div className="text-red-600">Error loading chart: {error}</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm h-96 flex items-center justify-center">
        <div className="text-gray-500">No data available. Please upload a file to see analytics.</div>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm h-96">
      <h3 className="text-lg font-semibold mb-4">Analytics Overview</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#8884d8" 
            name="Value"
          />
          {data[0]?.forecast !== undefined && (
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#82ca9d"
              strokeDasharray="5 5"
              name="Forecast"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const QuickStats = ({ stats, isLoading, error }: QuickStatsProps) => {
  if (isLoading) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
        <div className="text-gray-500">Loading stats...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
        <div className="text-red-600">Error loading stats</div>
      </div>
    );
  }

  if (!stats || stats.length === 0) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
        <div className="text-gray-500">No stats available</div>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
      <div className="grid grid-cols-2 gap-4">
        {stats.map((stat: Stat, index: number) => (
          <div key={index} className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">{stat.label}</p>
            <p className="text-2xl font-semibold">{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const AnalyticsDashboard = () => {
  const [chartData, setChartData] = useState<ChartDataPoint[] | null>(null);
  const [stats, setStats] = useState<Stat[] | null>(null);
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Initial data load with better error handling
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        setError('');
        
        if (!user) {
          setError('Please log in to access analytics features');
          return;
        }

        const response = await analyticsService.getSummary();
        if (response) {
          setChartData(response.chartData);
          setStats(response.stats);
        }
      } catch (err) {
        console.error('Failed to load initial data:', err);
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          setError('Session expired. Please log in again.');
        } else {
          setError('Failed to load analytics data. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, [user]);  // Add user as dependency to reload when auth state changes

  // Display auth error message if needed
  if (error) {
    return (
      <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
        <p className="font-medium">Error</p>
        <p>{error}</p>
      </div>
    );
  }

  const handleFileUpload = async (file: File) => {
    try {
        setIsLoading(true);
        setError('');
        const data = await analyticsService.uploadFile(file);
        console.log('Received data:', data); // Debug log
        
        if (data) {
            setChartData(data.chartData);
            setStats(data.stats);
        } else {
            console.warn('Received empty data from API');
            setChartData([]);
            setStats([]);
        }
    } catch (err) {
        console.error('File upload failed:', err);
        setError('Failed to process file. Please ensure the file format is correct.');
    } finally {
        setIsLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      await analyticsService.exportData('csv');
    } catch (err) {
      console.error('Export failed:', err);
      setError('Failed to export data. Please try again.');
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        <button 
          onClick={handleExport}
          disabled={!chartData || isLoading}
          className="px-4 py-2 bg-green-600 text-white rounded-lg 
            hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Export Data
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FileUploader onUpload={handleFileUpload} isLoading={isLoading} />
        <QuickStats 
          stats={stats} 
          isLoading={isLoading} 
          error={error} 
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <AnalyticsChart 
          data={chartData} 
          isLoading={isLoading} 
          error={error}
        />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;