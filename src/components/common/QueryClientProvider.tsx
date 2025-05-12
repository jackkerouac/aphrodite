import { ReactNode } from 'react';
import { QueryClient, QueryClientProvider as RQProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

interface QueryClientProviderProps {
  children: ReactNode;
}

/**
 * Provides React Query context to the application
 */
export const QueryClientProvider = ({ children }: QueryClientProviderProps) => {
  return (
    <RQProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV !== 'production' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </RQProvider>
  );
};

export { queryClient };
