import { Bot } from 'lucide-react';

interface AgentResponseProps {
  response: string;
}

export const AgentResponse = ({ response }: AgentResponseProps) => {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-blue-900 mb-2">AI Assistant</h3>
          <p className="text-gray-700 whitespace-pre-wrap">{response}</p>
        </div>
      </div>
    </div>
  );
};
