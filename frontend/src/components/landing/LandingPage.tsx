// src/components/landing/LandingPage.tsx
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-blue-600 text-white py-20">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl">
            <h1 className="text-4xl font-bold mb-6">
              Master Export Industry Knowledge
            </h1>
            <p className="text-xl mb-8">
              Comprehensive education platform for export industry professionals with
              integrated analytics and developer tools.
            </p>
            <Link
              to="/register"
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold
                hover:bg-blue-50 transition-colors inline-block"
            >
              Get Started
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Platform Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-white rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Educational Content</h3>
              <p className="text-gray-600">
                Access comprehensive courses and materials about export industry practices.
              </p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Data Analytics</h3>
              <p className="text-gray-600">
                Analyze export data with powerful visualization and reporting tools.
              </p>
            </div>
            <div className="p-6 bg-white rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Developer API</h3>
              <p className="text-gray-600">
                Integrate our analytics capabilities into your own applications.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="bg-gray-50 py-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-8">Ready to Get Started?</h2>
          <div className="space-x-4">
            <Link
              to="/register"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold
                hover:bg-blue-700 transition-colors inline-block"
            >
              Sign Up Now
            </Link>
            <Link
              to="/documentation"
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold
                border border-blue-600 hover:bg-blue-50 transition-colors inline-block"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;