import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  BarChart3,
  Target,
  Zap,
  Calendar,
  Plus,
  ArrowUp,
  ArrowDown,
  Activity
} from 'lucide-react';
import { api } from '../lib/api';

const Dashboard = ({ user }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await api.get('/dashboard/stats/');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statsCards = [
    {
      title: 'Tasks Completed',
      value: stats?.tasks_completed || 0,
      change: '+12%',
      changeType: 'increase',
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Avg Completion Time',
      value: `${stats?.avg_completion_time || 0}h`,
      change: '-8%',
      changeType: 'decrease',
      icon: Clock,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Team Productivity',
      value: `${stats?.team_productivity || 0}%`,
      change: '+5%',
      changeType: 'increase',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Overdue Tasks',
      value: stats?.overdue_tasks || 0,
      change: '-3',
      changeType: 'decrease',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
  ];

  const aiInsights = [
    {
      title: 'Daily Focus Time',
      value: `${stats?.daily_focus_time || 0}h`,
      insight: 'Peak productivity between 9-11 AM',
      icon: Target,
      color: 'text-orange-600',
    },
    {
      title: 'Completion Rate',
      value: `${stats?.completion_rate?.toFixed(1) || 0}%`,
      insight: 'Above team average',
      icon: Zap,
      color: 'text-green-600',
    },
    {
      title: 'Team Velocity',
      value: '24 pts',
      insight: 'Consistent sprint performance',
      icon: Activity,
      color: 'text-blue-600',
    },
    {
      title: 'Best Work Hours',
      value: '9-11 AM',
      insight: 'Highest task completion rate',
      icon: Calendar,
      color: 'text-purple-600',
    },
  ];

  if (loading) {
    return (
      <div className="animate-fadeIn">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome back, {user?.name}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, {user?.name}</p>
        </div>
        <button className="btn-primary flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Create Task</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card card-hover">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</p>
                  <div className="flex items-center space-x-1">
                    {stat.changeType === 'increase' ? (
                      <ArrowUp className="w-4 h-4 text-green-600" />
                    ) : (
                      <ArrowDown className="w-4 h-4 text-red-600" />
                    )}
                    <span className={`text-sm font-medium ${
                      stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </span>
                    <span className="text-sm text-gray-500">vs last week</span>
                  </div>
                </div>
                <div className={`w-12 h-12 ${stat.bgColor} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Productivity Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">AI Productivity Insights</h2>
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          
          <div className="space-y-4">
            {aiInsights.map((insight, index) => {
              const Icon = insight.icon;
              return (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                      <Icon className={`w-5 h-5 ${insight.color}`} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{insight.title}</p>
                      <p className="text-xs text-gray-600">{insight.insight}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{insight.value}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Active Projects */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Active Projects</h2>
            <span className="text-sm text-gray-500">{stats?.active_projects || 0} projects</span>
          </div>
          
          <div className="space-y-4">
            {[
              { name: 'TaskFlow Mobile App', progress: 75, team: 4, dueDate: '2 days' },
              { name: 'Website Redesign', progress: 45, team: 3, dueDate: '1 week' },
              { name: 'API Integration', progress: 90, team: 2, dueDate: 'Tomorrow' },
            ].map((project, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{project.name}</h3>
                  <span className="text-sm text-gray-500">Due {project.dueDate}</span>
                </div>
                
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className="flex -space-x-1">
                      {[...Array(project.team)].map((_, i) => (
                        <div key={i} className="w-6 h-6 bg-blue-600 rounded-full border-2 border-white flex items-center justify-center">
                          <span className="text-xs text-white font-medium">{i + 1}</span>
                        </div>
                      ))}
                    </div>
                    <span className="text-sm text-gray-600">{project.team} members</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{project.progress}%</span>
                </div>
                
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${project.progress}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Recent Tasks</h2>
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">View all</button>
        </div>
        
        <div className="space-y-3">
          {stats?.recent_tasks?.slice(0, 5).map((task, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="flex items-center space-x-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  task.status === 'done' ? 'bg-green-100 text-green-600' :
                  task.status === 'in_progress' ? 'bg-blue-100 text-blue-600' :
                  task.status === 'review' ? 'bg-purple-100 text-purple-600' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  <CheckCircle className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{task.title}</p>
                  <p className="text-sm text-gray-600 capitalize">{task.priority} priority</p>
                </div>
              </div>
              <div className="text-right">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  task.status === 'done' ? 'bg-green-100 text-green-800' :
                  task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                  task.status === 'review' ? 'bg-purple-100 text-purple-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {task.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          )) || (
            <div className="text-center py-8 text-gray-500">
              <p>No recent tasks found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;