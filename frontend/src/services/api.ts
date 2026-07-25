import axios, { AxiosError } from 'axios';
import { EmailResponse, AgentResponse } from '../types/api';

// Use VITE_API_URL if set (for local development with remote backend or production)
// Otherwise use local proxy for development
// Vite requires environment variables to start with VITE_ prefix
const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? import.meta.env.VITE_API_URL
  : (import.meta.env.PROD 
    ? 'https://ai-email-assistant-re4w.onrender.com/api' 
    : '/api');

export interface ApiError {
  message: string;
  detail?: string;
  status: number;
  source: 'gmail' | 'agent' | 'network' | 'server';
}

export const parseError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    
    // Network error (no response from server)
    if (!axiosError.response) {
      const backendUrl = import.meta.env.PROD 
        ? 'https://ai-email-assistant-re4w.onrender.com'
        : 'http://localhost:8000';
      return {
        message: 'Unable to connect to the server',
        detail: `Please check if the backend server is running on ${backendUrl}`,
        status: 0,
        source: 'network'
      };
    }

    const status = axiosError.response.status;
    const detail = axiosError.response.data?.detail || axiosError.message;

    // Identify error source based on status code and message
    let source: ApiError['source'] = 'server';
    
    if (status === 503 || detail.includes('Gmail') || detail.includes('connection')) {
      source = 'gmail';
    } else if (detail.includes('agent') || detail.includes('Groq') || detail.includes('api_key')) {
      source = 'agent';
    }

    // Create user-friendly messages
    let message = 'An error occurred';
    
    if (source === 'gmail') {
      message = 'Gmail Connection Error';
    } else if (source === 'agent') {
      message = 'AI Agent Error';
    } else if (status === 500) {
      message = 'Server Error';
    } else if (status === 404) {
      message = 'Not Found';
    }

    return {
      message,
      detail,
      status,
      source
    };
  }

  // Unknown error
  return {
    message: 'An unexpected error occurred',
    detail: error instanceof Error ? error.message : String(error),
    status: -1,
    source: 'server'
  };
};

export const emailApi = {
  // Get latest emails
  getEmails: async (limit: number = 5): Promise<EmailResponse> => {
    const response = await axios.get(`${API_BASE_URL}/email/`, {
      params: { limit }
    });
    return response.data;
  },

  // Run agent with natural language query
  runAgent: async (query: string, threadId: string = 'default'): Promise<AgentResponse> => {
    const response = await axios.post(`${API_BASE_URL}/agent/run`, {
      query,
      thread_id: threadId
    });
    return response.data;
  },

  // Send email
  sendEmail: async (to: string, subject: string, body: string): Promise<{ message: string }> => {
    const response = await axios.post(`${API_BASE_URL}/email/send`, {
      to,
      subject,
      body
    });
    return response.data;
  }
};
