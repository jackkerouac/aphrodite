import React, { useState } from "react";
import { Button, Progress, Card, CardContent, AlertCircle, Badge, ScrollArea, Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui";
import { useRunAphrodite } from "./RunAphroditeContext";
import { XCircle, CheckCircle, RefreshCw, StopCircle, CopyCheck, HelpCircle } from "lucide-react";
import apiClient from "@/lib/api-client";
import { toast } from "sonner";

export const ProcessingStep: React.FC = () => {
  const { 
    stepData, 
    connected, 
    jobStatus, 
    jobProgress, 
    jobError, 
    setCurrentStep, 
    currentStep 
  } = useRunAphrodite();
  
  const [processingLog, setProcessingLog] = useState<Array<{message: string; timestamp: string; type: 'info' | 'error' | 'success'}>>([]);
  const [isCancelling, setIsCancelling] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  // Function to add log entries
  const addLogEntry = (message: string, type: 'info' | 'error' | 'success' = 'info') => {
    setProcessingLog(prev => [
      ...prev,
      {
        message,
        timestamp: new Date().toLocaleTimeString(),
        type
      }
    ]);
  };

  // Function to handle retry for failed jobs
  const handleRetry = async () => {
    if (!stepData.jobId) return;
    
    try {
      setIsRetrying(true);
      addLogEntry('Retrying failed items...', 'info');
      
      // API call to retry the job
      await apiClient.jobs.startProcessing(stepData.jobId);
      
      addLogEntry('Retry initiated successfully', 'success');
      toast.success('Retrying failed items');
    } catch (error) {
      console.error('Failed to retry job:', error);
      addLogEntry(`Failed to retry: ${(error as Error).message}`, 'error');
      toast.error('Failed to retry job');
    } finally {
      setIsRetrying(false);
    }
  };

  // Function to handle job cancellation
  const handleCancel = async () => {
    if (!stepData.jobId) return;
    
    try {
      setIsCancelling(true);
      addLogEntry('Cancelling job...', 'info');
      
      // API call to cancel the job
      await apiClient.jobs.updateJobStatus(stepData.jobId, 'failed');
      
      addLogEntry('Job cancelled', 'info');
      toast.success('Job cancelled');
    } catch (error) {
      console.error('Failed to cancel job:', error);
      addLogEntry(`Failed to cancel: ${(error as Error).message}`, 'error');
      toast.error('Failed to cancel job');
    } finally {
      setIsCancelling(false);
    }
  };

  // Add to log when status changes
  React.useEffect(() => {
    if (jobStatus) {
      addLogEntry(`Job status: ${jobStatus.status}`, jobStatus.status === 'failed' ? 'error' : jobStatus.status === 'completed' ? 'success' : 'info');
    }
  }, [jobStatus?.status]);

  // Add to log when progress updates
  React.useEffect(() => {
    if (jobProgress && jobProgress.status === 'failed' && jobProgress.error) {
      addLogEntry(`Error: ${jobProgress.error}`, 'error');
    }
  }, [jobProgress?.error]);

  // Add to log when job has an error
  React.useEffect(() => {
    if (jobError) {
      addLogEntry(`Job Error: ${jobError.error}`, 'error');
    }
  }, [jobError]);

  // Determine job status for display
  const getStatusBadge = () => {
    if (!jobStatus) return null;
    
    switch (jobStatus.status) {
      case 'pending':
        return <Badge variant="outline" className="bg-amber-50 text-amber-700">Pending</Badge>;
      case 'running':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700">Running</Badge>;
      case 'completed':
        return <Badge variant="outline" className="bg-green-50 text-green-700">Completed</Badge>;
      case 'failed':
        return <Badge variant="outline" className="bg-red-50 text-red-700">Failed</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-muted-foreground">Processing selected items and applying badges.</p>
      
      {stepData.jobId ? (
        <div className="space-y-4">
          <Tabs defaultValue="status">
            <TabsList className="mb-4">
              <TabsTrigger value="status">Status</TabsTrigger>
              <TabsTrigger value="log">Log</TabsTrigger>
            </TabsList>
            
            <TabsContent value="status">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="font-medium">Job ID: {stepData.jobId}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-sm text-muted-foreground">
                          {connected ? 'Connected' : 'Disconnected'}
                        </span>
                      </div>
                    </div>
                    <div>{getStatusBadge()}</div>
                  </div>
                  
                  {jobStatus && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="border rounded-md p-3 flex flex-col items-center justify-center">
                        <div className="text-3xl font-semibold">{jobStatus.totalItems || 0}</div>
                        <div className="text-sm text-muted-foreground">Total Items</div>
                      </div>
                      
                      <div className="border rounded-md p-3 flex flex-col items-center justify-center">
                        <div className="text-3xl font-semibold text-green-600">
                          {jobStatus.processedCount !== undefined ? jobStatus.processedCount - (jobStatus.failedCount || 0) : 0}
                        </div>
                        <div className="text-sm text-muted-foreground">Successful</div>
                      </div>
                      
                      <div className="border rounded-md p-3 flex flex-col items-center justify-center">
                        <div className={`text-3xl font-semibold ${jobStatus.failedCount ? 'text-red-600' : 'text-muted-foreground'}`}>
                          {jobStatus.failedCount || 0}
                        </div>
                        <div className="text-sm text-muted-foreground">Failed</div>
                      </div>
                    </div>
                  )}
                  
                  {jobProgress && (
                    <div className="mt-6">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Overall Progress</span>
                        <span>{jobProgress.progress}%</span>
                      </div>
                      <Progress value={jobProgress.progress} className="h-2" />
                    </div>
                  )}
                  
                  {/* Action buttons */}
                  <div className="mt-6 flex justify-end gap-2">
                    {jobStatus?.status === 'running' && (
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        onClick={handleCancel}
                        disabled={isCancelling}
                      >
                        {isCancelling ? (
                          <>
                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                            Cancelling...
                          </>
                        ) : (
                          <>
                            <StopCircle className="h-4 w-4 mr-2" />
                            Cancel Job
                          </>
                        )}
                      </Button>
                    )}
                    
                    {jobStatus?.status === 'failed' && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={handleRetry}
                        disabled={isRetrying}
                      >
                        {isRetrying ? (
                          <>
                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                            Retrying...
                          </>
                        ) : (
                          <>
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Retry Failed Items
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                  
                  {/* Errors section */}
                  {((jobStatus?.failedCount && jobStatus.failedCount > 0) || jobError) && (
                    <div className="mt-6 border-t pt-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="h-4 w-4 text-destructive" />
                        <h3 className="font-medium">Errors</h3>
                      </div>
                      
                      {jobError && (
                        <div className="mt-2 p-3 bg-destructive/10 rounded-md">
                          <p className="text-sm text-destructive">{jobError.error}</p>
                        </div>
                      )}
                      
                      {jobProgress?.status === 'failed' && jobProgress.error && (
                        <div className="mt-2 p-3 bg-destructive/10 rounded-md">
                          <p className="text-sm text-destructive">{jobProgress.error}</p>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="log">
              <Card>
                <CardContent className="p-4">
                  <h3 className="font-medium mb-2">Processing Log</h3>
                  
                  <ScrollArea className="h-60 border rounded-md p-2">
                    {processingLog.length > 0 ? (
                      <div className="space-y-2">
                        {processingLog.map((entry, index) => (
                          <div key={index} className="text-sm">
                            <span className="text-muted-foreground mr-2">[{entry.timestamp}]</span>
                            <span className={`
                              ${entry.type === 'error' ? 'text-destructive' : 
                                entry.type === 'success' ? 'text-green-600' : ''}
                            `}>
                              {entry.message}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center text-muted-foreground py-4">
                        No log entries yet
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
          
          {jobStatus?.status === 'completed' && (
            <div className="text-center">
              <Button onClick={() => setCurrentStep(currentStep + 1)}>
                <CopyCheck className="h-4 w-4 mr-2" />
                View Results Summary
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="border rounded-lg p-4 text-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-muted-foreground">Preparing job...</p>
        </div>
      )}
    </div>
  );
};
