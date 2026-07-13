// shared/utils/format.ts
export const formatSender = (sender: string | undefined): string => {
  if (!sender) return 'Unknown';
  // Extract name from email if available
  const match = sender.match(/^(.*?)\s*</);
  return match ? match[1].trim() : sender;
};

export const truncateText = (text: string | undefined, maxLength: number): string => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
