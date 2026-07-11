export const formatSender = (sender: string): string => {
  // Extract name from email if available
  const match = sender.match(/^(.*?)\s*</);
  return match ? match[1].trim() : sender;
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
