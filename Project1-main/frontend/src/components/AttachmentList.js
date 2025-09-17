import React, { useState, useEffect } from 'react';
import { getAttachments, uploadAttachment, deleteAttachment } from '../services/activityService';
import { Paperclip, X, Upload, File } from 'lucide-react';

const AttachmentList = ({ taskId }) => {
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!taskId) return;
    
    const fetchAttachments = async () => {
      try {
        setLoading(true);
        const data = await getAttachments(taskId);
        setAttachments(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching attachments:', err);
        setError('Failed to load attachments');
      } finally {
        setLoading(false);
      }
    };

    fetchAttachments();
  }, [taskId]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      const fileData = {
        name: file.name,
        size: file.size,
        type: file.type
      };
      
      const newAttachment = await uploadAttachment(taskId, fileData);
      setAttachments([...attachments, newAttachment]);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (attachmentId) => {
    try {
      await deleteAttachment(attachmentId);
      setAttachments(attachments.filter(a => a.id !== attachmentId));
    } catch (err) {
      console.error('Error deleting attachment:', err);
      setError('Failed to delete attachment');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (!taskId) return null;
  if (loading) return <div className="p-4 text-center">Loading attachments...</div>;
  if (error) return <div className="p-4 text-center text-red-500">{error}</div>;

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden mt-4">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Attachments</h3>
        <label className="flex items-center px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 cursor-pointer">
          <Upload className="h-4 w-4 mr-1" />
          Upload
          <input 
            type="file" 
            className="hidden" 
            onChange={handleFileUpload}
            disabled={uploading}
          />
        </label>
      </div>
      
      {uploading && (
        <div className="p-3 bg-blue-50 text-blue-700 text-sm">
          Uploading file...
        </div>
      )}
      
      {attachments.length === 0 ? (
        <div className="p-4 text-center text-gray-500">No attachments</div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {attachments.map((attachment) => (
            <li key={attachment.id} className="px-4 py-3 hover:bg-gray-50 flex items-center justify-between">
              <div className="flex items-center">
                <File className="h-5 w-5 text-gray-400 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{attachment.file_name}</p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(attachment.file_size)} • Uploaded by {attachment.uploaded_by.name}
                  </p>
                </div>
              </div>
              <div className="flex items-center">
                <a 
                  href={attachment.file_url} 
                  className="text-blue-600 hover:text-blue-800 mr-3 text-sm"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Download
                </a>
                <button
                  onClick={() => handleDelete(attachment.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AttachmentList;