/**
 * JobsTab Component
 * 
 * Jobs management interface for the Poster Manager
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RefreshCw, Search, Filter } from 'lucide-react'
import { JobStatusCard } from './JobStatusCard'

interface Job {
  job_id: string  // Backend uses job_id
  name: string
  status: string
  total_posters: number
  completed_posters: number
  failed_posters: number
  badge_types?: string[]  // May not be returned in list
  created_at: string
  estimated_completion?: string
}

interface JobsTabProps {
  className?: string
}

export const JobsTab: React.FC<JobsTabProps> = ({ className = '' }) => {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [error, setError] = useState<string | null>(null)

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/v1/workflow/jobs/')
      
      if (response.ok) {
        const data = await response.json()
        setJobs(data || [])
        setError(null)
      } else {
        setError('Failed to fetch jobs')
      }
    } catch (err) {
      setError('Network error while fetching jobs')
      console.error('Error fetching jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  const handleJobUpdate = (jobId: string, newStatus: string) => {
    setJobs(prev => prev.map(job => 
      job.job_id === jobId ? { ...job, status: newStatus } : job
    ))
  }

  const handleProgressUpdate = useCallback((jobId: string, progressData: any) => {
    console.log(`📥 JobsTab received progress update for job ${jobId}:`, progressData)
    setJobs(prev => prev.map(job => {
      if (job.job_id === jobId) {
        console.log(`🔄 JobsTab updating job ${jobId} with progress data`)
        return {
          ...job,
          completed_posters: progressData.completed_posters,
          failed_posters: progressData.failed_posters,
          total_posters: progressData.total_posters,
          estimated_completion: progressData.estimated_completion
        }
      }
      return job
    }))
  }, [])

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.job_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || job.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusCounts = () => {
    const counts = jobs.reduce((acc, job) => {
      acc[job.status] = (acc[job.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    return {
      all: jobs.length,
      ...counts
    }
  }

  const statusCounts = getStatusCounts()

  if (loading) {
    return (
      <div className={`flex justify-center items-center h-64 ${className}`}>
        <RefreshCw className="w-8 h-8 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">Loading jobs...</span>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Background Jobs</h2>
        <Button onClick={fetchJobs} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filter Jobs</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search by job name or ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div className="w-48">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All ({statusCounts.all})</SelectItem>
                  <SelectItem value="processing">Processing ({statusCounts.processing || 0})</SelectItem>
                  <SelectItem value="paused">Paused ({statusCounts.paused || 0})</SelectItem>
                  <SelectItem value="completed">Completed ({statusCounts.completed || 0})</SelectItem>
                  <SelectItem value="failed">Failed ({statusCounts.failed || 0})</SelectItem>
                  <SelectItem value="cancelled">Cancelled ({statusCounts.cancelled || 0})</SelectItem>
                  <SelectItem value="queued">Queued ({statusCounts.queued || 0})</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200">
          <CardContent className="pt-6">
            <div className="text-red-600 text-center">
              {error}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Jobs List */}
      <div className="space-y-4">
        {filteredJobs.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-muted-foreground">
                {jobs.length === 0 
                  ? 'No background jobs found. Create a batch job by selecting 2+ posters in the Poster Manager.'
                  : 'No jobs match your search criteria.'
                }
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredJobs.map(job => (
            <JobStatusCard
              key={job.job_id}
              job={job}
              onJobUpdate={handleJobUpdate}
              onProgressUpdate={handleProgressUpdate}
            />
          ))
        )}
      </div>

      {/* Summary */}
      {jobs.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground text-center">
              Showing {filteredJobs.length} of {jobs.length} jobs
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
