// src/hooks/useRoleCheck.ts
import { useAuth } from '../contexts/AuthContext';

type RoleCheckFunction = {
  isAdmin: () => boolean;
  isDeveloper: () => boolean;
  hasRole: (role: string) => boolean;
};

export function useRoleCheck(): RoleCheckFunction {
  const { user } = useAuth();

  return {
    isAdmin: () => user?.role === 'admin',
    isDeveloper: () => user?.role === 'developer' || user?.role === 'admin',
    hasRole: (role: string) => user?.role === role,
  };
}