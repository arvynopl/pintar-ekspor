// src/pages/CourseView.tsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';

interface Course {
  id: number;
  title: string;
  description: string;
  content: string;
  created_at: string;
  updated_at?: string;
}

interface CourseProgress {
  completed: boolean;
}

export default function CourseView() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  
  const [course, setCourse] = useState<Course | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCourseData() {
      if (!courseId) return;
      
      try {
        setLoading(true);
        
        // Fetch course details
        const courseResponse = await api.get<Course>(`/courses/${courseId}`);
        setCourse(courseResponse.data);

        // Fetch course progress
        const progressResponse = await api.get<CourseProgress>(`/courses/${courseId}/progress`);
        setProgress(progressResponse.data.completed ? 100 : 0);
      } catch (err) {
        setError('Failed to load course');
        console.error('Error loading course:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchCourseData();
  }, [courseId]);

  const handleUpdateProgress = async () => {
    if (!courseId) return;

    try {
      await api.post(`/courses/${courseId}/progress`, {
        completed: true
      });
      setProgress(100);
    } catch (err) {
      console.error('Failed to update progress:', err);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-full"></div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded">
        <p>{error || 'Course not found'}</p>
        <button 
          onClick={() => navigate('/courses')}
          className="text-sm text-red-700 underline mt-2"
        >
          Return to courses
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Navigation */}
      <button
        onClick={() => navigate('/courses')}
        className="text-blue-600 hover:text-blue-700 flex items-center gap-2"
      >
        ← Back to Courses
      </button>

      {/* Course Header */}
      <div className="border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {course.title}
        </h1>
        <p className="text-gray-600">
          {course.description}
        </p>
      </div>

      {/* Progress Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-lg font-medium text-gray-900">Your Progress</h2>
          <span className="text-sm text-gray-600">{progress}% Complete</span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Complete Button */}
        {progress < 100 && (
          <button
            onClick={handleUpdateProgress}
            className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Mark as Complete
          </button>
        )}
      </div>

      {/* Course Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Course Content
        </h2>
        <div className="prose max-w-none">
          {course.content}
        </div>
      </div>
    </div>
  );
}