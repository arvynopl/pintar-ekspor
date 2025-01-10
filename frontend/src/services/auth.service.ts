// src/services/auth.service.ts
import { api } from './api';
import { AuthResponse, User } from '../types';

export class AuthService {
    async login(email: string, password: string): Promise<AuthResponse> {
        try {
            const formData = new URLSearchParams();
            formData.append('grant_type', 'password');
            formData.append('username', email);
            formData.append('password', password);
            
            // Use the api instance which has the normalized baseURL
            const response = await api.post<AuthResponse>(
                'auth/token',  // Remove leading slash
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
            // Use the api instance which has the normalized baseURL
            const response = await api.post<User>(
                'auth/register',  // Remove leading slash
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
                // Use the api instance which has the normalized baseURL
                await api.post('auth/logout');
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