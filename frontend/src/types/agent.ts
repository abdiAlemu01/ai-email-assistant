// types/agent.ts

export interface AgentRequest {
  query: string;
}

export interface AgentMessage {
  type: string;
  content: string;
}

export interface AgentResponse {
  messages: AgentMessage[];
}
