// src/components/courses/CourseCard.tsx
import { Link } from 'react-router-dom';
import { Course } from '../../types';

interface CourseCardProps {
  course: Course;
  progress: number;
}

export default function CourseCard({ course, progress }: CourseCardProps) {
  // Convert progress to a percentage between 0-100
  const progressPercentage = Math.min(Math.max(progress, 0), 100);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <Link to={`/courses/${course.id}`} className="block p-4">
        {/* Course header section */}
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            {course.title}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2">
            {course.description}
          </p>
        </div>

        {/* Progress section */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{progressPercentage}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className="bg-blue-600 rounded-full h-2 transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </Link>
    </div>
  );
}