import { api } from '../lib/api';

// Activity Log API functions
export const getActivityLogs = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.taskId) params.append('task_id', filters.taskId);
  if (filters.projectId) params.append('project_id', filters.projectId);
  if (filters.userId) params.append('user_id', filters.userId);
  
  const response = await api.get(`/activity-logs?${params.toString()}`);
  return response.data;
};

// Attachment API functions
export const getAttachments = async (taskId) => {
  const params = taskId ? `?task_id=${taskId}` : '';
  const response = await api.get(`/attachments${params}`);
  return response.data;
};

export const uploadAttachment = async (taskId, fileData) => {
  const formData = new FormData();
  formData.append('task_id', taskId);
  formData.append('file_name', fileData.name);
  formData.append('file_size', fileData.size);
  formData.append('file_type', fileData.type);
  formData.append('file_url', 'placeholder'); // This would be replaced with actual file upload logic
  
  const response = await api.post('/attachments', formData);
  return response.data;
};

export const deleteAttachment = async (attachmentId) => {
  const response = await api.delete(`/attachments/${attachmentId}`);
  return response.data;
};