// src/pages/Courses.tsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import SearchAndSort from '../components/courses/SearchAndSort';
import CourseCard from '../components/courses/CourseCard';

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

interface CourseWithProgress extends Course {
  progress: number;
}

export default function Courses() {
  // State management
  const [courses, setCourses] = useState<CourseWithProgress[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<CourseWithProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortConfig, setSortConfig] = useState<{
    option: 'title' | 'progress';
    direction: 'asc' | 'desc';
  }>({
    option: 'title',
    direction: 'asc'
  });

  // Fetch courses and their progress
  useEffect(() => {
    async function fetchCourses() {
      try {
        setLoading(true);
        
        // Fetch all courses
        const coursesResponse = await api.get('/courses');
        const coursesData: Course[] = coursesResponse.data;

        // Fetch progress for each course
        const coursesWithProgress = await Promise.all(
          coursesData.map(async (course: Course) => {
            try {
              const progressResponse = await api.get<CourseProgress>(
                `/courses/${course.id}/progress`
              );
              return {
                ...course,
                progress: progressResponse.data.completed ? 100 : 0,
              };
            } catch (err) {
              console.error(`Failed to fetch progress for course ${course.id}`, err);
              return {
                ...course,
                progress: 0,
              };
            }
          })
        );

        setCourses(coursesWithProgress);
        setFilteredCourses(coursesWithProgress);
        
      } catch (err) {
        setError('Failed to load courses');
        console.error('Error fetching courses:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchCourses();
  }, []);

  // Search functionality
  const handleSearch = (query: string) => {
    const searchTerm = query.toLowerCase();
    let filtered = courses.filter(
      (course) =>
        course.title.toLowerCase().includes(searchTerm) ||
        course.description.toLowerCase().includes(searchTerm)
    );
    
    // Apply current sort to filtered results
    sortCourses(filtered, sortConfig.option, sortConfig.direction);
  };

  // Sort functionality
  const sortCourses = (
    coursesToSort: CourseWithProgress[],
    option: 'title' | 'progress',
    direction: 'asc' | 'desc'
  ) => {
    const sorted = [...coursesToSort].sort((a, b) => {
      if (option === 'title') {
        return direction === 'asc'
          ? a.title.localeCompare(b.title)
          : b.title.localeCompare(a.title);
      } else {
        return direction === 'asc'
          ? a.progress - b.progress
          : b.progress - a.progress;
      }
    });
    setFilteredCourses(sorted);
  };

  const handleSort = (option: 'title' | 'progress', direction: 'asc' | 'desc') => {
    setSortConfig({ option, direction });
    sortCourses(filteredCourses, option, direction);
  };

  // Loading state
  if (loading) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse">
          {/* Search bar placeholder */}
          <div className="h-10 bg-gray-200 rounded max-w-md mb-8"></div>
          
          {/* Course cards placeholder */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
        <p>{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="text-sm text-red-700 underline mt-2"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Available Courses
        </h1>
        <p className="text-gray-600">
          Browse through our collection of courses and track your progress
        </p>
      </div>

      {/* Search and Sort */}
      <div className="max-w-md">
        <SearchAndSort onSearch={handleSearch} onSort={handleSort} />
      </div>

      {/* Courses Grid */}
      {filteredCourses.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No courses found matching your search.</p>
          <button 
            onClick={() => {
              handleSearch('');
              setSortConfig({ option: 'title', direction: 'asc' });
            }}
            className="text-blue-600 hover:text-blue-700 text-sm mt-2"
          >
            Clear search and filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <Link 
              key={course.id} 
              to={`/courses/${course.id}`}
              className="block transition-transform hover:-translate-y-1"
            >
              <CourseCard
                course={course}
                progress={course.progress}
              />
            </Link>
          ))}
        </div>
      )}

      {/* Course Count */}
      <div className="text-sm text-gray-500">
        Showing {filteredCourses.length} of {courses.length} courses
      </div>
    </div>
  );
}