// components/EmailCard.tsx
import { Email } from '../types/email';
import { formatSender, truncateText } from '../shared/utils/format';
import { Mail, User } from 'lucide-react';

interface EmailCardProps {
  email: Email;
}

export const EmailCard = ({ email }: EmailCardProps) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow border border-gray-200">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-blue-600" />
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h3 className="font-semibold text-gray-900 truncate">
              {formatSender(email.from)}
            </h3>
            <Mail className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
          </div>
          <p className="text-sm font-medium text-gray-800 mb-2 truncate">
            {email.subject}
          </p>
          <p className="text-sm text-gray-600 line-clamp-2">
            {truncateText(email.snippet, 150)}
          </p>
        </div>
      </div>
    </div>
  );
};
