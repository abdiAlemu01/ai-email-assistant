
import { useState } from 'react';
import { useEmails, useAgentQuery } from '../hooks/useEmailQuery';
import { EmailList } from '../components/EmailList';
import { QueryInput } from '../components/QueryInput';
import { AgentResponse } from '../components/AgentResponse';
import { Mail, Sparkles } from 'lucide-react';

export const EmailPage = () => {
  const [agentResponse, setAgentResponse] = useState<string>('');
  const { data: emailsData, isLoading: emailsLoading } = useEmails(5);
  const agentQuery = useAgentQuery();

  const handleQuery = (query: string) => {
    agentQuery.mutate(query, {
      onSuccess: (data) => {
        // Extract the last AI message from the response
        const messages = data.messages || [];
        const lastAiMessage = messages
          .filter((msg: any) => msg.type === 'ai')
          .pop();
        
        if (lastAiMessage) {
          setAgentResponse(lastAiMessage.content);
        }
      },
      onError: () => {
        setAgentResponse('Sorry, I encountered an error processing your request.');
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

        {/* Agent Response */}
        {agentResponse && (
          <div className="max-w-3xl mx-auto mb-8">
            <AgentResponse response={agentResponse} />
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
          <EmailList 
            emails={emailsData?.emails || []} 
            loading={emailsLoading} 
          />
        </div>
      </div>
    </div>
  );
};
