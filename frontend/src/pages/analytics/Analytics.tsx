// src/pages/analytics/Analytics.tsx
import AnalyticsDashboard from '../../components/analytics/Dashboard';
import { useAuth } from '../../contexts/AuthContext';
import { Navigate } from 'react-router-dom';

export default function Analytics() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="container mx-auto px-4">
      <AnalyticsDashboard />
    </div>
  );
}