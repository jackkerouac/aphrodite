"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, CheckCircle, XCircle, AlertTriangle, RefreshCw } from "lucide-react"
import { BatchDebugTab } from "@/components/diagnostics/batch-debug-tab"

interface DiagnosticResult {
  success: boolean
  message: string
  details?: any
}

interface MediaItemTest {
  jellyfin_id: string
  title: string
  metadata_available: boolean
  poster_available: boolean
  error_message?: string
}

interface BatchJobResult {
  job_id: string
  status: string
  total_posters: number
  completed_posters: number
  failed_posters: number
  error_message?: string
  sample_failed_ids: string[]
}

interface BatchJobDiagnosis {
  success: boolean
  message: string
  details: {
    job_info: {
      id: string
      status: string
      total_posters: number
      completed_posters: number
      failed_posters: number
      badge_types: string[]
      error_message?: string
    }
    tested_poster_ids: string[]
    poster_test_results: MediaItemTest[]
    summary: {
      total_tested: number
      successful: number
      failed: number
    }
  }
}

interface InfrastructureResult {
  success: boolean
  message: string
  details: any
}

interface ComponentStatus {
  name: string
  status: string
  message: string
  details?: any
}

interface SystemOverview {
  overall_status: string
  components: ComponentStatus[]
  timestamp: string
}

