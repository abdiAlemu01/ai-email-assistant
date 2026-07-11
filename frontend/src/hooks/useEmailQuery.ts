// useEmailQuery.tsx

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { emailApi } from '../services/api';

export const useEmails = (limit: number = 5) => {
  return useQuery({
    queryKey: ['emails', limit],
    queryFn: () => emailApi.getEmails(limit),
  });
};

export const useAgentQuery = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (query: string) => emailApi.runAgent(query),
    onSuccess: () => {
      // Invalidate emails query after agent runs
      queryClient.invalidateQueries({ queryKey: ['emails'] });
    },
  });
};
