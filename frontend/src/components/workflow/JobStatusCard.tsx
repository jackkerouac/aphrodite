/**
 * JobStatusCard Component
 * 
 * Individual job status display with real-time updates
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Clock, Users, FileImage, Calendar } from 'lucide-react'
import { ProgressBar } from './ProgressBar'
import { JobControls } from './JobControls'
import { useJobProgress } from './hooks/useJobProgress'

interface Job {
  job_id: string  // Backend uses job_id
  name: string
  status: string
  total_posters: number
  completed_posters: number
  failed_posters: number
  badge_types?: string[]  // May not be included in response
  created_at: string
  estimated_completion?: string
}

interface JobStatusCardProps {
  job: Job
  onJobUpdate?: (jobId: string, newStatus: string) => void
  onProgressUpdate?: (jobId: string, progressData: any) => void
}

export const JobStatusCard: React.FC<JobStatusCardProps> = ({
  job,
  onJobUpdate,
  onProgressUpdate
}) => {
  const [currentStatus, setCurrentStatus] = useState(job.status)
  const { progress, isConnected, error } = useJobProgress(job.job_id)

  // Debug logging for progress updates
  useEffect(() => {
    console.log(`🎯 JobStatusCard for ${job.job_id}: progress updated:`, progress)
  }, [progress, job.job_id])

  useEffect(() => {
    console.log(`🔗 JobStatusCard for ${job.job_id}: connection status:`, isConnected)
  }, [isConnected, job.job_id])

  // Notify parent component when progress updates AND connected
  useEffect(() => {
    if (progress && onProgressUpdate && isConnected) {
      console.log(`📤 JobStatusCard sending progress update to parent for job ${job.job_id}:`, progress)
      // Debounce progress updates to prevent excessive re-renders
      const timeoutId = setTimeout(() => {
        onProgressUpdate(job.job_id, progress)
      }, 100)
      
      return () => clearTimeout(timeoutId)
    } else if (progress && !isConnected) {
      console.log(`⚠️ JobStatusCard has progress data but WebSocket disconnected for job ${job.job_id} - not sending stale data`)
    }
  }, [progress?.completed_posters, progress?.failed_posters, progress?.total_posters, job.job_id, onProgressUpdate, isConnected])

  const handleStatusChange = (newStatus: string) => {
    setCurrentStatus(newStatus)
    onJobUpdate?.(job.job_id, newStatus)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500'
      case 'processing': return 'bg-blue-500'
      case 'paused': return 'bg-yellow-500'
      case 'failed': return 'bg-red-500'
      case 'cancelled': return 'bg-gray-500'
      case 'queued': return 'bg-purple-500'
      default: return 'bg-gray-400'
    }
  }

  const formatDate = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleString()
    } catch {
      return 'Unknown'
    }
  }

  // Use real-time progress data if available, otherwise fall back to job data
  const displayProgress = progress || {
    total_posters: job.total_posters,
    completed_posters: job.completed_posters,
    failed_posters: job.failed_posters,
    progress_percentage: job.total_posters > 0 
      ? ((job.completed_posters + job.failed_posters) / job.total_posters) * 100 
      : 0,
    estimated_completion: job.estimated_completion
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{job.name}</CardTitle>
          <Badge className={`${getStatusColor(currentStatus)} text-white`}>
            {currentStatus}
          </Badge>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
          <div className="flex items-center">
            <FileImage className="w-4 h-4 mr-1" />
            {job.total_posters} posters
          </div>
          
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-1" />
            {job.badge_types?.join(', ') || 'Unknown badges'}
          </div>
          
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-1" />
            {formatDate(job.created_at)}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress Bar */}
        {['processing', 'paused'].includes(currentStatus) && (
          <ProgressBar 
            progress={displayProgress}
            isConnected={isConnected}
          />
        )}

        {/* Error Display */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
            Connection error: {error}
          </div>
        )}

        {/* Completed Progress */}
        {currentStatus === 'completed' && (
          <div className="text-center text-green-600 font-medium">
            ✅ All {job.total_posters} posters processed successfully
          </div>
        )}

        {/* Failed Progress */}
        {currentStatus === 'failed' && (
          <div className="text-center text-red-600 font-medium">
            ❌ Job failed - {job.failed_posters} posters could not be processed
          </div>
        )}

        {/* Job Controls */}
        <div className="flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            ID: {job.job_id.slice(0, 8)}...
          </div>
          
          <JobControls
            jobId={job.job_id}
            jobStatus={currentStatus}
            onStatusChange={handleStatusChange}
          />
        </div>
      </CardContent>
    </Card>
  )
}
