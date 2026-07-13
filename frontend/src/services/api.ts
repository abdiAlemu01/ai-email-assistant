import axios from 'axios';
import { EmailResponse, AgentResponse } from '../types/api';

const API_BASE_URL = '/api';

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
