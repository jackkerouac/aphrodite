import { useEffect, useState } from 'react';
import { useUser } from '@/contexts/UserContext';
import { wsClient, JobStatusMessage, JobProgressMessage, JobErrorMessage } from '@/lib/websocket';

interface JobWebSocketState {
  connected: boolean;
  jobStatus: JobStatusMessage | null;
  jobProgress: JobProgressMessage | null;
  jobError: JobErrorMessage | null;
}

export function useJobWebSocket(jobId?: string) {
  const { user } = useUser();
  const [state, setState] = useState<JobWebSocketState>({
    connected: false,
    jobStatus: null,
    jobProgress: null,
    jobError: null,
  });

  useEffect(() => {
    if (!user?.id) return;

    // Connect to WebSocket
    wsClient.connect(user.id);

    // Set up event handlers
    const handleJobStatus = (data: JobStatusMessage) => {
      if (!jobId || data.jobId === jobId) {
        setState(prev => ({ ...prev, jobStatus: data }));
      }
    };

    const handleJobProgress = (data: JobProgressMessage) => {
      if (!jobId || data.jobId === jobId) {
        setState(prev => ({ ...prev, jobProgress: data }));
      }
    };

    const handleJobError = (data: JobErrorMessage) => {
      if (!jobId || data.jobId === jobId) {
        setState(prev => ({ ...prev, jobError: data }));
      }
    };

    const handleConnect = () => {
      setState(prev => ({ ...prev, connected: true }));
    };

    const handleDisconnect = () => {
      setState(prev => ({ ...prev, connected: false }));
    };

    // Subscribe to events
    wsClient.on('job-status', handleJobStatus);
    wsClient.on('job-progress', handleJobProgress);
    wsClient.on('job-error', handleJobError);
    wsClient.on('connect', handleConnect);
    wsClient.on('disconnect', handleDisconnect);

    // Cleanup
    return () => {
      wsClient.off('job-status', handleJobStatus);
      wsClient.off('job-progress', handleJobProgress);
      wsClient.off('job-error', handleJobError);
      wsClient.off('connect', handleConnect);
      wsClient.off('disconnect', handleDisconnect);
    };
  }, [user?.id, jobId]);

  return state;
}
