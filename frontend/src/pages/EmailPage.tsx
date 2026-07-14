
import { useState } from 'react';
import { useEmails, useAgentQuery } from '../hooks/useEmailQuery';
import { EmailList } from '../components/EmailList';
import { QueryInput } from '../components/QueryInput';
import { AgentResponse as AgentResponseComponent } from '../components/AgentResponse';
import { ErrorAlert } from '../components/ErrorAlert';
import { Mail, Sparkles } from 'lucide-react';
import { parseError, ApiError } from '../services/api';
import { AgentResponse } from '../types/agent';

export const EmailPage = () => {
  const [agentResponse, setAgentResponse] = useState<string>('');
  const [agentError, setAgentError] = useState<ApiError | null>(null);
  const [emailError, setEmailError] = useState<ApiError | null>(null);
  
  const { data: emailsData, isLoading: emailsLoading, error: emailsQueryError } = useEmails(5);
  const agentQuery = useAgentQuery();

  // Parse email loading error
  if (emailsQueryError && !emailError) {
    setEmailError(parseError(emailsQueryError));
  }

  const handleQuery = (query: string) => {
    // Clear previous errors
    setAgentError(null);
    setAgentResponse('');

    agentQuery.mutate(query, {
      onSuccess: (data: AgentResponse) => {
        // Extract the last AI message from the response
        const messages = data.messages || [];
        const lastAiMessage = messages
          .filter((msg) => msg.type === 'ai')
          .pop();
        
        if (lastAiMessage) {
          setAgentResponse(lastAiMessage.content);
        } else {
          setAgentError({
            message: 'No Response',
            detail: 'The AI agent did not return any response.',
            status: 200,
            source: 'agent'
          });
        }
      },
      onError: (error) => {
        const parsedError = parseError(error);
        setAgentError(parsedError);
        setAgentResponse('');
      }
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Mail className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">AI Email Assistant</h1>
            <Sparkles className="w-8 h-8 text-blue-600" />
          </div>
          <p className="text-green-600">Ask questions about your emails using natural language</p>
        </div>

        {/* Query Input */}
        <div className="max-w-3xl mx-auto mb-8">
          <QueryInput 
            onQuery={handleQuery} 
            loading={agentQuery.isPending} 
          />
        </div>

        {/* Agent Error */}
        {agentError && (
          <div className="max-w-3xl mx-auto mb-8">
            <ErrorAlert 
              error={agentError} 
              onDismiss={() => setAgentError(null)} 
            />
          </div>
        )}

        {/* Agent Response */}
        {agentResponse && (
          <div className="max-w-3xl mx-auto mb-8">
            <AgentResponseComponent response={agentResponse} />
          </div>
        )}

        {/* Email List */}
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Emails</h2>
            <span className="text-sm text-gray-500">
              {emailsData?.count || 0} emails
            </span>
          </div>

          {/* Email Loading Error */}
          {emailError && (
            <ErrorAlert 
              error={emailError} 
              onDismiss={() => setEmailError(null)} 
            />
          )}

          <EmailList 
            emails={emailsData?.emails || []} 
            loading={emailsLoading} 
          />
        </div>
      </div>
    </div>
  );
};
