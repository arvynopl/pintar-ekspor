// src/components/layout/Sidebar.tsx

import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export default function Sidebar() {
  const { logout } = useAuth();
  const location = useLocation();

  const navigationItems = [
    { path: '/home', label: 'Home', icon: '🏠' },
    { path: '/courses', label: 'Courses', icon: '📚' },
    { path: '/analytics', label: 'Analytics', icon: '📊' },
    { path: '/profile', label: 'Profile', icon: '👤' }
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white border-r border-gray-200 overflow-y-auto">
      <div className="flex flex-col h-full">
        {/* Navigation Section */}
        <div className="flex-1 py-6">
          <div className="px-3 mb-6">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Navigation
            </h2>
          </div>
          
          {navigationItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 mx-3 px-4 py-3 rounded-lg transition-colors duration-150
                ${
                  isActive(item.path)
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }
              `}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </div>
        
        {/* User Actions Section */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-lg text-gray-700 
              hover:bg-gray-50 transition-colors duration-150"
          >
            <span className="text-lg">🚪</span>
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}