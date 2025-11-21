import { useAuthStore } from '../store/authStore';
import { BookOpen, Briefcase, CheckCircle, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const { user } = useAuthStore();

  const stats = [
    {
      name: 'Upcoming Assignments',
      value: '5',
      icon: BookOpen,
      color: 'bg-blue-500',
      href: '/assignments',
    },
    {
      name: 'Completed',
      value: '12',
      icon: CheckCircle,
      color: 'bg-green-500',
      href: '/assignments',
    },
    {
      name: 'Job Matches',
      value: '8',
      icon: Briefcase,
      color: 'bg-purple-500',
      href: '/jobs',
    },
    {
      name: 'Hours This Week',
      value: '24',
      icon: Clock,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.full_name || user?.email}!
        </h1>
        <p className="text-gray-600 mt-2">
          Here's what's happening with your academics and career search
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <Link
            key={stat.name}
            to={stat.href || '#'}
            className="card hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-center gap-4">
              <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-600">{stat.name}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Deadlines */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upcoming Deadlines</h2>
          <div className="space-y-3">
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900">Database Design Project</p>
              <p className="text-sm text-gray-600">CS 440 - Due in 3 days</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900">Algorithm Analysis Essay</p>
              <p className="text-sm text-gray-600">CS 341 - Due in 5 days</p>
            </div>
            <Link to="/assignments" className="block text-center text-primary-600 hover:text-primary-700 font-medium text-sm mt-4">
              View all assignments →
            </Link>
          </div>
        </div>

        {/* Job Matches */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Job Matches</h2>
          <div className="space-y-3">
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900">Software Engineering Intern</p>
              <p className="text-sm text-gray-600">Google - 95% match</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900">Backend Developer Intern</p>
              <p className="text-sm text-gray-600">Microsoft - 92% match</p>
            </div>
            <Link to="/jobs" className="block text-center text-primary-600 hover:text-primary-700 font-medium text-sm mt-4">
              View all matches →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
