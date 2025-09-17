import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Calendar, 
  Clock, 
  User, 
  CheckCircle, 
  MessageSquare,
  Paperclip,
  Activity
} from 'lucide-react';
import { api, getErrorMessage } from '../lib/api';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Separator } from '../components/ui/separator';
import ActivityLogList from '../components/ActivityLogList';
import AttachmentList from '../components/AttachmentList';

const TaskDetail = ({ user }) => {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [comment, setComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [comments, setComments] = useState([]);

  useEffect(() => {
    fetchTask();
    fetchComments();
  }, [taskId]);

  const fetchTask = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/tasks/${taskId}/`);
      setTask(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching task:', err);
      setError('Failed to load task details');
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await api.get(`/comments/?task_id=${taskId}`);
      setComments(response.data);
    } catch (err) {
      console.error('Error fetching comments:', err);
    }
  };

  const submitComment = async () => {
    if (!comment.trim()) return;
    
    try {
      setSubmittingComment(true);
      await api.post('/comments/', {
        task: taskId,
        content: comment
      });
      setComment('');
      fetchComments();
    } catch (err) {
      console.error('Error submitting comment:', err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No date set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'todo': return 'bg-gray-100 text-gray-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'review': return 'bg-purple-100 text-purple-800';
      case 'done': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'urgent': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="animate-fadeIn p-6">
        <div className="flex items-center space-x-2 mb-8">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-full hover:bg-gray-100"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div className="h-6 bg-gray-200 rounded w-1/4 animate-pulse"></div>
        </div>
        <div className="space-y-6">
          <div className="h-8 bg-gray-200 rounded w-3/4 animate-pulse"></div>
          <div className="h-24 bg-gray-200 rounded animate-pulse"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex items-center space-x-2 mb-8">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-full hover:bg-gray-100"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <h1 className="text-xl font-semibold text-gray-900">Task Details</h1>
        </div>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
        <button 
          onClick={fetchTask}
          className="mt-4 btn-primary"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!task) return null;

  return (
    <div className="animate-fadeIn p-6">
      {/* Header with back button */}
      <div className="flex items-center space-x-2 mb-8">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 rounded-full hover:bg-gray-100"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <h1 className="text-xl font-semibold text-gray-900">Task Details</h1>
      </div>

      {/* Task title and status */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 md:mb-0">{task.title}</h2>
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(task.status)}`}>
            {task.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(task.priority)}`}>
            {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
          </span>
        </div>
      </div>

      {/* Task details */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Details</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Description</p>
                <p className="text-gray-900">{task.description || 'No description provided'}</p>
              </div>
              
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-900">
                  Due: {formatDate(task.due_date)}
                </span>
              </div>
              
              {task.estimated_hours && (
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-900">
                    Estimated: {task.estimated_hours} hours
                  </span>
                </div>
              )}
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">People</h3>
            <div className="space-y-4">
              {task.assigned_to && (
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Assigned to</p>
                    <p className="text-gray-900">{task.assigned_to.name}</p>
                  </div>
                </div>
              )}
              
              {task.created_by && (
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Created by</p>
                    <p className="text-gray-900">{task.created_by.name}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs for Comments, Attachments, and Activity */}
      <Tabs defaultValue="comments" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="comments" className="flex items-center space-x-2">
            <MessageSquare className="w-4 h-4" />
            <span>Comments</span>
          </TabsTrigger>
          <TabsTrigger value="attachments" className="flex items-center space-x-2">
            <Paperclip className="w-4 h-4" />
            <span>Attachments</span>
          </TabsTrigger>
          <TabsTrigger value="activity" className="flex items-center space-x-2">
            <Activity className="w-4 h-4" />
            <span>Activity</span>
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="comments" className="space-y-6">
          {/* Comment input */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Add a comment..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-3"
              rows="3"
            />
            <div className="flex justify-end">
              <button
                onClick={submitComment}
                disabled={!comment.trim() || submittingComment}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submittingComment ? 'Submitting...' : 'Add Comment'}
              </button>
            </div>
          </div>
          
          {/* Comments list */}
          <div className="space-y-4">
            {comments.length === 0 ? (
              <p className="text-center text-gray-500 py-6">No comments yet</p>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{comment.user.name}</p>
                      <p className="text-xs text-gray-500">{formatDate(comment.created_at)}</p>
                    </div>
                  </div>
                  <p className="text-gray-800">{comment.content}</p>
                </div>
              ))
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="attachments">
          <AttachmentList taskId={taskId} />
        </TabsContent>
        
        <TabsContent value="activity">
          <ActivityLogList taskId={taskId} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TaskDetail;