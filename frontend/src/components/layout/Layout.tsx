// src/components/layout/Layout.tsx

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useAuth } from '../../contexts/AuthContext';

const Layout = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main Navigation */}
      <Navbar 
        isMobileMenuOpen={isMobileMenuOpen} 
        setIsMobileMenuOpen={setIsMobileMenuOpen} 
      />
      
      {/* Sidebar for authenticated users */}
      {user && <Sidebar />}

      {/* Main Content */}
      <main className={`pt-16 ${user ? 'pl-64' : ''}`}>
        <div className="p-6">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 mt-auto border-t">
        <div className="container mx-auto px-6 py-8">
          <p className="text-center text-gray-600">
            © {new Date().getFullYear()} Pintar Ekspor. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;