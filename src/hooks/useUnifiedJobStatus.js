import { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Hook to monitor unified badge rendering job status
 * @param {number|null} jobId - The job ID to monitor
 * @returns {Object} Job status information
 */
export function useUnifiedJobStatus(jobId) {
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    let intervalId;
    
    const fetchStatus = async () => {
      if (!jobId) return;
      
      try {
        setLoading(true);
        const response = await axios.get(`/api/unified-badge-render/jobs/${jobId}`);
        const jobStatus = response.data;
        
        setStatus(jobStatus.status);
        setProgress(jobStatus.progress || 0);
        
        // Check if job is completed or failed
        if (jobStatus.status === 'completed' || jobStatus.status === 'failed' || jobStatus.status === 'cancelled') {
          setCompleted(true);
          clearInterval(intervalId);
        }
        
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch job status');
      } finally {
        setLoading(false);
      }
    };
    
    // Fetch immediately
    if (jobId) {
      fetchStatus();
      
      // Then set up polling
      intervalId = setInterval(fetchStatus, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [jobId]);
  
  /**
   * Cancel the job
   */
  const cancelJob = async () => {
    if (!jobId) return;
    
    try {
      await axios.delete(`/api/unified-badge-render/jobs/${jobId}`);
      // Update status locally
      setStatus('cancelled');
      setCompleted(true);
    } catch (err) {
      setError(err.message || 'Failed to cancel job');
    }
  };
  
  return {
    status,
    progress,
    error,
    loading,
    completed,
    cancelJob
  };
}
