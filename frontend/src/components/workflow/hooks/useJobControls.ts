/**
 * useJobControls Hook
 * 
 * Job control actions (pause, resume, cancel)
 */

import { useState, useCallback } from 'react'

interface JobControlsState {
  isPausing: boolean
  isResuming: boolean
  isCancelling: boolean
}

interface UseJobControlsReturn extends JobControlsState {
  pauseJob: () => Promise<boolean>
  resumeJob: () => Promise<boolean>
  cancelJob: () => Promise<boolean>
}

export const useJobControls = (jobId: string): UseJobControlsReturn => {
  const [state, setState] = useState<JobControlsState>({
    isPausing: false,
    isResuming: false,
    isCancelling: false
  })

  const makeRequest = useCallback(async (
    action: 'pause' | 'resume' | 'cancel',
    loadingKey: keyof JobControlsState
  ): Promise<boolean> => {
    setState(prev => ({ ...prev, [loadingKey]: true }))
    
    try {
      const response = await fetch(`/api/v1/workflow/control/${jobId}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        return true
      } else {
        console.error(`Failed to ${action} job:`, response.statusText)
        return false
      }
    } catch (error) {
      console.error(`Error ${action}ing job:`, error)
      return false
    } finally {
      setState(prev => ({ ...prev, [loadingKey]: false }))
    }
  }, [jobId])

  const pauseJob = useCallback(() => 
    makeRequest('pause', 'isPausing'), [makeRequest])

  const resumeJob = useCallback(() => 
    makeRequest('resume', 'isResuming'), [makeRequest])

  const cancelJob = useCallback(() => 
    makeRequest('cancel', 'isCancelling'), [makeRequest])

  return {
    ...state,
    pauseJob,
    resumeJob,
    cancelJob
  }
}
