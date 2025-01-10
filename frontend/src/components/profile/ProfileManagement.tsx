// src/components/profile/ProfileManagement.tsx
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { UserRole } from '../../types';
import { api } from '../../services/api';

interface UpgradeResponse {
  api_key: string;
  role: UserRole;
}

const ProfileManagement = () => {
  const { user, refreshUserData } = useAuth();
  const [showApiKey, setShowApiKey] = useState(false);
  const [upgradeSuccess, setUpgradeSuccess] = useState(false);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);

  // Role upgrade mutation with improved success handling
  const upgradeRoleMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post<UpgradeResponse>('/auth/upgrade-role', {
        email: user?.email,
        new_role: UserRole.DEVELOPER
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Show the newly generated API key
      setNewApiKey(data.api_key);
      setUpgradeSuccess(true);
      setShowApiKey(true);
      // Refresh the user data in AuthContext
      refreshUserData();
    },
    onError: (error) => {
      console.error('Role upgrade error:', error);
    }
  });

  // Generate API key mutation
  const generateApiKeyMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post<{ api_key: string }>('/auth/api-key/generate');
      return response.data;
    },
    onSuccess: (data) => {
      setNewApiKey(data.api_key);
      setShowApiKey(true);
      refreshUserData();
    },
    onError: (error) => {
      console.error('API key generation error:', error);
    }
  });

  // Function to copy API key to clipboard
  const copyApiKey = async (key: string) => {
    try {
      await navigator.clipboard.writeText(key);
      alert('API key copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy API key:', err);
    }
  };

  if (!user) {
    return <div className="flex justify-center items-center h-64">Please log in to view your profile.</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Profile Management</h2>
      </div>

      <div className="grid gap-6">
        {/* Profile Information */}
        <div className="p-6 bg-white rounded-lg shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Profile Information</h3>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="text-lg">{user.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Role</p>
              <p className="text-lg">{user.role}</p>
            </div>
          </div>
        </div>

        {/* Developer Tools */}
        {user.role !== UserRole.ADMIN && (
          <div className="p-6 bg-white rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Developer Access</h3>
            
            {/* Show upgrade success message and API key */}
            {upgradeSuccess && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-700 font-semibold mb-2">
                  Successfully upgraded to Developer role!
                </p>
                <p className="text-sm text-green-600 mb-2">
                  Your API key has been generated. Please copy and save it securely:
                </p>
                <div className="flex items-center space-x-2 bg-white p-2 rounded border">
                  <code className="flex-1 font-mono text-sm">{newApiKey}</code>
                  <button
                    onClick={() => newApiKey && copyApiKey(newApiKey)}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                  >
                    Copy
                  </button>
                </div>
              </div>
            )}

            {user.role === UserRole.PUBLIC ? (
              <div>
                <p className="text-gray-600 mb-4">
                  Upgrade to developer access to use our API and integrate with your applications.
                </p>
                <button
                  onClick={() => upgradeRoleMutation.mutate()}
                  disabled={upgradeRoleMutation.isPending}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700
                    disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {upgradeRoleMutation.isPending ? 'Upgrading...' : 'Upgrade to Developer'}
                </button>
                {upgradeRoleMutation.isError && (
                  <p className="mt-2 text-red-600">Failed to upgrade role. Please try again.</p>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm text-gray-600">API Key</p>
                    <button
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      {showApiKey ? 'Hide' : 'Show'}
                    </button>
                  </div>
                  <div className="flex items-center space-x-2 bg-gray-50 p-2 rounded border">
                    <code className="flex-1 font-mono text-sm">
                      {showApiKey ? (newApiKey || user.api_key) : '••••••••••••••••'}
                    </code>
                    {showApiKey && (
                      <button
                        onClick={() => copyApiKey(newApiKey || user.api_key || '')}
                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                      >
                        Copy
                      </button>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => generateApiKeyMutation.mutate()}
                  disabled={generateApiKeyMutation.isPending}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700
                    disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {generateApiKeyMutation.isPending ? 'Generating...' : 'Generate New API Key'}
                </button>
                {generateApiKeyMutation.isError && (
                  <p className="mt-2 text-red-600">Failed to generate API key. Please try again.</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileManagement;