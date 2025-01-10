// src/services/profile.service.ts
import { api } from './api';
import { UserRole } from '../types';

interface ApiKeyResponse {
  api_key: string;
  rate_limit: {
    requests_per_hour: number;
    window_size: string;
  };
}

export const profileService = {
  // Request role upgrade to developer
  upgradeRole: async (email: string): Promise<void> => {
    await api.post('/auth/upgrade-role', {
      email,
      new_role: UserRole.DEVELOPER
    });
  },

  // Generate new API key
  generateApiKey: async (): Promise<ApiKeyResponse> => {
    const response = await api.post('/auth/api-key/generate');
    return response.data;
  }
};

export default profileService;