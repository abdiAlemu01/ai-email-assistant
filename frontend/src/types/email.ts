// 
// types/email.ts
export interface Email {
  sender: string;
  subject: string;
  snippet: string;
}

export interface EmailResponse {
  count: number;
  emails: Email[];
}

export interface AgentRequest {
  query: string;
}

export interface AgentResponse {
  messages: any[];
  response?: string;
}
