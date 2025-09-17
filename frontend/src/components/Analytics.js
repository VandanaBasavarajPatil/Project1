import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import { api, getErrorMessage } from '../lib/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// API base centralized in lib/api

const Analytics = ({ user }) => {
  const [timeRange, setTimeRange] = useState('7d');
  const [loading, setLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState({
    productivityTrends: [],
    teamPerformance: [],
    taskDistribution: {}
  });

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      // Fetch all analytics data
      const [trendsResponse, teamResponse, distributionResponse] = await Promise.all([
        api.get('/analytics/productivity-trends/'),
        api.get('/analytics/team-performance/'),
        api.get('/analytics/task-distribution/')
      ]);

      setAnalyticsData({
        productivityTrends: trendsResponse.data.trends || [],
        teamPerformance: teamResponse.data.team_performance || [],
        taskDistribution: distributionResponse.data || {}
      });
    } catch (error) {
      console.error('Error fetching analytics data:', getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  // Chart configurations
  const productivityChartData = {
    labels: analyticsData.productivityTrends.map(item => 
      new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ),
    datasets: [
      {
        label: 'Completed Tasks',
        data: analyticsData.productivityTrends.map(item => item.completed),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2,
      },
      {
        label: 'Total Tasks',
        data: analyticsData.productivityTrends.map(item => item.total),
        backgroundColor: 'rgba(156, 163, 175, 0.5)',
        borderColor: 'rgb(156, 163, 175)',
        borderWidth: 2,
      }
    ]
  };

  const teamPerformanceChartData = {
    labels: analyticsData.teamPerformance.map(member => member.user_name),
    datasets: [
      {
        label: 'Completed Tasks',
        data: analyticsData.teamPerformance.map(member => member.completed_tasks),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 92, 246, 0.8)',
        ],
        borderWidth: 2,
      }
    ]
  };

  const taskDistributionData = {
    labels: analyticsData.taskDistribution.status_distribution?.map(item => 
      item.status.replace('_', ' ').toUpperCase()
    ) || [],
    datasets: [
      {
        data: analyticsData.taskDistribution.status_distribution?.map(item => item.count) || [],
        backgroundColor: [
          'rgba(156, 163, 175, 0.8)', // todo
          'rgba(59, 130, 246, 0.8)',  // in_progress
          'rgba(245, 158, 11, 0.8)',  // review
          'rgba(16, 185, 129, 0.8)',  // done
        ],
        borderWidth: 2,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  // Calculate metrics from analytics data
  const totalCompleted = analyticsData.productivityTrends.reduce((sum, item) => sum + item.completed, 0);
  const totalTasks = analyticsData.productivityTrends.reduce((sum, item) => sum + item.total, 0);
  const avgCompletionRate = totalTasks > 0 ? ((totalCompleted / totalTasks) * 100).toFixed(1) : 0;
  const teamProductivity = analyticsData.teamPerformance.length > 0 
    ? (analyticsData.teamPerformance.reduce((sum, member) => sum + member.completion_rate, 0) / analyticsData.teamPerformance.length).toFixed(1)
    : 0;

  const metrics = [
    {
      title: 'Tasks Completed',
      value: totalCompleted.toString(),
      change: '+12%',
      changeType: 'positive',
      description: 'vs last period'
    },
    {
      title: 'Completion Rate',
      value: `${avgCompletionRate}%`,
      change: '+8%',
      changeType: 'positive',
      description: 'efficiency score'
    },
    {
      title: 'Team Productivity',
      value: `${teamProductivity}%`,
      change: '+5%',
      changeType: 'positive',
      description: 'average performance'
    },
    {
      title: 'Active Projects',
      value: analyticsData.taskDistribution.project_distribution?.length?.toString() || '0',
      change: '+2',
      changeType: 'positive',
      description: 'projects running'
    },
  ];

  if (loading) {
    return (
      <div className="animate-fadeIn">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600 mt-1">Track productivity and performance metrics</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">Track productivity and performance metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <button 
            onClick={fetchAnalyticsData}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button className="btn-primary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">{metric.title}</h3>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                index === 0 ? 'bg-blue-100' :
                index === 1 ? 'bg-green-100' :
                index === 2 ? 'bg-purple-100' :
                'bg-orange-100'
              }`}>
                {index === 0 ? <BarChart3 className="w-4 h-4 text-blue-600" /> :
                 index === 1 ? <Calendar className="w-4 h-4 text-green-600" /> :
                 index === 2 ? <TrendingUp className="w-4 h-4 text-purple-600" /> :
                 <TrendingUp className="w-4 h-4 text-orange-600" />}
              </div>
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-gray-900">{metric.value}</span>
              <span className={`text-sm font-medium ${
                metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
              }`}>
                {metric.change}
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-1">{metric.description}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Productivity Trends Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Productivity Trends</h2>
          </div>
          {analyticsData.productivityTrends.length > 0 ? (
            <Bar data={productivityChartData} options={chartOptions} />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              <p>No productivity data available</p>
            </div>
          )}
        </div>

        {/* Task Distribution Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Task Distribution</h2>
          </div>
          {analyticsData.taskDistribution.status_distribution?.length > 0 ? (
            <Doughnut data={taskDistributionData} options={doughnutOptions} />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              <p>No task distribution data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Team Performance Chart */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Team Performance</h2>
        </div>
        {analyticsData.teamPerformance.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <Bar data={teamPerformanceChartData} options={chartOptions} />
            </div>
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Team Statistics</h3>
              {analyticsData.teamPerformance.map((member, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-medium">
                        {member.user_name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{member.user_name}</p>
                      <p className="text-xs text-gray-600">
                        {member.completed_tasks} completed • {member.total_hours.toFixed(1)}h logged
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{member.completion_rate.toFixed(1)}%</p>
                    <p className="text-xs text-gray-600">completion rate</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <p>No team performance data available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;