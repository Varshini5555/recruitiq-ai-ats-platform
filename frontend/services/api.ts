import axios from 'axios';

// Ensure this matches the port your FastAPI terminal displays on startup
const API_BASE_URL = 'http://127.0.0.1:8000'; 

export const analyzeResume = async (
  file: File, 
  role?: string, 
  level?: string,
  jdText?: string
) => {
  try {
    const formData = new FormData();
    
    // 💡 Map keys perfectly to match FastAPI's UploadFile and Form arguments!
    formData.append('file', file);
    formData.append('jd_mode', jdText ? 'custom' : 'system');
    if (role) formData.append('role', role);
    if (level) formData.append('level', level);
    if (jdText) formData.append('jd_text', jdText);

    // 💡 Hit "/upload_resume" instead of "/analyze"
    const response = await axios.post(`${API_BASE_URL}/upload_resume`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error uploading and analyzing resume:', error);
    throw error;
  }
};