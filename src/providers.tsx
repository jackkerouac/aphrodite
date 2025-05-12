import { ReactNode } from 'react';
import { QueryClientProvider } from '@/components/common/QueryClientProvider';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Root providers for the application
 * Wraps the application with all required providers
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <QueryClientProvider>
      {children}
    </QueryClientProvider>
  );
}
