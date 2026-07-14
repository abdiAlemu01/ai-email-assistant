// types/email.ts

export interface Email {
  id?: string;
  subject: string;
  from: string;
  to: string;
  date: string;
  body: string;
  attachments: string[];
  snippet?: string;
  priority?: 'high' | 'medium' | 'low';
  unread?: boolean;
}

export interface EmailResponse {
  count: number;
  emails: Email[];
}

export interface EmailFilter {
  unread?: boolean;
  priority?: 'high' | 'medium' | 'low';
  sender?: string;
  dateFrom?: string;
  dateTo?: string;
}
