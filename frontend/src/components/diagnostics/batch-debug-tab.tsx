"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, CheckCircle, XCircle, AlertTriangle, RefreshCw, Download, Bug, Play, Square } from "lucide-react"

interface DebugStatusResponse {
  debug_enabled: boolean
  active_jobs_with_debug: string[]
  recent_debug_files: {
    filename: string
    job_id: string
    created_at: string
    size_bytes: number
    path: string
  }[]
}

interface DebugSummary {
  debug_enabled: boolean
  job_id: string
  duration_seconds: number
  total_requests: number
  successful_requests: number
  failed_requests: number
  success_rate_percent: number
  status_code_breakdown: Record<string, number>
  failure_patterns: {
    poster_id: string
    status_code: number
    error_body: string
  }[]
  recommendations: string[]
}

interface JobDebugSummaryResponse {
  success: boolean
  debug_summary?: DebugSummary
  error?: string
}

export function BatchDebugTab() {
  const [debugStatus, setDebugStatus] = useState<DebugStatusResponse | null>(null)
  const [debugDuration, setDebugDuration] = useState(30)
  const [selectedJobSummary, setSelectedJobSummary] = useState<JobDebugSummaryResponse | null>(null)
  const [loading, setLoading] = useState<Record<string, boolean>>({})

  const loadDebugStatus = async () => {
    setLoading(prev => ({ ...prev, 'status': true }))
    try {
      const response = await fetch('/api/v1/batch-debug/status')
      const status = await response.json()
      setDebugStatus(status)
    } catch (error) {
      console.error('Failed to load debug status:', error)
      setDebugStatus(null)
    } finally {
      setLoading(prev => ({ ...prev, 'status': false }))
    }
  }

  const enableDebugMode = async () => {
    setLoading(prev => ({ ...prev, 'enable': true }))
    try {
      const response = await fetch('/api/v1/batch-debug/enable', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration_minutes: debugDuration })
      })
      
      if (response.ok) {
        await loadDebugStatus()
      } else {
        console.error('Failed to enable debug mode')
      }
    } catch (error) {
      console.error('Error enabling debug mode:', error)
    } finally {
      setLoading(prev => ({ ...prev, 'enable': false }))
    }
  }

  const disableDebugMode = async () => {
    setLoading(prev => ({ ...prev, 'disable': true }))
    try {
      const response = await fetch('/api/v1/batch-debug/disable', {
        method: 'POST'
      })
      
      if (response.ok) {
        await loadDebugStatus()
      } else {
        console.error('Failed to disable debug mode')
      }
    } catch (error) {
      console.error('Error disabling debug mode:', error)
    } finally {
      setLoading(prev => ({ ...prev, 'disable': false }))
    }
  }

  const loadJobDebugSummary = async (jobId: string) => {
    setLoading(prev => ({ ...prev, [`summary-${jobId}`]: true }))
    try {
      const response = await fetch(`/api/v1/batch-debug/job/${jobId}/summary`)
      const summary = await response.json()
      setSelectedJobSummary(summary)
    } catch (error) {
      console.error(`Failed to load debug summary for job ${jobId}:`, error)
      setSelectedJobSummary({
        success: false,
        error: 'Failed to load debug summary'
      })
    } finally {
      setLoading(prev => ({ ...prev, [`summary-${jobId}`]: false }))
    }
  }

  const downloadDebugLog = async (jobId: string, filename: string) => {
    try {
      const response = await fetch(`/api/v1/batch-debug/job/${jobId}/full-log`)
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        console.error('Failed to download debug log')
      }
    } catch (error) {
      console.error('Error downloading debug log:', error)
    }
  }

  const cleanupDebugFiles = async (days: number = 7) => {
    setLoading(prev => ({ ...prev, 'cleanup': true }))
    try {
      const response = await fetch(`/api/v1/batch-debug/cleanup?days=${days}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        await loadDebugStatus()
      } else {
        console.error('Failed to cleanup debug files')
      }
    } catch (error) {
      console.error('Error cleaning up debug files:', error)
    } finally {
      setLoading(prev => ({ ...prev, 'cleanup': false }))
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  useEffect(() => {
    loadDebugStatus()
  }, [])

  return (
    <div className="space-y-4">
      {/* Debug Mode Control */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bug className="h-5 w-5" />
            Batch Processing Debug Mode
          </CardTitle>
          <CardDescription>
            Enable comprehensive logging for batch processing jobs to diagnose connection issues
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Debug Status</p>
              <div className="flex items-center gap-2 mt-1">
                {debugStatus?.debug_enabled ? (
                  <>
                    <Badge variant="default" className="bg-green-500">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      ENABLED
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      Debug logging is active for all new batch jobs
                    </span>
                  </>
                ) : (
                  <>
                    <Badge variant="secondary">
                      <XCircle className="h-3 w-3 mr-1" />
                      DISABLED
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      No debug logging for batch jobs
                    </span>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                onClick={loadDebugStatus}
                disabled={loading.status}
                size="sm"
                variant="outline"
              >
                {loading.status ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                Refresh
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Label htmlFor="debug-duration">Duration (minutes):</Label>
              <Input
                id="debug-duration"
                type="number"
                value={debugDuration}
                onChange={(e) => setDebugDuration(Number(e.target.value))}
                min={5}
                max={120}
                className="w-20"
              />
            </div>
            
            {debugStatus?.debug_enabled ? (
              <Button
                onClick={disableDebugMode}
                disabled={loading.disable}
                variant="destructive"
                size="sm"
              >
                {loading.disable ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Square className="h-4 w-4 mr-2" />
                )}
                Disable Debug Mode
              </Button>
            ) : (
              <Button
                onClick={enableDebugMode}
                disabled={loading.enable}
                size="sm"
              >
                {loading.enable ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Play className="h-4 w-4 mr-2" />
                )}
                Enable Debug Mode
              </Button>
            )}
          </div>

          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>How to use:</strong>
              <br />1. Enable debug mode before starting batch jobs that are failing
              <br />2. Run your batch job as normal
              <br />3. Review the debug summary and detailed logs below
              <br />4. Debug mode will automatically disable after the specified duration
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Recent Debug Files */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Debug Sessions</CardTitle>
          <CardDescription>
            View and download debug information from recent batch processing jobs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              {debugStatus?.recent_debug_files?.length || 0} debug files available
            </p>
            <Button
              onClick={() => cleanupDebugFiles(7)}
              disabled={loading.cleanup}
              size="sm"
              variant="outline"
            >
              {loading.cleanup ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                "Cleanup Old Files"
              )}
            </Button>
          </div>

          {debugStatus?.recent_debug_files && debugStatus.recent_debug_files.length > 0 ? (
            <div className="space-y-3">
              {debugStatus.recent_debug_files.map((file, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Job ID: {file.job_id}</p>
                      <p className="text-sm text-muted-foreground">
                        Created: {formatDate(file.created_at)} • Size: {formatBytes(file.size_bytes)}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={() => loadJobDebugSummary(file.job_id)}
                        disabled={loading[`summary-${file.job_id}`]}
                        size="sm"
                        variant="outline"
                      >
                        {loading[`summary-${file.job_id}`] ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "View Summary"
                        )}
                      </Button>
                      <Button
                        onClick={() => downloadDebugLog(file.job_id, file.filename)}
                        size="sm"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download Full Log
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No debug files available. Enable debug mode and run batch jobs to generate debug information.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Debug Summary Display */}
      {selectedJobSummary && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {selectedJobSummary.success ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
              Debug Summary
              {selectedJobSummary.debug_summary && (
                <span className="text-sm font-normal text-muted-foreground">
                  - Job {selectedJobSummary.debug_summary.job_id}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedJobSummary.error ? (
              <Alert variant="destructive">
                <AlertDescription>{selectedJobSummary.error}</AlertDescription>
              </Alert>
            ) : selectedJobSummary.debug_summary ? (
              <div className="space-y-4">
                {/* Performance Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 border rounded">
                    <p className="text-2xl font-bold text-green-600">
                      {selectedJobSummary.debug_summary.success_rate_percent}%
                    </p>
                    <p className="text-sm text-muted-foreground">Success Rate</p>
                  </div>
                  <div className="text-center p-3 border rounded">
                    <p className="text-2xl font-bold">
                      {selectedJobSummary.debug_summary.total_requests}
                    </p>
                    <p className="text-sm text-muted-foreground">Total Requests</p>
                  </div>
                  <div className="text-center p-3 border rounded">
                    <p className="text-2xl font-bold text-red-600">
                      {selectedJobSummary.debug_summary.failed_requests}
                    </p>
                    <p className="text-sm text-muted-foreground">Failed Requests</p>
                  </div>
                  <div className="text-center p-3 border rounded">
                    <p className="text-2xl font-bold">
                      {Math.round(selectedJobSummary.debug_summary.duration_seconds)}s
                    </p>
                    <p className="text-sm text-muted-foreground">Duration</p>
                  </div>
                </div>

                {/* Status Code Breakdown */}
                {Object.keys(selectedJobSummary.debug_summary.status_code_breakdown).length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">HTTP Status Codes</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(selectedJobSummary.debug_summary.status_code_breakdown).map(([code, count]) => (
                        <Badge
                          key={code}
                          variant={code.startsWith('2') ? 'default' : 'destructive'}
                        >
                          {code}: {count}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Failure Patterns */}
                {selectedJobSummary.debug_summary.failure_patterns.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Failure Patterns</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedJobSummary.debug_summary.failure_patterns.map((failure, index) => (
                        <div key={index} className="border rounded p-3 text-sm">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-mono">{failure.poster_id.substring(0, 8)}...</span>
                            <Badge variant="destructive">HTTP {failure.status_code}</Badge>
                          </div>
                          {failure.error_body && (
                            <p className="text-muted-foreground text-xs">{failure.error_body}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {selectedJobSummary.debug_summary.recommendations.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Recommendations</h4>
                    <ul className="space-y-1">
                      {selectedJobSummary.debug_summary.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-blue-500 mt-1">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : null}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
