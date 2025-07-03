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

export default function JellyfinDiagnosticsPage() {
  const [connectionResult, setConnectionResult] = useState<DiagnosticResult | null>(null)
  const [configResult, setConfigResult] = useState<DiagnosticResult | null>(null)
  const [mediaTests, setMediaTests] = useState<MediaItemTest[]>([])
  const [customIdTest, setCustomIdTest] = useState<DiagnosticResult | null>(null)
  const [customId, setCustomId] = useState("")
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

      <Tabs defaultValue="connection" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="connection">Connection</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="media">Media Tests</TabsTrigger>
          <TabsTrigger value="custom">Custom ID Test</TabsTrigger>
        </TabsList>

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
                    <p className="text-sm">{configResult.details.api_key}</p>
                  </div>
                  <div>
                    <Label>User ID</Label>
                    <p className="text-sm">{configResult.details.user_id}</p>
                  </div>
                  <div>
                    <Label>Settings Loaded</Label>
                    <p className="text-sm">{configResult.details.settings_loaded ? 'Yes' : 'No'}</p>
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
