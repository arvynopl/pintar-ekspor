// src/pages/Profile.tsx
import ProfileManagement from '../components/profile/ProfileManagement';

export default function Profile() {
  return (
    <div className="container mx-auto">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">My Profile</h1>
        <ProfileManagement />
      </div>
    </div>
  );
}