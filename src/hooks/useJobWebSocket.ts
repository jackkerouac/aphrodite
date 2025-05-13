import { useEffect, useState, useCallback, useRef } from 'react';
import { useUser } from '@/contexts/UserContext';
import { wsClient, JobStatusMessage, JobProgressMessage, JobErrorMessage } from '@/lib/websocket';

interface JobWebSocketState {
  connected: boolean;
  jobStatus: JobStatusMessage | null;
  jobProgress: JobProgressMessage | null;
  jobError: JobErrorMessage | null;
  isReconnecting: boolean;
  reconnectAttempts: number;
  lastMessageTime: number | null;
}

export function useJobWebSocket(jobId?: string) {
  const { user } = useUser();
  const [state, setState] = useState<JobWebSocketState>({
    connected: false,
    jobStatus: null,
    jobProgress: null,
    jobError: null,
    isReconnecting: false,
    reconnectAttempts: 0,
    lastMessageTime: null,
  });
  
  // Keep track of the job ID in a ref to avoid unnecessary effect triggers
  const jobIdRef = useRef<string | undefined>(jobId);
  
  // Store the reconnection timeout ID for cleanup
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Store the heartbeat interval ID for cleanup
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Function to handle reconnection logic
  const attemptReconnect = useCallback(() => {
    if (!user?.id || state.reconnectAttempts >= 5) return;
    
    setState(prev => ({
      ...prev,
      isReconnecting: true,
      reconnectAttempts: prev.reconnectAttempts + 1
    }));
    
    // Exponential backoff for reconnection attempts
    const delay = Math.min(1000 * Math.pow(2, state.reconnectAttempts), 30000);
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    reconnectTimeoutRef.current = setTimeout(() => {
      console.log(`Attempting to reconnect WebSocket (attempt ${state.reconnectAttempts + 1})`);
      wsClient.connect(user.id);
    }, delay);
  }, [user?.id, state.reconnectAttempts]);
  
  // Function to cancel the current job
  const cancelJob = useCallback(() => {
    if (!jobIdRef.current) return;
    
    console.log(`Sending cancel request for job ${jobIdRef.current}`);
    wsClient.emit('cancel-job', { jobId: jobIdRef.current });
  }, []);
  
  // Update the ref when the jobId prop changes
  useEffect(() => {
    jobIdRef.current = jobId;
  }, [jobId]);
  
  // Setup WebSocket connection and event handlers
  useEffect(() => {
    if (!user?.id) return;

    // Connect to WebSocket
    wsClient.connect(user.id);
    
    // Reset reconnection state
    setState(prev => ({
      ...prev,
      isReconnecting: false,
      reconnectAttempts: 0
    }));

    // Set up event handlers
    const handleJobStatus = (data: JobStatusMessage) => {
      if (!jobIdRef.current || data.jobId === jobIdRef.current) {
        setState(prev => ({
          ...prev,
          jobStatus: data,
          lastMessageTime: Date.now()
        }));
        
        // Handle different status types with enhanced information
        console.log(`Job ${data.jobId} status updated: ${data.status}`, data);
      }
    };

    const handleJobProgress = (data: JobProgressMessage) => {
      if (!jobIdRef.current || data.jobId === jobIdRef.current) {
        setState(prev => ({
          ...prev,
          jobProgress: data,
          lastMessageTime: Date.now()
        }));
        
        // Log badge-specific information if available
        if (data.badgeType) {
          console.log(`Processing ${data.badgeType} badge for item ${data.itemId}`);
        }
      }
    };

    const handleJobError = (data: JobErrorMessage) => {
      if (!jobIdRef.current || data.jobId === jobIdRef.current) {
        setState(prev => ({
          ...prev,
          jobError: data,
          lastMessageTime: Date.now()
        }));
        
        console.error(`Job ${data.jobId} error:`, data.error);
      }
    };

    const handleConnect = () => {
      setState(prev => ({
        ...prev,
        connected: true,
        isReconnecting: false,
        reconnectAttempts: 0,
        lastMessageTime: Date.now()
      }));
      
      console.log('WebSocket connected successfully');
      
      // Subscribe to job-specific channel if jobId is provided
      if (jobIdRef.current) {
        wsClient.emit('subscribe-job', { jobId: jobIdRef.current });
        console.log(`Subscribed to updates for job ${jobIdRef.current}`);
      }
    };

    const handleDisconnect = () => {
      setState(prev => ({ ...prev, connected: false }));
      console.log('WebSocket disconnected');
      attemptReconnect();
    };
    
    // Handle job cancellation confirmation
    const handleJobCancelled = (data: { jobId: string }) => {
      if (!jobIdRef.current || data.jobId === jobIdRef.current) {
        console.log(`Job ${data.jobId} cancellation confirmed`);
        setState(prev => ({
          ...prev,
          jobStatus: prev.jobStatus ? { ...prev.jobStatus, status: 'failed' } : null,
          lastMessageTime: Date.now()
        }));
      }
    };

    // Subscribe to events
    wsClient.on('job-status', handleJobStatus);
    wsClient.on('job-progress', handleJobProgress);
    wsClient.on('job-error', handleJobError);
    wsClient.on('connect', handleConnect);
    wsClient.on('disconnect', handleDisconnect);
    wsClient.on('job-cancelled', handleJobCancelled);
    
    // Setup a heartbeat to check connection status
    heartbeatIntervalRef.current = setInterval(() => {
      const currentTime = Date.now();
      const lastMessageTime = state.lastMessageTime;
      
      // If no message received in the last 30 seconds and we're supposedly connected,
      // attempt to reconnect
      if (state.connected && lastMessageTime && (currentTime - lastMessageTime > 30000)) {
        console.log('No message received in 30 seconds, checking connection...');
        wsClient.emit('ping', {});
        
        // Set a timeout to check if we got a response
        setTimeout(() => {
          if (state.lastMessageTime === lastMessageTime) {
            console.log('No response to ping, reconnecting...');
            wsClient.disconnect();
            attemptReconnect();
          }
        }, 5000);
      }
    }, 30000);

    // Cleanup
    return () => {
      wsClient.off('job-status', handleJobStatus);
      wsClient.off('job-progress', handleJobProgress);
      wsClient.off('job-error', handleJobError);
      wsClient.off('connect', handleConnect);
      wsClient.off('disconnect', handleDisconnect);
      wsClient.off('job-cancelled', handleJobCancelled);
      
      // Clear the heartbeat interval
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }
      
      // Clear any reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      
      // Unsubscribe from the job if we were subscribed
      if (jobIdRef.current) {
        wsClient.emit('unsubscribe-job', { jobId: jobIdRef.current });
      }
    };
  }, [user?.id, attemptReconnect]);

  // Return the state and the cancelJob function
  return {
    ...state,
    cancelJob
  };
}
