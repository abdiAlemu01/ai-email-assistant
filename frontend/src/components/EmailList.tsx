import { Email } from '../types/email';
import { EmailCard } from './EmailCard';

interface EmailListProps {
  emails: Email[];
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
        <EmailCard key={index} email={email} />
      ))}
    </div>
  );
};
