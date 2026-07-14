import { Email } from '../types/email';
import { EmailCard } from './EmailCard';

interface EmailListProps {
  emails: Email[] | undefined;
  loading?: boolean;
}

export const EmailList = ({ emails, loading }: EmailListProps) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-lg p-4 animate-pulse">
            <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-300 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-300 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  // Defensive check - ensure emails is an array
  if (!emails || !Array.isArray(emails)) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Unable to load emails</p>
        <p className="text-sm text-gray-400 mt-2">Invalid data format received</p>
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No emails found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {emails.map((email, index) => (
        <EmailCard key={email.id || index} email={email} />
      ))}
    </div>
  );
};
