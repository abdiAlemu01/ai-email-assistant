import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EmailPage } from '../pages/EmailPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <EmailPage />
    </QueryClientProvider>
  );
};
