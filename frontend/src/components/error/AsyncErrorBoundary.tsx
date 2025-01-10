// src/components/error/AsyncErrorBoundary.tsx
import { Suspense } from 'react';
import { ErrorBoundary } from './ErrorBoundary';
import LoadingSpinner from '../layout/common/LoadingSpinner';

interface AsyncBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function AsyncBoundary({ children, fallback }: AsyncBoundaryProps) {
  return (
    <ErrorBoundary fallback={fallback}>
      <Suspense fallback={<LoadingSpinner />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}