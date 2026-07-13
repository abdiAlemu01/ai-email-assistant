// types/agent.ts

export interface AgentRequest {
  query: string;
}

export interface AgentResponse {
  success: boolean;
  response?: string;
  error?: string;
  data?: unknown;
}
