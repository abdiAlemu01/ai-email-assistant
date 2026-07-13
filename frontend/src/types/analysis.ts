// types/analysis.ts

export interface EmailAnalysis {
  priority: 'high' | 'medium' | 'low';
  summary: string;
  actionItems: string[];
}
