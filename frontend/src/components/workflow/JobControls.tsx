/**
 * JobControls Component
 * 
 * Pause, resume, and cancel job functionality
 */

import React from 'react'
import { Button } from '@/components/ui/button'
import { Pause, Play, Square, Loader2, RefreshCw } from 'lucide-react'
import { useJobControls } from './hooks/useJobControls'

interface JobControlsProps {
  jobId: string
  jobStatus: string
  onStatusChange?: (newStatus: string) => void
  disabled?: boolean
}

export const JobControls: React.FC<JobControlsProps> = ({
  jobId,
  jobStatus,
  onStatusChange,
  disabled = false
}) => {
  const { 
    isPausing, 
    isResuming, 
    isCancelling, 
    isRestarting,
    pauseJob, 
    resumeJob, 
    cancelJob,
    restartJob
  } = useJobControls(jobId)

  const handlePause = async () => {
    const success = await pauseJob()
    if (success && onStatusChange) {
      onStatusChange('paused')
    }
  }

  const handleResume = async () => {
    const success = await resumeJob()
    if (success && onStatusChange) {
      onStatusChange('processing')
    }
  }

  const handleCancel = async () => {
    const success = await cancelJob()
    if (success && onStatusChange) {
      onStatusChange('cancelled')
    }
  }

  const handleRestart = async () => {
    const success = await restartJob()
    if (success && onStatusChange) {
      onStatusChange('queued')
    }
  }

  const isLoading = isPausing || isResuming || isCancelling || isRestarting
  const isProcessing = jobStatus === 'processing'
  const isPaused = jobStatus === 'paused'
  const isQueued = jobStatus === 'queued'
  const isCompleted = ['completed', 'failed', 'cancelled'].includes(jobStatus)

  if (isCompleted) {
    return (
      <div className="text-sm text-muted-foreground">
        Job {jobStatus}
      </div>
    )
  }

  return (
    <div className="flex items-center space-x-2">
      {/* Pause/Resume Button */}
      {isProcessing && (
        <Button
          variant="outline"
          size="sm"
          onClick={handlePause}
          disabled={disabled || isLoading}
        >
          {isPausing ? (
            <>
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              Pausing...
            </>
          ) : (
            <>
              <Pause className="w-4 h-4 mr-1" />
              Pause
            </>
          )}
        </Button>
      )}

      {isPaused && (
        <Button
          variant="outline"
          size="sm"
          onClick={handleResume}
          disabled={disabled || isLoading}
        >
          {isResuming ? (
            <>
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              Resuming...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-1" />
              Resume
            </>
          )}
        </Button>
      )}

      {/* Restart Button for stuck queued jobs */}
      {isQueued && (
        <Button
          variant="outline"
          size="sm"
          onClick={handleRestart}
          disabled={disabled || isLoading}
        >
          {isRestarting ? (
            <>
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              Restarting...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 mr-1" />
              Restart
            </>
          )}
        </Button>
      )}

      {/* Cancel Button */}
      {!isCompleted && (
        <Button
          variant="destructive"
          size="sm"
          onClick={handleCancel}
          disabled={disabled || isLoading}
        >
          {isCancelling ? (
            <>
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              Cancelling...
            </>
          ) : (
            <>
              <Square className="w-4 h-4 mr-1" />
              Cancel
            </>
          )}
        </Button>
      )}
    </div>
  )
}
