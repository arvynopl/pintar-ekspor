// src/services/auth.service.ts
import axios from 'axios';
import { AuthResponse, User } from '../types';

export class AuthService {
  private baseURL = 'http://localhost:8000';

  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      // Create form data explicitly as OAuth2 expects
      const formData = new URLSearchParams();
      formData.append('grant_type', 'password');
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await axios.post<AuthResponse>(
        `${this.baseURL}/auth/token`,
        formData.toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          }
        }
      );

      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      return response.data;
    } catch (error: any) {
      console.error('Login request failed:', {
        status: error.response?.status,
        data: error.response?.data,
      });
      throw error;
    }
  }

  async register(email: string, password: string): Promise<User> {
    try {
      const response = await axios.post<User>(
        `${this.baseURL}/auth/register`,
        { email, password }
      );
      return response.data;
    } catch (error: any) {
      console.error('Registration failed:', {
        status: error.response?.status,
        data: error.response?.data,
      });
      throw error;
    }
  }

  async logout(): Promise<void> {
    const token = this.getToken();
    if (token) {
      try {
        await axios.post(
          `${this.baseURL}/auth/logout`,
          {},
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

export const authService = new AuthService();