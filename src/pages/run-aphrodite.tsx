import React, { useState } from "react";
import { Button, Card, CardContent, Progress } from "@/components/ui";
import { ChevronLeft, ChevronRight, Library, Grid3X3, Zap, CheckCircle } from "lucide-react";
import { LibrarySelector } from "@/components/library-selector";
import { PosterSelector } from "@/components/poster-selector";
import { ErrorBoundary } from "@/components/error-boundary";
import { useCreateJob } from "@/hooks/useCreateJob";
import { useJobWebSocket } from "@/hooks/useJobWebSocket";
import { useUser } from "@/contexts/UserContext";
import apiClient from "@/lib/api-client";

// Workflow steps
const WORKFLOW_STEPS = [
  { 
    id: "libraries", 
    title: "Select Libraries", 
    description: "Choose which libraries to process with Aphrodite",
    icon: Library 
  },
  { 
    id: "selection", 
    title: "Select Items", 
    description: "Choose media items for badge application",
    icon: Grid3X3 
  },
  { 
    id: "processing", 
    title: "Processing", 
    description: "Applying badges to selected items",
    icon: Zap 
  },
  { 
    id: "summary", 
    title: "Summary", 
    description: "Review the results",
    icon: CheckCircle 
  },
];

interface StepData {
  libraries?: string[];
  enabledBadges?: string[];
  selectedItems?: string[];
  jobId?: string;
}

export default function RunAphrodite() {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepData, setStepData] = useState<StepData>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const { user } = useUser();
  const createJob = useCreateJob();
  const { connected, jobStatus, jobProgress, jobError } = useJobWebSocket(stepData.jobId);

  const currentStepInfo = WORKFLOW_STEPS[currentStep];
  const Icon = currentStepInfo.icon;

  const canProceed = () => {
    switch (currentStepInfo.id) {
      case "libraries":
        return stepData.libraries && stepData.libraries.length > 0 && stepData.enabledBadges && stepData.enabledBadges.length > 0;
      case "selection":
        return stepData.selectedItems && stepData.selectedItems.length > 0;
      case "processing":
        return true; // Can always view summary after processing
      case "summary":
        return false; // Last step
      default:
        return false;
    }
  };

  const handleNext = async () => {
    if (currentStep < WORKFLOW_STEPS.length - 1 && canProceed()) {
      // Special handling for moving from selection to processing
      if (currentStepInfo.id === "selection" && stepData.selectedItems) {
        try {
          setIsProcessing(true);
          
          // Create a job with the selected items
          const selectedItems = await fetchSelectedItemsDetails(stepData.selectedItems);
          const jobName = `Badge Application - ${new Date().toISOString().replace(/[:.]/g, '-')}`;
          
          const jobPayload = {
            user_id: parseInt(user?.id || '1'),
            name: jobName,
            items: selectedItems.map(item => ({
              jellyfin_item_id: item.id,
              title: item.name
            }))
          };
          
          console.log('Creating job with payload:', jobPayload);
          
          const job = await createJob.mutateAsync(jobPayload);
          
          // Start processing the job
          await apiClient.jobs.startProcessing(job.id);
          
          // Store job ID and move to processing step
          setStepData(prev => ({ ...prev, jobId: job.id }));
          setCurrentStep(currentStep + 1);
        } catch (error) {
          console.error('Failed to create job:', error);
        } finally {
          setIsProcessing(false);
        }
      } else {
        setCurrentStep(currentStep + 1);
      }
    }
  };

  // Helper function to fetch details of selected items
  const fetchSelectedItemsDetails = async (itemIds: string[]) => {
    // Get the library items data from the previous step
    const libraryIds = stepData.libraries || [];
    
    // For now, we'll use the item IDs directly
    // In a real implementation, you might want to fetch full details
    return itemIds.map(id => ({
      id: id,
      name: `Media Item`  // Safe placeholder name
    }));
  };

  const handleLibrarySelection = (selectedLibraries: string[], enabledBadges: string[]) => {
    setStepData(prev => ({
      ...prev,
      libraries: selectedLibraries,
      enabledBadges: enabledBadges
    }));
    handleNext();
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const progressPercentage = ((currentStep + 1) / WORKFLOW_STEPS.length) * 100;

  // Step content rendering based on current step
  const renderStepContent = () => {
    switch (currentStepInfo.id) {
      case "libraries":
        return (
          <LibrarySelector
            onContinue={handleLibrarySelection}
            preselectedLibraries={stepData.libraries}
          />
        );

      case "selection":
        return (
          <div className="space-y-4">
            <p className="text-muted-foreground">Select the media items you want to apply badges to.</p>
            <div className="text-sm text-muted-foreground mb-4">
              Selected libraries: {stepData.libraries?.length} | Enabled badges: {stepData.enabledBadges?.join(', ')}
            </div>
            <ErrorBoundary>
              <PosterSelector
                libraryIds={stepData.libraries || []}
                onContinue={(selectedItems) => {
                  setStepData(prev => ({ ...prev, selectedItems }));
                  handleNext();
                }}
                preselectedItems={stepData.selectedItems}
              />
            </ErrorBoundary>
          </div>
        );

      case "processing":
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

      case "summary":
        return (
          <div className="space-y-4">
            <p className="text-muted-foreground">Review the results of the badge application process.</p>
            {/* Summary component will go here */}
            <div className="border rounded-lg p-4 text-center text-muted-foreground">
              Summary results will be displayed here
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Run Aphrodite</h1>
      
      {/* Progress indicator */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Step {currentStep + 1} of {WORKFLOW_STEPS.length}</span>
          <span>{progressPercentage}% Complete</span>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Step indicators */}
      <div className="flex justify-between items-center">
        {WORKFLOW_STEPS.map((step, index) => {
          const StepIcon = step.icon;
          const isActive = index === currentStep;
          const isCompleted = index < currentStep;
          
          return (
            <div key={step.id} className="flex-1">
              <div className={`flex flex-col items-center relative ${index < WORKFLOW_STEPS.length - 1 ? "after:content-[''] after:absolute after:top-6 after:left-[60%] after:right-[-40%] after:h-px after:bg-border" : ""}`}>
                <div className={`
                  rounded-full w-12 h-12 flex items-center justify-center mb-2
                  ${isActive ? "bg-primary text-primary-foreground" : ""}
                  ${isCompleted ? "bg-primary/80 text-primary-foreground" : ""}
                  ${!isActive && !isCompleted ? "bg-muted text-muted-foreground" : ""}
                `}>
                  <StepIcon className="h-6 w-6" />
                </div>
                <span className={`text-sm font-medium ${isActive ? "text-primary" : "text-muted-foreground"}`}>
                  {step.title}
                </span>
                <span className="text-xs text-muted-foreground text-center mt-1 max-w-[100px]">
                  {step.description}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Current step content */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Icon className="h-6 w-6 text-primary" />
            <div>
              <h2 className="text-xl font-semibold">{currentStepInfo.title}</h2>
              <p className="text-sm text-muted-foreground">{currentStepInfo.description}</p>
            </div>
          </div>
          
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation buttons */}
      <div className="flex justify-between">
        <Button 
          variant="secondary" 
          onClick={handlePrevious}
          disabled={currentStep === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>
        
        <Button 
          onClick={handleNext}
          disabled={!canProceed() || isProcessing}
        >
          {currentStep === WORKFLOW_STEPS.length - 1 ? "Finish" : "Next"}
          {currentStep < WORKFLOW_STEPS.length - 1 && <ChevronRight className="h-4 w-4 ml-2" />}
        </Button>
      </div>
    </div>
  );
}
