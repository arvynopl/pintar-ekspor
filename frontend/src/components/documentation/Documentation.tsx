// src/components/documentation/Documentation.tsx
import { useState } from 'react';

interface DocSection {
  id: string;
  title: string;
  content: string;
}

const Documentation = () => {
  const [activeSection, setActiveSection] = useState('getting-started');

  const sections: DocSection[] = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      content: `
### Introduction
Pintar Ekspor provides educational content and analytics tools for the export industry.
This documentation will help you get started with our platform.

### Quick Start
1. Create an account
2. Browse available courses
3. Access analytics dashboard
      `
    },
    {
      id: 'courses',
      title: 'Course System',
      content: `
### Accessing Courses
Browse our course catalog and enroll in courses that match your needs.

### Course Progress
Track your progress through each course and earn certificates upon completion.
      `
    },
    {
      id: 'analytics',
      title: 'Analytics Tools',
      content: `
### Data Analysis
Upload your data and use our analytics tools to gain insights.

### Visualization
Create charts and reports to visualize your export data effectively.
      `
    },
    {
      id: 'api',
      title: 'API Integration',
      content: `
### Authentication
Use API keys to authenticate your requests:
\`\`\`
Authorization: Bearer YOUR_API_KEY
\`\`\`

### Endpoints
- GET /api/analytics/summary
- POST /api/analytics/upload
- GET /api/analytics/export
      `
    }
  ];

  return (
    <div className="container mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">Documentation</h1>
      
      <div className="grid md:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <nav className="md:col-span-1">
          <ul className="space-y-2 sticky top-8">
            {sections.map((section) => (
              <li key={section.id}>
                <button
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full text-left px-4 py-2 rounded-lg transition-colors
                    ${activeSection === section.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                    }`}
                >
                  {section.title}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Content Area */}
        <div className="md:col-span-3">
          <div className="prose max-w-none">
            {sections.map((section) => (
              <div
                key={section.id}
                className={activeSection === section.id ? 'block' : 'hidden'}
              >
                <h2 className="text-2xl font-bold mb-6">{section.title}</h2>
                <div className="space-y-4">
                  {section.content.split('\n').map((line, index) => {
                    if (line.startsWith('###')) {
                      return (
                        <h3 key={index} className="text-xl font-semibold mt-8 mb-4">
                          {line.replace('### ', '')}
                        </h3>
                      );
                    }
                    return <p key={index} className="text-gray-600">{line}</p>;
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Documentation;