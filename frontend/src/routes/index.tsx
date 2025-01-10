// src/routes/index.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import Layout from '../components/layout/Layout';
import LoadingSpinner from '../components/layout/common/LoadingSpinner';
import ProtectedRoute from '../components/auth/ProtectedRoute';

// Lazy load pages
const Landing = lazy(() => import('../pages/Landing'));
const Login = lazy(() => import('../pages/auth/Login'));
const Register = lazy(() => import('../pages/auth/Register'));
const Home = lazy(() => import('../pages/Home'));
const Profile = lazy(() => import('../pages/Profile'));
const Analytics = lazy(() => import('../pages/analytics/Analytics'));
const CourseAnalytics = lazy(() => import('../pages/analytics/CourseAnalytics'));
const Courses = lazy(() => import('../pages/Courses'));
const CourseView = lazy(() => import('../pages/CourseView'));

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <Landing />
          </Suspense>
        ),
      },
      {
        path: 'login',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <Login />
          </Suspense>
        ),
      },
      {
        path: 'register',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <Register />
          </Suspense>
        ),
      },
      {
        path: 'home',
        element: (
          <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <Home />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: 'courses',
        element: (
          <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <Courses />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: 'courses/:courseId',
        element: (
          <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <CourseView />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <Suspense fallback={<LoadingSpinner />}>
              <Profile />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: 'analytics',
        children: [
          {
            index: true,
            element: (
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <Analytics />
                </Suspense>
              </ProtectedRoute>
            ),
          },
          {
            path: ':courseId',
            element: (
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner />}>
                  <CourseAnalytics />
                </Suspense>
              </ProtectedRoute>
            ),
          },
        ],
      },
    ],
  },
]);

export function Routes() {
  return <RouterProvider router={router} />;
}