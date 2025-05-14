import React, { useState, useEffect } from "react";
import { Button, Progress, Card, CardContent, Badge, ScrollArea, Tabs, TabsList, TabsTrigger, TabsContent, Alert, AlertTitle, AlertDescription } from "@/components/ui";
import { useRunAphrodite } from "./RunAphroditeContext";
import { XCircle, CheckCircle, RefreshCw, StopCircle, CopyCheck, HelpCircle, AlertCircle, WifiOff } from "lucide-react";
import { useUnifiedJobStatus } from "@/hooks/useUnifiedJobStatus";
import { toast } from "sonner";

export const ProcessingStep: React.FC = () => {
  const { stepData, setCurrentStep, currentStep } = useRunAphrodite();
  
  // Use our new hook for job status monitoring
  const { 
    status, 
    progress, 
    error, 
    loading, 
    completed,
    cancelJob 
  } = useUnifiedJobStatus(stepData.jobId);
  
  const [processingLog, setProcessingLog] = useState<Array<{message: string; timestamp: string; type: 'info' | 'error' | 'success'}>>([]);
  const [isCancelling, setIsCancelling] = useState(false);

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

  // Function to handle job cancellation
  const handleCancel = async () => {
    if (!stepData.jobId) return;
    
    try {
      setIsCancelling(true);
      addLogEntry('Cancelling job...', 'info');
      
      // Cancel job using the hook's cancelJob function
      await cancelJob();
      
      addLogEntry('Job cancelled', 'success');
      toast.success('Job cancellation requested');
    } catch (error) {
      console.error('Failed to cancel job:', error);
      addLogEntry(`Failed to cancel: ${(error as Error).message}`, 'error');
      toast.error('Failed to cancel job');
    } finally {
      setIsCancelling(false);
    }
  };

  // Add to log when status changes
  useEffect(() => {
    if (status) {
      addLogEntry(`Job status: ${status}`, 
        status === 'failed' || status === 'cancelled' ? 'error' : 
        status === 'completed' ? 'success' : 'info');
    }
  }, [status]);

  // Add to log when there's an error
  useEffect(() => {
    if (error) {
      addLogEntry(`Error: ${error}`, 'error');
    }
  }, [error]);

  // Add initial log entry
  useEffect(() => {
    if (stepData.jobId) {
      addLogEntry(`Starting job with ID: ${stepData.jobId}`, 'info');
    }
  }, [stepData.jobId]);

  // Determine job status for display
  const getStatusBadge = () => {
    if (!status) return null;
    
    switch (status) {
      case 'pending':
        return <Badge variant="outline" className="bg-amber-50 text-amber-700">Pending</Badge>;
      case 'processing':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700">Processing</Badge>;
      case 'completed':
        return <Badge variant="outline" className="bg-green-50 text-green-700">Completed</Badge>;
      case 'failed':
        return <Badge variant="outline" className="bg-red-50 text-red-700">Failed</Badge>;
      case 'cancelled':
        return <Badge variant="outline" className="bg-gray-50 text-gray-700">Cancelled</Badge>;
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
                    </div>
                    <div>{getStatusBadge()}</div>
                  </div>
                  
                  {status && (
                    <div className="mt-6">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Overall Progress</span>
                        <span>{progress}%</span>
                      </div>
                      <Progress value={progress} className="h-2" />
                    </div>
                  )}
                  
                  {/* Action buttons */}
                  <div className="mt-6 flex justify-end gap-2">
                    {status === 'processing' && (
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
                  </div>
                  
                  {/* Errors section */}
                  {error && (
                    <div className="mt-6 border-t pt-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="h-4 w-4 text-destructive" />
                        <h3 className="font-medium">Errors</h3>
                      </div>
                      
                      <div className="mt-2 p-3 bg-destructive/10 rounded-md">
                        <p className="text-sm text-destructive">{error}</p>
                      </div>
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
          
          {status === 'completed' && (
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
