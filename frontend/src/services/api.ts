import axios, { AxiosError } from 'axios';
import { EmailResponse, AgentResponse } from '../types/api';

const API_BASE_URL = '/api';

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
      return {
        message: 'Unable to connect to the server',
        detail: 'Please check if the backend server is running on http://localhost:8000',
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
  runAgent: async (query: string): Promise<AgentResponse> => {
    const response = await axios.post(`${API_BASE_URL}/agent/run`, {
      query
    });
    return response.data;
  }
};
