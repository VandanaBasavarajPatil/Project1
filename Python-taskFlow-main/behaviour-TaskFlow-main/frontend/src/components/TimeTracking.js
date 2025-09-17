import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Square,
  Clock,
  Calendar,
  BarChart3,
  Timer
} from 'lucide-react';
import { api, getErrorMessage } from '../lib/api';

const TimeTracking = ({ user }) => {
  const [activeTimer, setActiveTimer] = useState(null);
  const [timeEntries, setTimeEntries] = useState([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedTask, setSelectedTask] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [description, setDescription] = useState('');

  useEffect(() => {
    fetchTasks();
    fetchTimeEntries();
  }, []);

  useEffect(() => {
    let interval = null;
    if (activeTimer) {
      interval = setInterval(() => {
        setCurrentTime(time => time + 1);
      }, 1000);
    } else if (!activeTimer && currentTime !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [activeTimer, currentTime]);

  const fetchTasks = async () => {
    try {
      const response = await api.get('/tasks/');
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', getErrorMessage(error));
    }
  };

  const fetchTimeEntries = async () => {
    try {
      const response = await api.get('/time-entries/');
      setTimeEntries(response.data);
    } catch (error) {
      console.error('Error fetching time entries:', getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const startTimer = () => {
    if (!selectedTask) return;
    setActiveTimer(selectedTask);
    setCurrentTime(0);
  };

  const pauseTimer = () => {
    setActiveTimer(null);
  };

  const stopTimer = async () => {
    if (activeTimer && currentTime > 0) {
      try {
        const token = localStorage.getItem('token');
        const startTime = new Date(Date.now() - currentTime * 1000).toISOString();
        const endTime = new Date().toISOString();
        
        await api.post('/time-entries/', {
          task_id: activeTimer,
          start_time: startTime,
          end_time: endTime,
          description: description || 'Time tracking session'
        });
        
        fetchTimeEntries(); // Refresh the list
      } catch (error) {
        console.error('Error saving time entry:', getErrorMessage(error));
      }
    }
    setActiveTimer(null);
    setCurrentTime(0);
    setSelectedTask('');
    setDescription('');
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDuration = (hours) => {
    const h = Math.floor(hours);
    const m = Math.floor((hours - h) * 60);
    return `${h}h ${m}m`;
  };

  // Calculate today's and week's totals
  const today = new Date().toISOString().split('T')[0];
  const todayEntries = timeEntries.filter(entry => 
    entry.created_at && entry.created_at.split('T')[0] === today
  );
  
  const thisWeekTotal = timeEntries.reduce((total, entry) => total + (entry.duration_hours || 0), 0);
  const todayTotal = todayEntries.reduce((total, entry) => total + (entry.duration_hours || 0), 0);

  if (loading) {
    return (
      <div className="animate-fadeIn">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Time Tracking</h1>
            <p className="text-gray-600 mt-1">Track time spent on tasks and projects</p>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2 card animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6"></div>
            <div className="h-20 bg-gray-200 rounded mb-8"></div>
            <div className="h-12 bg-gray-200 rounded"></div>
          </div>
          <div className="space-y-6">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-6 bg-gray-200 rounded mb-4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Time Tracking</h1>
          <p className="text-gray-600 mt-1">Track time spent on tasks and projects</p>
        </div>
      </div>

      {/* Time Tracker */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-2">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Active Timer</h2>
            
            {/* Timer Display */}
            <div className="text-center mb-8">
              <div className="text-6xl font-mono font-bold text-gray-900 mb-4">
                {formatTime(currentTime)}
              </div>
              {activeTimer && (
                <p className="text-lg text-gray-600">
                  Tracking: {tasks.find(t => t.id === activeTimer)?.title}
                </p>
              )}
            </div>

            {/* Task Selection */}
            {!activeTimer && (
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Task
                  </label>
                  <select
                    value={selectedTask}
                    onChange={(e) => setSelectedTask(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Choose a task to track</option>
                    {tasks.map((task) => (
                      <option key={task.id} value={task.id}>
                        {task.title}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (Optional)
                  </label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="What are you working on?"
                  />
                </div>
              </div>
            )}

            {/* Timer Controls */}
            <div className="flex items-center justify-center space-x-4">
              {!activeTimer ? (
                <button
                  onClick={startTimer}
                  disabled={!selectedTask}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg flex items-center space-x-2 transition-all duration-200 transform hover:scale-105"
                >
                  <Play className="w-5 h-5" />
                  <span>Start Timer</span>
                </button>
              ) : (
                <>
                  <button
                    onClick={pauseTimer}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-all duration-200"
                  >
                    <Pause className="w-5 h-5" />
                    <span>Pause</span>
                  </button>
                  <button
                    onClick={stopTimer}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-all duration-200"
                  >
                    <Square className="w-5 h-5" />
                    <span>Stop & Save</span>
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Today's Summary</h3>
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Hours Worked</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatDuration(todayTotal + (activeTimer ? currentTime / 3600 : 0))}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Sessions</p>
                <p className="text-2xl font-bold text-gray-900">{todayEntries.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Tasks Tracked</p>
                <p className="text-2xl font-bold text-green-600">
                  {new Set(todayEntries.map(entry => entry.task?.id)).size}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">This Week</h3>
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Total Hours</p>
                <p className="text-2xl font-bold text-gray-900">{formatDuration(thisWeekTotal)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Daily Average</p>
                <p className="text-2xl font-bold text-gray-900">{formatDuration(thisWeekTotal / 7)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Goal Progress (40h/week)</p>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${Math.min((thisWeekTotal / 40) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">
                    {Math.round((thisWeekTotal / 40) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Time Entries */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Recent Time Entries</h2>
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
            View All
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-600">Task</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Duration</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Date</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Description</th>
              </tr>
            </thead>
            <tbody>
              {timeEntries.slice(0, 10).map((entry) => (
                <tr key={entry.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span className="font-medium text-gray-900">
                      {entry.task?.title || 'Unknown Task'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <Timer className="w-4 h-4 text-blue-600" />
                      <span className="text-gray-900">
                        {formatDuration(entry.duration_hours || 0)}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-600">
                      {entry.created_at ? new Date(entry.created_at).toLocaleDateString() : 'Unknown'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-gray-600">{entry.description || 'No description'}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {timeEntries.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Timer className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No time entries yet</p>
            <p className="text-sm">Start tracking time to see your entries here</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeTracking;