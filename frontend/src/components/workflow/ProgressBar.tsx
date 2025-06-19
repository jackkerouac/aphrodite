/**
 * ProgressBar Component
 * 
 * Real-time progress visualization for job processing
 */

import React, { useEffect } from 'react'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

interface ProgressData {
  total_posters: number
  completed_posters: number
  failed_posters: number
  progress_percentage: number
  estimated_completion?: string
}

interface ProgressBarProps {
  progress: ProgressData
  isConnected: boolean
  className?: string
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  isConnected,
  className = ''
}) => {
  // Debug logging for progress updates
  useEffect(() => {
    console.log('📊 ProgressBar received progress update:', progress)
  }, [progress])

  useEffect(() => {
    console.log('🔗 ProgressBar connection status:', isConnected)
  }, [isConnected])
  const getStatusColor = () => {
    if (!isConnected) return 'bg-gray-400'
    if (progress.failed_posters > 0) return 'bg-orange-500'
    if (progress.progress_percentage === 100) return 'bg-green-500'
    return 'bg-blue-500'
  }

  const formatTime = (isoString?: string) => {
    if (!isoString) return 'Calculating...'
    try {
      const date = new Date(isoString)
      return date.toLocaleTimeString()
    } catch {
      return 'Unknown'
    }
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Progress Bar */}
      <div className="relative">
        <Progress 
          value={progress.progress_percentage} 
          className="h-2"
        />
        <div 
          className={`absolute top-0 left-0 h-2 rounded transition-all ${getStatusColor()}`}
          style={{ width: `${progress.progress_percentage}%` }}
        />
      </div>

      {/* Status Information */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div className="flex items-center space-x-4">
          <span className="font-medium">
            {progress.completed_posters} / {progress.total_posters} completed
          </span>
          
          {progress.failed_posters > 0 && (
            <Badge variant="destructive" className="text-xs">
              <AlertCircle className="w-3 h-3 mr-1" />
              {progress.failed_posters} failed
            </Badge>
          )}
          
          <Badge 
            variant={isConnected ? "secondary" : "outline"} 
            className="text-xs"
          >
            <div className={`w-2 h-2 rounded-full mr-1 ${
              isConnected ? 'bg-green-500' : 'bg-gray-400'
            }`} />
            {isConnected ? 'Live' : 'Disconnected'}
          </Badge>
        </div>

        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4" />
          <span>
            ETA: {formatTime(progress.estimated_completion)}
          </span>
        </div>
      </div>

      {/* Progress Percentage */}
      <div className="text-center">
        <span className="text-lg font-semibold">
          {progress.progress_percentage.toFixed(1)}%
        </span>
      </div>
    </div>
  )
}
