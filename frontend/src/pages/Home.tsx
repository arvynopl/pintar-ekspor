// src/pages/Home.tsx
import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Course } from '../types';

interface CourseWithProgress extends Course {
  progress: number;
}

export default function Home() {
  const [recentCourses, setRecentCourses] = useState<CourseWithProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch recent courses with progress
        const response = await api.get('/courses');
        const courses = response.data.slice(0, 4); // Show only 4 recent courses

        // For each course, fetch progress
        const coursesWithProgress = await Promise.all(
          courses.map(async (course: Course) => {
            const progressResponse = await api.get(`/courses/${course.id}/progress`);
            return {
              ...course,
              progress: progressResponse.data.completed ? 100 : 0, // Simplified for now
            };
          })
        );

        setRecentCourses(coursesWithProgress);
      } catch (err) {
        setError('Failed to load recent courses');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
        <div className="grid grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-48 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 bg-red-50 p-4 rounded">
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Welcome Back
      </h1>

      {/* Recent Courses Section */}
      <section className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">
            Continue Learning
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recentCourses.map((course) => (
            <div 
              key={course.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
            >
              <h3 className="font-medium text-gray-900 mb-2">
                {course.title}
              </h3>
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {course.description}
              </p>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all"
                  style={{ width: `${course.progress}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-600 mt-1">
                {course.progress}% complete
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Quick Stats Section */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Quick Stats
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-sm font-medium text-gray-500">
              Courses in Progress
            </h3>
            <p className="text-2xl font-semibold text-gray-900">
              {recentCourses.length}
            </p>
          </div>
          {/* Add more stats cards as needed */}
        </div>
      </section>
    </div>
  );
}