export default function JellyfinDiagnosticsPage() {
  const [connectionResult, setConnectionResult] = useState<DiagnosticResult | null>(null)
  const [configResult, setConfigResult] = useState<DiagnosticResult | null>(null)
  const [mediaTests, setMediaTests] = useState<MediaItemTest[]>([])
  const [customIdTest, setCustomIdTest] = useState<DiagnosticResult | null>(null)
  const [customId, setCustomId] = useState("")
  const [batchJobs, setBatchJobs] = useState<BatchJobResult[]>([])
  const [selectedJobDiagnosis, setSelectedJobDiagnosis] = useState<BatchJobDiagnosis | null>(null)
  const [systemOverview, setSystemOverview] = useState<SystemOverview | null>(null)
  const [redisResult, setRedisResult] = useState<InfrastructureResult | null>(null)
  const [celeryResult, setCeleryResult] = useState<InfrastructureResult | null>(null)
  const [databaseResult, setDatabaseResult] = useState<InfrastructureResult | null>(null)
  const [workflowResult, setWorkflowResult] = useState<InfrastructureResult | null>(null)
  const [loading, setLoading] = useState<Record<string, boolean>>({})

  const runTest = async (testName: string, endpoint: string, setter: (result: DiagnosticResult) => void) => {
    setLoading(prev => ({ ...prev, [testName]: true }))
    try {
      const response = await fetch(`/api/v1/diagnostics/jellyfin/${endpoint}`)
      const result = await response.json()
      setter(result)
    } catch (error) {
      setter({
        success: false,
        message: `Failed to run test: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: {}
      })
    } finally {
      setLoading(prev => ({ ...prev, [testName]: false }))
    }
  }

  const runInfrastructureTest = async (testName: string, endpoint: string, setter: (result: InfrastructureResult) => void) => {
    setLoading(prev => ({ ...prev, [testName]: true }))
    try {
      const response = await fetch(`/api/v1/diagnostics/infrastructure/${endpoint}`)
      const result = await response.json()
      setter(result)
    } catch (error) {
      setter({
        success: false,
        message: `Failed to run test: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: {}
      })
    } finally {
      setLoading(prev => ({ ...prev, [testName]: false }))
    }
  }

  const loadSystemOverview = async () => {
    setLoading(prev => ({ ...prev, 'overview': true }))
    try {
      const response = await fetch('/api/v1/diagnostics/infrastructure/overview')
      const result = await response.json()
      setSystemOverview(result)
    } catch (error) {
      setSystemOverview(null)
    } finally {
      setLoading(prev => ({ ...prev, 'overview': false }))
    }
  }

  const runMediaTest = async () => {
    setLoading(prev => ({ ...prev, 'media': true }))
    try {
      const response = await fetch('/api/v1/diagnostics/jellyfin/media-sample')
      const results = await response.json()
      setMediaTests(results)
    } catch (error) {
      setMediaTests([])
    } finally {
      setLoading(prev => ({ ...prev, 'media': false }))
    }
  }

  const runCustomIdTest = async () => {
    if (!customId.trim()) return
    
    setLoading(prev => ({ ...prev, 'custom': true }))
    try {
      const response = await fetch(`/api/v1/diagnostics/jellyfin/test-id/${encodeURIComponent(customId.trim())}`, {
        method: 'POST'
      })
      const result = await response.json()
      setCustomIdTest(result)
    } catch (error) {
      setCustomIdTest({
        success: false,
        message: `Failed to test ID: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: {}
      })
    } finally {
      setLoading(prev => ({ ...prev, 'custom': false }))
    }
  }

  const loadFailedBatchJobs = async () => {
    setLoading(prev => ({ ...prev, 'batch': true }))
    try {
      const response = await fetch('/api/v1/diagnostics/jellyfin/batch-jobs/failed')
      const jobs = await response.json()
      setBatchJobs(jobs)
    } catch (error) {
      setBatchJobs([])
    } finally {
      setLoading(prev => ({ ...prev, 'batch': false }))
    }
  }

  const diagnoseBatchJob = async (jobId: string) => {
    setLoading(prev => ({ ...prev, [`job-${jobId}`]: true }))
    try {
      const response = await fetch(`/api/v1/diagnostics/jellyfin/batch-jobs/${jobId}/diagnose`, {
        method: 'POST'
      })
      const diagnosis = await response.json()
      setSelectedJobDiagnosis(diagnosis)
    } catch (error) {
      setSelectedJobDiagnosis({
        success: false,
        message: `Failed to diagnose job: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: {
          job_info: { id: jobId, status: 'unknown', total_posters: 0, completed_posters: 0, failed_posters: 0, badge_types: [] },
          tested_poster_ids: [],
          poster_test_results: [],
          summary: { total_tested: 0, successful: 0, failed: 0 }
        }
      })
    } finally {
      setLoading(prev => ({ ...prev, [`job-${jobId}`]: false }))
    }
  }

  const getStatusIcon = (success: boolean | null) => {
    if (success === null) return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    return success ? <CheckCircle className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />
  }

  const getStatusBadge = (success: boolean | null) => {
    if (success === null) return <Badge variant="secondary">Unknown</Badge>
    return success ? 
      <Badge variant="default" className="bg-green-500">Success</Badge> :
      <Badge variant="destructive">Failed</Badge>
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Jellyfin Diagnostics</h1>
        <p className="text-muted-foreground">
          Diagnose Jellyfin connectivity and data issues
        </p>
      </div>

      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Use these diagnostics to troubleshoot issues with badge processing and Jellyfin connectivity.
          Common problems include invalid Jellyfin IDs, authentication issues, or configuration problems.
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-8">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="connection">Connection</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="infrastructure">Infrastructure</TabsTrigger>
          <TabsTrigger value="media">Media Tests</TabsTrigger>
          <TabsTrigger value="batch">Batch Jobs</TabsTrigger>
          <TabsTrigger value="debug">Batch Debug</TabsTrigger>
          <TabsTrigger value="custom">Custom ID Test</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Overview</CardTitle>
              <CardDescription>
                Get a high-level view of all infrastructure components
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Overall System Status</p>
                  <p className="text-sm text-muted-foreground">
                    {systemOverview ? 
                      `Last checked: ${new Date(systemOverview.timestamp).toLocaleString()}` : 
                      "Not checked yet"
                    }
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {systemOverview && (
                    <Badge variant={systemOverview.overall_status === "healthy" ? "default" : "destructive"}>
                      {systemOverview.overall_status.toUpperCase()}
                    </Badge>
                  )}
                  <Button
                    onClick={loadSystemOverview}
                    disabled={loading.overview}
                    size="sm"
                  >
                    {loading.overview ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    Check All Systems
                  </Button>
                </div>
              </div>

              {systemOverview && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {systemOverview.components.map((component, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        {component.status === "healthy" ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : component.status === "degraded" ? (
                          <AlertTriangle className="h-4 w-4 text-yellow-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="font-medium">{component.name}</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{component.message}</p>
                      {component.details?.worker_count && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Workers: {component.details.worker_count}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="infrastructure" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Redis Test */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(redisResult?.success || null)}
                  Redis Infrastructure
                </CardTitle>
                <CardDescription>
                  Test Redis broker and result backend connectivity
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Redis Status</p>
                    <p className="text-sm text-muted-foreground">
                      {redisResult?.message || "Not tested yet"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(redisResult?.success || null)}
                    <Button
                      onClick={() => runInfrastructureTest('redis', 'redis', setRedisResult)}
                      disabled={loading.redis}
                      size="sm"
                    >
                      {loading.redis ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      Test Redis
                    </Button>
                  </div>
                </div>

                {redisResult?.details && (
                  <div className="space-y-2 text-sm">
                    {redisResult.details.broker && (
                      <div>
                        <p className="font-medium">Broker:</p>
                        <p className="text-muted-foreground">
                          {redisResult.details.broker.ping_successful ? "✓ Connected" : "✗ Failed"}
                          {redisResult.details.broker.redis_version && (
                            ` (Redis ${redisResult.details.broker.redis_version})`
                          )}
                        </p>
                      </div>
                    )}
                    {redisResult.details.performance && (
                      <div>
                        <p className="font-medium">Performance:</p>
                        <p className="text-muted-foreground">
                          Write: {redisResult.details.performance.write_time_ms}ms, 
                          Read: {redisResult.details.performance.read_time_ms}ms
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Celery Test */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(celeryResult?.success || null)}
                  Celery Workers
                </CardTitle>
                <CardDescription>
                  Test Celery worker availability and task registration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Celery Status</p>
                    <p className="text-sm text-muted-foreground">
                      {celeryResult?.message || "Not tested yet"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(celeryResult?.success || null)}
                    <Button
                      onClick={() => runInfrastructureTest('celery', 'celery', setCeleryResult)}
                      disabled={loading.celery}
                      size="sm"
                    >
                      {loading.celery ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      Test Celery
                    </Button>
                  </div>
                </div>

                {celeryResult?.details && (
                  <div className="space-y-2 text-sm">
                    {celeryResult.details.workers && (
                      <div>
                        <p className="font-medium">Workers:</p>
                        <p className="text-muted-foreground">
                          {celeryResult.details.workers.workers_available ? 
                            `${Object.keys(celeryResult.details.workers.active_workers || {}).length} active` :
                            "No workers found"
                          }
                        </p>
                      </div>
                    )}
                    {celeryResult.details.task_registration && (
                      <div>
                        <p className="font-medium">Tasks:</p>
                        <p className="text-muted-foreground">
                          {celeryResult.details.task_registration.target_task_registered ? 
                            "✓ Batch task registered" : "✗ Batch task missing"
                          }
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Database Test */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(databaseResult?.success || null)}
                  Database
                </CardTitle>
                <CardDescription>
                  Test database connectivity and performance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Database Status</p>
                    <p className="text-sm text-muted-foreground">
                      {databaseResult?.message || "Not tested yet"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(databaseResult?.success || null)}
                    <Button
                      onClick={() => runInfrastructureTest('database', 'database', setDatabaseResult)}
                      disabled={loading.database}
                      size="sm"
                    >
                      {loading.database ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      Test Database
                    </Button>
                  </div>
                </div>

                {databaseResult?.details && (
                  <div className="space-y-2 text-sm">
                    {databaseResult.details.performance && (
                      <div>
                        <p className="font-medium">Performance:</p>
                        <p className="text-muted-foreground">
                          Query time: {databaseResult.details.performance.query_time_ms}ms
                        </p>
                        <p className="text-muted-foreground">
                          Batch jobs: {databaseResult.details.performance.batch_jobs_count}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Workflow Test */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(workflowResult?.success || null)}
                  Batch Workflow
                </CardTitle>
                <CardDescription>
                  Test complete batch processing workflow
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Workflow Status</p>
                    <p className="text-sm text-muted-foreground">
                      {workflowResult?.message || "Not tested yet"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(workflowResult?.success || null)}
                    <Button
                      onClick={() => {
                        // Special handling for workflow test which requires POST
                        if (loading.workflow) return;
                        setLoading(prev => ({ ...prev, workflow: true }));
                        fetch('/api/v1/diagnostics/infrastructure/test-batch-workflow', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' }
                        })
                        .then(response => response.json())
                        .then(result => setWorkflowResult(result))
                        .catch(error => setWorkflowResult({
                          success: false,
                          message: `Failed to run test: ${error.message}`,
                          details: {}
                        }))
                        .finally(() => setLoading(prev => ({ ...prev, workflow: false })));
                      }}
                      disabled={loading.workflow}
                      size="sm"
                    >
                      {loading.workflow ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      Test Workflow
                    </Button>
                  </div>
                </div>

                {workflowResult?.details && (
                  <div className="space-y-2 text-sm">
                    {workflowResult.details.summary && (
                      <div>
                        <p className="font-medium">Components:</p>
                        {workflowResult.details.summary.successful_components.map((comp: string) => (
                          <p key={comp} className="text-green-600">✓ {comp.replace('_', ' ')}</p>
                        ))}
                        {workflowResult.details.summary.failed_components.map((comp: string) => (
                          <p key={comp} className="text-red-600">✗ {comp.replace('_', ' ')}</p>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Troubleshooting Tips:</strong>
              <br />• <strong>Redis failures:</strong> Check if Redis is running and accessible
              <br />• <strong>Celery failures:</strong> Ensure Celery workers are started with correct configuration
              <br />• <strong>Database failures:</strong> Verify PostgreSQL is running and connection settings are correct
              <br />• <strong>Workflow failures:</strong> Usually indicates a combination of the above issues
            </AlertDescription>
          </Alert>
        </TabsContent>

        <TabsContent value="connection" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getStatusIcon(connectionResult?.success || null)}
                Jellyfin Connection Test
              </CardTitle>
              <CardDescription>
                Test basic connectivity to your Jellyfin server
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Connection Status</p>
                  <p className="text-sm text-muted-foreground">
                    {connectionResult?.message || "Not tested yet"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(connectionResult?.success || null)}
                  <Button
                    onClick={() => runTest('connection', 'connection', setConnectionResult)}
                    disabled={loading.connection}
                    size="sm"
                  >
                    {loading.connection ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    Test Connection
                  </Button>
                </div>
              </div>

              {connectionResult?.details && (
                <div className="space-y-2">
                  {connectionResult.details.libraries && (
                  <div>
                  <p className="font-medium">Libraries Found: {connectionResult.details.libraries.count}</p>
                  {connectionResult.details.libraries.available?.map((lib: any, index: number) => (
                  <p key={index} className="text-sm text-muted-foreground">
                  • {lib.name} {lib.id ? `(ID: ${lib.id})` : '(No ID field)'}
                  </p>
                  ))}
                  </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="batch" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Failed Batch Jobs Analysis</CardTitle>
              <CardDescription>
                Analyze recent failed batch jobs to identify poster download issues
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <p className="text-sm text-muted-foreground">
                  {batchJobs.length > 0 ? `Found ${batchJobs.length} jobs with failures` : "No failed jobs loaded"}
                </p>
                <Button
                  onClick={loadFailedBatchJobs}
                  disabled={loading.batch}
                  size="sm"
                >
                  {loading.batch ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                  Load Failed Jobs
                </Button>
              </div>

              {batchJobs.length > 0 && (
                <div className="space-y-3">
                  {batchJobs.map((job) => (
                    <div key={job.job_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="font-medium">Job ID: {job.job_id}</p>
                          <div className="flex gap-2 mt-1">
                            <Badge variant={job.status === 'COMPLETED' ? 'default' : 'destructive'}>
                              {job.status}
                            </Badge>
                            <Badge variant="outline">
                              {job.completed_posters}/{job.total_posters} completed
                            </Badge>
                            {job.failed_posters > 0 && (
                              <Badge variant="destructive">
                                {job.failed_posters} failed
                              </Badge>
                            )}
                          </div>
                        </div>
                        <Button
                          onClick={() => diagnoseBatchJob(job.job_id)}
                          disabled={loading[`job-${job.job_id}`]}
                          size="sm"
                        >
                          {loading[`job-${job.job_id}`] ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            "Diagnose"
                          )}
                        </Button>
                      </div>
                      
                      {job.error_message && (
                        <p className="text-sm text-red-600 mb-2">Error: {job.error_message}</p>
                      )}
                      
                      {job.sample_failed_ids.length > 0 && (
                        <div>
                          <p className="text-sm font-medium mb-1">Sample Poster IDs:</p>
                          <div className="flex flex-wrap gap-1">
                            {job.sample_failed_ids.map((id, index) => (
                              <code key={index} className="text-xs bg-gray-100 px-1 rounded">
                                {id.substring(0, 8)}...
                              </code>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {selectedJobDiagnosis && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(selectedJobDiagnosis.success)}
                  Batch Job Diagnosis Results
                </CardTitle>
                <CardDescription>
                  Detailed analysis of poster download failures
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  {getStatusBadge(selectedJobDiagnosis.success)}
                  <span className="font-medium">{selectedJobDiagnosis.message}</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center p-3 border rounded">
                    <p className="text-2xl font-bold text-green-600">
                      {selectedJobDiagnosis.details.summary.successful}
                    </p>
                    <p className="text-sm text-muted-foreground">Working</p>
                  </div>
                  <div className="text-center p-3 border rounded">
                    <p className="text-2xl font-bold text-red-600">
                      {selectedJobDiagnosis.details.summary.failed}
                    </p>
                    <p className="text-sm text-muted-foreground">Failed</p>
                  </div>
                  <div className="text-center p-3 border rounded">
                    <p className="text-2xl font-bold">
                      {selectedJobDiagnosis.details.summary.total_tested}
                    </p>
                    <p className="text-sm text-muted-foreground">Total Tested</p>
                  </div>
                </div>

                {selectedJobDiagnosis.details.poster_test_results.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Poster Test Results:</h4>
                    <div className="space-y-2">
                      {selectedJobDiagnosis.details.poster_test_results.map((test, index) => (
                        <div key={index} className="border rounded-lg p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">{test.title}</p>
                              <p className="text-xs text-muted-foreground">ID: {test.jellyfin_id}</p>
                            </div>
                            <div className="flex gap-2">
                              <Badge variant={test.metadata_available ? "default" : "destructive"}>
                                {test.metadata_available ? "Metadata ✓" : "Metadata ✗"}
                              </Badge>
                              <Badge variant={test.poster_available ? "default" : "destructive"}>
                                {test.poster_available ? "Poster ✓" : "Poster ✗"}
                              </Badge>
                            </div>
                          </div>
                          {test.error_message && (
                            <p className="text-sm text-red-600 mt-2">{test.error_message}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Next Steps:</strong>
                    <br />• If all tests fail: Check Jellyfin configuration and authentication
                    <br />• If some tests fail: Verify that these specific poster IDs exist in Jellyfin
                    <br />• If tests work but batch jobs fail: Check worker environment differences
                    <br />• Use the Custom ID Test tab to test specific failing poster IDs
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getStatusIcon(configResult?.success || null)}
                Jellyfin Configuration Check
              </CardTitle>
              <CardDescription>
                Verify your Jellyfin settings are properly configured
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Configuration Status</p>
                  <p className="text-sm text-muted-foreground">
                    {configResult?.message || "Not checked yet"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(configResult?.success || null)}
                  <Button
                    onClick={() => runTest('config', 'config', setConfigResult)}
                    disabled={loading.config}
                    size="sm"
                  >
                    {loading.config ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    Check Config
                  </Button>
                </div>
              </div>

              {configResult?.details && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Base URL</Label>
                    <p className="text-sm">{configResult.details.base_url}</p>
                  </div>
                  <div>
                    <Label>API Key</Label>
                    <div className="flex items-center gap-2">
                      <p className="text-sm">{configResult.details.api_key}</p>
                      {configResult.details.api_key_valid !== undefined && (
                        <Badge variant={configResult.details.api_key_valid ? "default" : "destructive"}>
                          {configResult.details.api_key_valid ? "Valid" : "Invalid"}
                        </Badge>
                      )}
                    </div>
                    {configResult.details.api_key_error && (
                      <p className="text-xs text-red-600">{configResult.details.api_key_error}</p>
                    )}
                    {configResult.details.connection_message && (
                      <p className="text-xs text-green-600">{configResult.details.connection_message}</p>
                    )}
                  </div>
                  <div>
                    <Label>User ID</Label>
                    <p className="text-sm">{configResult.details.user_id}</p>
                  </div>
                  <div>
                    <Label>User ID Validation</Label>
                    <div className="flex items-center gap-2">
                      <p className="text-sm">{configResult.details.settings_loaded ? 'Yes' : 'No'}</p>
                      {configResult.details.user_id_valid !== undefined && (
                        <Badge variant={configResult.details.user_id_valid ? "default" : "destructive"}>
                          {configResult.details.user_id_valid ? "Valid" : "Invalid"}
                        </Badge>
                      )}
                    </div>
                    {configResult.details.user_id_error && (
                      <p className="text-xs text-red-600">{configResult.details.user_id_error}</p>
                    )}
                    {configResult.details.libraries_count !== undefined && (
                      <p className="text-xs text-green-600">Found {configResult.details.libraries_count} libraries</p>
                    )}
                  </div>
                </div>
              )}

              {configResult?.details?.missing_settings?.length > 0 && (
                <Alert variant="destructive">
                  <AlertDescription>
                    Missing configuration: {configResult.details.missing_settings.join(', ')}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="media" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Media Item Tests</CardTitle>
              <CardDescription>
                Test a sample of media items directly from your Jellyfin libraries to check API compatibility
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <p className="text-sm text-muted-foreground">
                  {mediaTests.length > 0 ? `Tested ${mediaTests.length} items` : "No tests run yet"}
                </p>
                <Button
                  onClick={runMediaTest}
                  disabled={loading.media}
                  size="sm"
                >
                  {loading.media ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                  Test Media Items
                </Button>
              </div>

              {mediaTests.length > 0 && (
                <div className="space-y-2">
                  {mediaTests.map((test, index) => (
                    <div key={index} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{test.title}</p>
                          <p className="text-xs text-muted-foreground">ID: {test.jellyfin_id}</p>
                        </div>
                        <div className="flex gap-2">
                          <Badge variant={test.metadata_available ? "default" : "destructive"}>
                            {test.metadata_available ? "Metadata ✓" : "Metadata ✗"}
                          </Badge>
                          <Badge variant={test.poster_available ? "default" : "destructive"}>
                            {test.poster_available ? "Poster ✓" : "Poster ✗"}
                          </Badge>
                        </div>
                      </div>
                      {test.error_message && (
                        <p className="text-sm text-red-600 mt-2">{test.error_message}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="debug" className="space-y-4">
          <BatchDebugTab />
        </TabsContent>

        <TabsContent value="custom" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Specific Jellyfin ID</CardTitle>
              <CardDescription>
                Test a specific Jellyfin ID to diagnose issues (useful for debugging failed processing)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <div className="flex-1">
                  <Label htmlFor="custom-id">Jellyfin Item ID</Label>
                  <Input
                    id="custom-id"
                    value={customId}
                    onChange={(e) => setCustomId(e.target.value)}
                    placeholder="6ca81413a5022330ba7229693796c553"
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={runCustomIdTest}
                    disabled={loading.custom || !customId.trim()}
                  >
                    {loading.custom ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      "Test ID"
                    )}
                  </Button>
                </div>
              </div>

              {customIdTest && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(customIdTest.success)}
                    <span className="font-medium">{customIdTest.message}</span>
                  </div>

                  {customIdTest.details?.tests && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {Object.entries(customIdTest.details.tests).map(([testName, result]: [string, any]) => (
                        <div key={testName} className="border rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-2">
                            {getStatusIcon(result.success)}
                            <span className="font-medium capitalize">{testName}</span>
                          </div>
                          {result.item_name && (
                            <p className="text-sm">Item: {result.item_name}</p>
                          )}
                          {result.url && (
                            <p className="text-xs text-muted-foreground break-all">URL: {result.url}</p>
                          )}
                          {result.error && (
                            <p className="text-sm text-red-600">{result.error}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Common Issues:</strong>
              <br />• HTTP 400: Invalid or deleted Jellyfin item ID
              <br />• HTTP 401: Authentication failure (check API key)
              <br />• HTTP 404: Item not found in Jellyfin
              <br />• Network errors: Check Jellyfin URL and connectivity
            </AlertDescription>
          </Alert>
        </TabsContent>
      </Tabs>
    </div>
  )
}
