
import { useState, useRef, useEffect } from 'react';
import { useAgentQuery } from '../hooks/useEmailQuery';
import { QueryInput } from '../components/QueryInput';
import { ErrorAlert } from '../components/ErrorAlert';
import { Mail, Sparkles, User, Bot } from 'lucide-react';
import { parseError, ApiError, emailApi } from '../services/api';
import { AgentResponse } from '../types/agent';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'draft_email';
  draftData?: {
    to: string;
    subject: string;
    body: string;
  };
  isEditing?: boolean;
}

export const EmailPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [agentError, setAgentError] = useState<ApiError | null>(null);
  const [threadId] = useState(() => `thread_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [pendingDraft, setPendingDraft] = useState<ChatMessage | null>(null);
  const [editingDraft, setEditingDraft] = useState(false);
  const [editedDraft, setEditedDraft] = useState({ to: '', subject: '', body: '' });
  
  const agentQuery = useAgentQuery();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleQuery = (query: string) => {
    // Add user message to chat
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Clear previous errors and pending drafts
    setAgentError(null);
    setPendingDraft(null);

    agentQuery.mutate({ query, threadId }, {
      onSuccess: (data: AgentResponse) => {
        // Extract the last AI message from the response
        const responseMessages = data.messages || [];
        const lastAiMessage = responseMessages
          .filter((msg) => msg.type === 'ai')
          .pop();
        
        if (lastAiMessage) {
          // Check if the response contains a draft email - more sophisticated detection
          const content = lastAiMessage.content;
          const isDraftEmail = isDraftEmailResponse(content);
          
          const assistantMessage: ChatMessage = {
            id: `assistant_${Date.now()}`,
            role: 'assistant',
            content: lastAiMessage.content,
            timestamp: new Date(),
            type: isDraftEmail ? 'draft_email' : 'text'
          };
          
          if (isDraftEmail) {
            // Parse draft email data
            const draftData = parseDraftEmail(content);
            if (draftData.subject || draftData.body) {
              assistantMessage.draftData = draftData;
              setPendingDraft(assistantMessage);
              // Initialize edit state with draft data
              setEditedDraft(draftData);
            }
          }
          
          setMessages(prev => [...prev, assistantMessage]);
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
      }
    });
  };

  const isDraftEmailResponse = (content: string): boolean => {
    // More sophisticated detection for actual draft emails
    const lowerContent = content.toLowerCase();
    
    // Must have email structure indicators
    const hasSubject = lowerContent.includes('subject:');
    const hasTo = lowerContent.includes('to:') || lowerContent.includes('from:');
    const hasEmailBody = lowerContent.includes('dear') || 
                        lowerContent.includes('hi ') ||
                        lowerContent.includes('hello') ||
                        lowerContent.includes('regarding') ||
                        lowerContent.includes('regards') ||
                        lowerContent.includes('sincerely');
    
    // Must indicate it's a draft or reply
    const isDraftOrReply = lowerContent.includes('draft') || 
                         lowerContent.includes('reply') ||
                         lowerContent.includes('here is a draft') ||
                         lowerContent.includes('i\'ve drafted') ||
                         lowerContent.includes('prepared a response');
    
    // Strong indicators of email draft
    const strongIndicators = hasSubject && (hasTo || hasEmailBody);
    
    return strongIndicators && isDraftOrReply;
  };

  const parseDraftEmail = (content: string) => {
    // More robust parsing of draft email content
    const lines = content.split('\n');
    let to = '';
    let subject = '';
    let body = '';
    let inBody = false;
    
    lines.forEach(line => {
      const trimmedLine = line.trim();
      
      if (trimmedLine.toLowerCase().startsWith('to:')) {
        to = trimmedLine.replace(/to:\s*/i, '').trim();
      } else if (trimmedLine.toLowerCase().startsWith('subject:')) {
        subject = trimmedLine.replace(/subject:\s*/i, '').trim();
      } else if (trimmedLine.toLowerCase().startsWith('from:')) {
        // Skip from line
      } else if (trimmedLine === '' && (to || subject)) {
        // Empty line after headers indicates start of body
        inBody = true;
      } else if (inBody || (!trimmedLine.toLowerCase().startsWith('to:') && !trimmedLine.toLowerCase().startsWith('subject:') && !trimmedLine.toLowerCase().startsWith('from:'))) {
        // Add to body if we're past headers or line doesn't look like a header
        if (trimmedLine && !trimmedLine.toLowerCase().startsWith('here is') && 
            !trimmedLine.toLowerCase().startsWith('i\'ve drafted') &&
            !trimmedLine.toLowerCase().startsWith('draft')) {
          body += trimmedLine + '\n';
        }
      }
    });
    
    return { to, subject, body: body.trim() };
  };

  const handleApproveDraft = async () => {
    if (!pendingDraft || !pendingDraft.draftData) return;
    
    try {
      // Use edited draft if in edit mode, otherwise use original
      const draftToSend = editingDraft ? editedDraft : pendingDraft.draftData;
      
      // Call the send email API
      await emailApi.sendEmail(
        draftToSend.to,
        draftToSend.subject,
        draftToSend.body
      );
      
      // Add approval message
      const approvalMessage: ChatMessage = {
        id: `user_${Date.now()}`,
        role: 'user',
        content: '✓ Draft approved and sent successfully',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, approvalMessage]);
      setPendingDraft(null);
      setEditingDraft(false);
    } catch (error) {
      const parsedError = parseError(error);
      setAgentError(parsedError);
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: `Failed to send email: ${parsedError.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleRejectDraft = () => {
    if (!pendingDraft) return;
    
    // Add rejection message
    const rejectionMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: '✗ Draft rejected',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, rejectionMessage]);
    setPendingDraft(null);
    setEditingDraft(false);
  };

  const handleEditDraft = () => {
    setEditingDraft(true);
  };

  const handleCancelEdit = () => {
    setEditingDraft(false);
    if (pendingDraft && pendingDraft.draftData) {
      setEditedDraft(pendingDraft.draftData);
    }
  };

  const handleSaveEdit = () => {
    // Update the pending draft with edited content
    if (pendingDraft) {
      setPendingDraft({
        ...pendingDraft,
        draftData: editedDraft
      });
    }
    setEditingDraft(false);
  };

  return (
    <div className="min-h-screen bg-[#343541] flex flex-col">
      {/* Header */}
      <div className="bg-[#202123] border-b border-gray-700 px-4 py-3">
        <div className="container mx-auto flex items-center justify-center gap-3">
          <Mail className="w-6 h-6 text-emerald-400" />
          <h1 className="text-xl font-bold text-white">AI Email Assistant</h1>
          <Sparkles className="w-6 h-6 text-emerald-400" />
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="container mx-auto max-w-3xl">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-gray-200 mb-2">
                Welcome to AI Email Assistant
              </h2>
              <p className="text-gray-400">
                Ask me to read, search, summarize, or draft emails for you
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center">
                        <Bot className="w-5 h-5 text-white" />
                      </div>
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-[#444654] text-gray-100'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    <div
                      className={`text-xs mt-1 ${
                        message.role === 'user'
                          ? 'text-emerald-200'
                          : 'text-gray-400'
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {agentQuery.isPending && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <div className="bg-[#444654] rounded-lg px-4 py-3">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Draft Approval UI */}
              {pendingDraft && pendingDraft.draftData && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <div className="bg-[#444654] border border-gray-600 rounded-lg px-4 py-3 max-w-[80%]">
                    <div className="mb-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-sm font-semibold text-gray-200">Draft Email</div>
                        {!editingDraft && (
                          <button
                            onClick={handleEditDraft}
                            className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Edit
                          </button>
                        )}
                      </div>
                      
                      {editingDraft ? (
                        <div className="space-y-2">
                          <div>
                            <label className="text-xs font-medium text-gray-400">To:</label>
                            <input
                              type="text"
                              value={editedDraft.to}
                              onChange={(e) => setEditedDraft({...editedDraft, to: e.target.value})}
                              className="w-full mt-1 px-2 py-1 text-sm bg-[#40414f] border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="text-xs font-medium text-gray-400">Subject:</label>
                            <input
                              type="text"
                              value={editedDraft.subject}
                              onChange={(e) => setEditedDraft({...editedDraft, subject: e.target.value})}
                              className="w-full mt-1 px-2 py-1 text-sm bg-[#40414f] border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="text-xs font-medium text-gray-400">Body:</label>
                            <textarea
                              value={editedDraft.body}
                              onChange={(e) => setEditedDraft({...editedDraft, body: e.target.value})}
                              rows={4}
                              className="w-full mt-1 px-2 py-1 text-sm bg-[#40414f] border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
                            />
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={handleSaveEdit}
                              className="px-3 py-1 bg-emerald-600 text-white text-sm rounded hover:bg-emerald-700 transition-colors"
                            >
                              Save Changes
                            </button>
                            <button
                              onClick={handleCancelEdit}
                              className="px-3 py-1 bg-gray-600 text-gray-200 text-sm rounded hover:bg-gray-700 transition-colors"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <div className="text-sm text-gray-300 mb-1">
                            <span className="font-medium text-gray-400">To:</span> {pendingDraft.draftData.to}
                          </div>
                          <div className="text-sm text-gray-300 mb-1">
                            <span className="font-medium text-gray-400">Subject:</span> {pendingDraft.draftData.subject}
                          </div>
                          <div className="text-sm text-gray-200 whitespace-pre-wrap mt-2 p-2 bg-[#40414f] rounded max-h-48 overflow-y-auto">
                            {pendingDraft.draftData.body}
                          </div>
                        </div>
                      )}
                    </div>
                    {!editingDraft && (
                      <div className="flex gap-2">
                        <button
                          onClick={handleApproveDraft}
                          className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2 text-sm"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Approve & Send
                        </button>
                        <button
                          onClick={handleRejectDraft}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2 text-sm"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Agent Error */}
      {agentError && (
        <div className="px-4 py-2">
          <div className="container mx-auto max-w-3xl">
            <ErrorAlert 
              error={agentError} 
              onDismiss={() => setAgentError(null)} 
            />
          </div>
        </div>
      )}

      {/* Query Input */}
      <div className="bg-[#40414f] border-t border-gray-700 px-4 py-4">
        <div className="container mx-auto max-w-3xl">
          <QueryInput 
            onQuery={handleQuery} 
            loading={agentQuery.isPending} 
          />
        </div>
      </div>
    </div>
  );
};
