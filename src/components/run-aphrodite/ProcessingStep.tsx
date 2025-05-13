import React from "react";
import { Button, Progress } from "@/components/ui";
import { useRunAphrodite } from "./RunAphroditeContext";

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

  return (
    <div className="space-y-4">
      <p className="text-muted-foreground">Processing selected items and applying badges.</p>
      
      {stepData.jobId ? (
        <div className="space-y-4">
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="font-medium">Job ID: {stepData.jobId}</p>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-muted-foreground">
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            {jobStatus && (
              <div className="space-y-2">
                <p className="text-sm">
                  Status: <span className="font-medium">{jobStatus.status}</span>
                </p>
                {jobStatus.totalItems && (
                  <p className="text-sm">
                    Total items: {jobStatus.totalItems}
                  </p>
                )}
                {jobStatus.processedCount !== undefined && (
                  <p className="text-sm">
                    Processed: {jobStatus.processedCount} / {jobStatus.totalItems || 0}
                  </p>
                )}
                {jobStatus.failedCount !== undefined && jobStatus.failedCount > 0 && (
                  <p className="text-sm text-destructive">
                    Failed: {jobStatus.failedCount}
                  </p>
                )}
              </div>
            )}
            
            {jobProgress && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>Progress</span>
                  <span>{jobProgress.progress}%</span>
                </div>
                <Progress value={jobProgress.progress} className="h-2" />
                
                {jobProgress.status === 'failed' && jobProgress.error && (
                  <p className="text-sm text-destructive mt-2">
                    Last error: {jobProgress.error}
                  </p>
                )}
              </div>
            )}
            
            {jobError && (
              <div className="mt-4 p-3 bg-destructive/10 rounded-md">
                <p className="text-sm text-destructive font-medium">Job Error</p>
                <p className="text-sm text-destructive">{jobError.error}</p>
              </div>
            )}
          </div>
          
          {jobStatus?.status === 'completed' && (
            <div className="text-center">
              <Button onClick={() => setCurrentStep(currentStep + 1)}>
                View Summary
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="border rounded-lg p-4 text-center text-muted-foreground">
          Preparing job...
        </div>
      )}
    </div>
  );
};
