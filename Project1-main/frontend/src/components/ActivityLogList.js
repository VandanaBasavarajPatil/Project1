import React, { useState, useEffect } from 'react';
import { getActivityLogs } from '../services/activityService';
import { formatDistanceToNow } from 'date-fns';
import { Activity, User, Folder, FileText } from 'lucide-react';

const ActivityLogList = ({ taskId, projectId }) => {
  const [activityLogs, setActivityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActivityLogs = async () => {
      try {
        setLoading(true);
        const filters = {};
        if (taskId) filters.taskId = taskId;
        if (projectId) filters.projectId = projectId;
        
        const data = await getActivityLogs(filters);
        setActivityLogs(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching activity logs:', err);
        setError('Failed to load activity logs');
      } finally {
        setLoading(false);
      }
    };

    fetchActivityLogs();
  }, [taskId, projectId]);

  const getActionIcon = (action) => {
    switch (action) {
      case 'created':
      case 'updated':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'assigned':
        return <User className="h-4 w-4 text-green-500" />;
      case 'status_changed':
        return <Activity className="h-4 w-4 text-orange-500" />;
      case 'commented':
        return <FileText className="h-4 w-4 text-purple-500" />;
      case 'attached_file':
        return <Folder className="h-4 w-4 text-yellow-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) return <div className="p-4 text-center">Loading activity logs...</div>;
  if (error) return <div className="p-4 text-center text-red-500">{error}</div>;
  if (activityLogs.length === 0) return <div className="p-4 text-center text-gray-500">No activity logs found</div>;

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="text-lg font-medium text-gray-900">Activity Log</h3>
      </div>
      <ul className="divide-y divide-gray-200">
        {activityLogs.map((log) => (
          <li key={log.id} className="px-4 py-3 hover:bg-gray-50">
            <div className="flex items-start">
              <div className="flex-shrink-0 mt-1">
                {getActionIcon(log.action)}
              </div>
              <div className="ml-3 flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-900">
                    {log.user.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                  </p>
                </div>
                <p className="text-sm text-gray-500">{log.description}</p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ActivityLogList;