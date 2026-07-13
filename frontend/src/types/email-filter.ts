// types/email-filter.ts

export interface EmailFilter {
  query?: string;
  unread?: boolean;
  sender?: string;
  subject?: string;
  hasAttachments?: boolean;
  label?: string;
  dateFrom?: string;
  dateTo?: string;
}
