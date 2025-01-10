// src/contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, UserRole } from '@/types';
import { authService } from '@/services/auth.service';
import { jwtDecode } from 'jwt-decode';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUserData: () => void;
}

interface JWTPayload {
  sub: string;      // email
  role: string;     // user role
  id: number;       // user id
  created_at: string; // user creation date
  api_key?: string;   // api key will be included after role upgrade
  exp: number;      // token expiration
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper function to validate role
const isValidRole = (role: string): role is UserRole => {
  return ['public', 'developer', 'admin'].includes(role);
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Function to extract user info from token
  const getUserFromToken = (token: string): User | null => {
    try {
      const decoded = jwtDecode<JWTPayload>(token);
      
      if (!isValidRole(decoded.role)) {
        console.error('Invalid role in token:', decoded.role);
        return null;
      }

      return {
        id: decoded.id,
        email: decoded.sub,
        role: decoded.role as UserRole,
        created_at: decoded.created_at,
        ...(decoded.api_key && { api_key: decoded.api_key })
      };
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  };

    // Function to refresh user data from token
    const refreshUserData = () => {
      const token = authService.getToken();
      if (token) {
        const userData = getUserFromToken(token);
        if (userData) {
          setUser(userData);
        }
      }
    };

    useEffect(() => {
      const initAuth = async () => {
        const token = authService.getToken();
        if (token) {
          try {
            const userData = getUserFromToken(token);
            if (userData) {
              setUser(userData);
            } else {
              await authService.logout();
            }
          } catch (error) {
            console.error('Auth initialization error:', error);
            await authService.logout();
          }
        }
        setLoading(false);
      };
  
      initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password);
    const userData = getUserFromToken(response.access_token);
    if (userData) {
      setUser(userData);
    } else {
      throw new Error('Invalid token received');
    }
  };

  const register = async (email: string, password: string) => {
    await authService.register(email, password);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUserData }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}