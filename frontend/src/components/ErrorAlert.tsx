import { AlertCircle, Wifi, Server, Zap, X } from 'lucide-react';
import { ApiError } from '../services/api';

interface ErrorAlertProps {
  error: ApiError;
  onDismiss?: () => void;
}

export const ErrorAlert = ({ error, onDismiss }: ErrorAlertProps) => {
  const getIcon = () => {
    switch (error.source) {
      case 'network':
        return <Wifi className="w-5 h-5" />;
      case 'gmail':
        return <Server className="w-5 h-5" />;
      case 'agent':
        return <Zap className="w-5 h-5" />;
      default:
        return <AlertCircle className="w-5 h-5" />;
    }
  };

  const getColor = () => {
    switch (error.source) {
      case 'network':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'gmail':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      case 'agent':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getSuggestion = () => {
    switch (error.source) {
      case 'network':
        return 'Check if the backend server is running and your internet connection is active.';
      case 'gmail':
        return 'Try refreshing your Gmail token or check your internet connection.';
      case 'agent':
        return 'The AI service may be unavailable. Check your API key configuration.';
      default:
        return 'Please try again or contact support if the problem persists.';
    }
  };

  return (
    <div className={`rounded-lg border-2 p-4 ${getColor()} mb-4`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {getIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm mb-1">
            {error.message}
            {error.status > 0 && <span className="ml-2 text-xs opacity-75">(Status: {error.status})</span>}
          </h3>
          <p className="text-sm opacity-90 mb-2">{error.detail}</p>
          <p className="text-xs opacity-75">{getSuggestion()}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 p-1 hover:bg-black hover:bg-opacity-10 rounded transition-colors"
            aria-label="Dismiss error"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
