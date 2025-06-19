/**
 * ProcessingDecision Component
 * 
 * Determines whether to use immediate or batch processing
 */

import React from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Clock, Zap, Users } from 'lucide-react'

interface Poster {
  id: string
  title: string
  poster_url?: string
}

interface ProcessingDecisionProps {
  selectedPosters: Poster[]
  onImmediateProcess: (poster: Poster) => void
  onBatchProcess: (posters: Poster[]) => void
  className?: string
}

export const ProcessingDecision: React.FC<ProcessingDecisionProps> = ({
  selectedPosters,
  onImmediateProcess,
  onBatchProcess,
  className = ''
}) => {
  const posterCount = selectedPosters.length

  if (posterCount === 0) {
    return (
      <Alert className={className}>
        <AlertDescription>
          Select one or more posters to begin badge processing.
        </AlertDescription>
      </Alert>
    )
  }

  if (posterCount === 1) {
    return (
      <Alert className={className}>
        <Zap className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <div>
            <strong>Immediate Processing</strong> - Your poster will be processed instantly with real-time preview.
          </div>
          <Badge variant="secondary" className="ml-2">
            <Clock className="w-3 h-3 mr-1" />
            ~5-30 seconds
          </Badge>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <Alert className={className}>
      <Users className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <div>
          <strong>Background Processing</strong> - {posterCount} posters will be processed in the background with real-time progress tracking.
        </div>
        <Badge variant="outline" className="ml-2">
          <Clock className="w-3 h-3 mr-1" />
          Track in Jobs tab
        </Badge>
      </AlertDescription>
    </Alert>
  )
}
