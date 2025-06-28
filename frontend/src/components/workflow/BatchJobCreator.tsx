/**
 * BatchJobCreator Component
 * 
 * Interface for creating batch processing jobs
 */

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Play, FileImage } from 'lucide-react'

interface Poster {
  id: string
  title: string
  poster_url?: string
}

interface BatchJobCreatorProps {
  selectedPosters: Poster[]
  onJobCreated: (jobId: string) => void
  onCancel: () => void
  className?: string
}

export const BatchJobCreator: React.FC<BatchJobCreatorProps> = ({
  selectedPosters,
  onJobCreated,
  onCancel,
  className = ''
}) => {
  const [jobName, setJobName] = useState(`Batch Processing - ${new Date().toLocaleDateString()}`)
  const [badgeTypes, setBadgeTypes] = useState<string[]>(['audio', 'resolution'])
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const availableBadges = [
    { id: 'audio', label: 'Audio Codec Badges', description: 'DTS-HD MA, Atmos, etc.' },
    { id: 'resolution', label: 'Resolution Badges', description: '4K HDR, 1080p, etc.' },
    { id: 'review', label: 'Review Badges', description: 'IMDb, TMDb, RT ratings' },
    { id: 'awards', label: 'Awards Badges', description: 'Oscars, Emmys, etc.' }
  ]

  const handleBadgeToggle = (badgeId: string) => {
    setBadgeTypes(prev => 
      prev.includes(badgeId) 
        ? prev.filter(id => id !== badgeId)
        : [...prev, badgeId]
    )
  }

  const handleCreateJob = async () => {
    if (badgeTypes.length === 0) {
      setError('Please select at least one badge type')
      return
    }

    setIsCreating(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/workflow/jobs/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: jobName,
          badge_types: badgeTypes,
          poster_ids: selectedPosters.map(p => p.id),
          user_id: 'default_user'
        })
      })

      if (response.ok) {
        const data = await response.json()
        onJobCreated(data.job_id)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to create batch job')
      }
    } catch (err) {
      setError('Network error while creating job')
      console.error('Error creating batch job:', err)
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center">
          <FileImage className="w-5 h-5 mr-2" />
          Create Batch Processing Job
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Job Name */}
        <div className="space-y-2">
          <Label htmlFor="job-name">Job Name</Label>
          <Input
            id="job-name"
            value={jobName}
            onChange={(e) => setJobName(e.target.value)}
            placeholder="Enter a descriptive name for this job"
          />
        </div>

        {/* Badge Selection */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>Badge Types to Apply</Label>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                const allBadgeIds = availableBadges.map(badge => badge.id)
                setBadgeTypes(allBadgeIds)
              }}
              className="text-xs"
            >
              Select All
            </Button>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {availableBadges.map(badge => (
              <div key={badge.id} className="flex items-start space-x-3">
                <Checkbox
                  id={`badge-${badge.id}`}
                  checked={badgeTypes.includes(badge.id)}
                  onCheckedChange={() => handleBadgeToggle(badge.id)}
                />
                <div className="flex-1 min-w-0">
                  <Label 
                    htmlFor={`badge-${badge.id}`}
                    className="text-sm font-medium cursor-pointer"
                  >
                    {badge.label}
                  </Label>
                  <p className="text-xs text-muted-foreground mt-1">
                    {badge.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Job Summary */}
        <Alert>
          <AlertDescription>
            <strong>Job Summary:</strong> {selectedPosters.length} posters will be processed with {badgeTypes.length} badge type{badgeTypes.length !== 1 ? 's' : ''}
            {badgeTypes.length > 0 && ` (${badgeTypes.join(', ')})`}.
          </AlertDescription>
        </Alert>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Actions */}
        <div className="flex justify-between">
          <Button variant="outline" onClick={onCancel} disabled={isCreating}>
            Cancel
          </Button>
          
          <Button onClick={handleCreateJob} disabled={isCreating || badgeTypes.length === 0}>
            {isCreating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating Job...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Batch Processing
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
