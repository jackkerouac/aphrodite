/**
 * useNotifications Hook
 * 
 * Centralized notification management for workflow events
 */

import React, { useCallback } from 'react'
import { toast } from 'sonner'
import { CheckCircle, AlertCircle, Clock, Info } from 'lucide-react'

export const useNotifications = () => {
  const showSuccess = useCallback((title: string, message?: string) => {
    toast.success(
      <div className="flex items-center space-x-3">
        <CheckCircle className="w-4 h-4 text-green-600" />
        <div>
          <div className="font-medium">{title}</div>
          {message && <div className="text-sm text-muted-foreground mt-1">{message}</div>}
        </div>
      </div>
    )
  }, [])

  const showError = useCallback((title: string, message?: string) => {
    toast.error(
      <div className="flex items-center space-x-3">
        <AlertCircle className="w-4 h-4 text-red-600" />
        <div>
          <div className="font-medium">{title}</div>
          {message && <div className="text-sm text-muted-foreground mt-1">{message}</div>}
        </div>
      </div>,
      { duration: 8000 }
    )
  }, [])

  const showInfo = useCallback((title: string, message?: string) => {
    toast.info(
      <div className="flex items-center space-x-3">
        <Info className="w-4 h-4 text-blue-600" />
        <div>
          <div className="font-medium">{title}</div>
          {message && <div className="text-sm text-muted-foreground mt-1">{message}</div>}
        </div>
      </div>
    )
  }, [])

  const showProgress = useCallback((title: string, message?: string) => {
    toast.info(
      <div className="flex items-center space-x-3">
        <Clock className="w-4 h-4 text-orange-600" />
        <div>
          <div className="font-medium">{title}</div>
          {message && <div className="text-sm text-muted-foreground mt-1">{message}</div>}
        </div>
      </div>
    )
  }, [])

  // Specialized notification functions for workflow events
  const showJobCreated = useCallback((jobName: string, totalPosters: number) => {
    showSuccess(
      'Background Job Created',
      `${jobName} - Processing ${totalPosters} posters`
    )
  }, [showSuccess])

  const showJobCompleted = useCallback((jobName: string, totalPosters: number, failedPosters: number = 0) => {
    if (failedPosters === 0) {
      showSuccess(
        'Job Completed Successfully',
        `${jobName} - All ${totalPosters} posters processed`
      )
    } else {
      showError(
        'Job Completed with Errors',
        `${jobName} - ${totalPosters - failedPosters}/${totalPosters} posters processed, ${failedPosters} failed`
      )
    }
  }, [showSuccess, showError])

  const showJobPaused = useCallback((jobName: string) => {
    showInfo('Job Paused', `${jobName} has been paused`)
  }, [showInfo])

  const showJobResumed = useCallback((jobName: string) => {
    showInfo('Job Resumed', `${jobName} is now processing`)
  }, [showInfo])

  const showJobCancelled = useCallback((jobName: string) => {
    showError('Job Cancelled', `${jobName} has been cancelled`)
  }, [showError])

  const showConnectionError = useCallback(() => {
    showError(
      'Connection Lost',
      'Lost connection to job progress updates. Trying to reconnect...'
    )
  }, [showError])

  const showConnectionRestored = useCallback(() => {
    showSuccess(
      'Connection Restored',
      'Real-time progress updates are working again'
    )
  }, [showSuccess])

  return {
    showSuccess,
    showError,
    showInfo,
    showProgress,
    showJobCreated,
    showJobCompleted,
    showJobPaused,
    showJobResumed,
    showJobCancelled,
    showConnectionError,
    showConnectionRestored
  }
}
