import React, { useState, useEffect, useMemo } from "react";
import { Button, Card, CardContent, Progress } from "@/components/ui";
import { ChevronLeft, ChevronRight, Library, Grid3X3, Zap, CheckCircle } from "lucide-react";
import { LibrarySelector } from "@/components/library-selector";
import { PosterSelector } from "@/components/poster-selector";
import { ErrorBoundary } from "@/components/error-boundary";
import { useCreateJob } from "@/hooks/useCreateJob";
import { useJobWebSocket } from "@/hooks/useJobWebSocket";
import { useUser } from "@/contexts/UserContext";
import apiClient from "@/lib/api-client";
import { toast } from "sonner";

// Import unified badge hooks and types only - not the preview component
import { useUnifiedBadgeSettings } from "@/hooks/useUnifiedBadgeSettings";
import { UnifiedBadgeSettings } from "@/types/unifiedBadgeSettings";

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

// Enhanced StepData interface to include unified badge settings
interface StepData {
  libraries?: string[];
  enabledBadges?: string[];
  badgeSettings?: UnifiedBadgeSettings[];
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

  // Get unified badge settings from the hook
  const {
    audioBadge,
    resolutionBadge,
    reviewBadge,
    isLoading: isLoadingBadges,
  } = useUnifiedBadgeSettings({ autoSave: false });

  // Prepare unified badge settings for processing
  const availableBadgeSettings = [
    audioBadge,
    resolutionBadge,
    reviewBadge,
  ].filter(Boolean) as UnifiedBadgeSettings[];

  // Convert unified badge settings to the format required for batch processing
  const prepareBadgeSettingsForJob = (badgeSettings: UnifiedBadgeSettings[] = []): any[] => {
    if (!badgeSettings || badgeSettings.length === 0) {
      console.warn('No badge settings provided for job creation');
      return [];
    }

    // Map each badge setting to the format expected by the API
    return badgeSettings.map(setting => {
      // Create a clean copy to avoid reference issues
      const settingCopy = JSON.parse(JSON.stringify(setting));
      
      // Ensure required fields are present
      if (!settingCopy.badge_type) {
        console.error('Badge setting missing badge_type:', settingCopy);
        return null;
      }
      
      // Format badge settings as expected by the API
      return {
        badge_type: settingCopy.badge_type,
        badge_size: settingCopy.badge_size || 100,
        badge_position: settingCopy.badge_position,
        background_color: settingCopy.background_color,
        background_opacity: settingCopy.background_opacity,
        border_size: settingCopy.border_size,
        border_color: settingCopy.border_color,
        border_opacity: settingCopy.border_opacity,
        border_radius: settingCopy.border_radius,
        border_width: settingCopy.border_width,
        shadow_enabled: settingCopy.shadow_enabled,
        shadow_color: settingCopy.shadow_color,
        shadow_blur: settingCopy.shadow_blur,
        shadow_offset_x: settingCopy.shadow_offset_x,
        shadow_offset_y: settingCopy.shadow_offset_y,
        properties: settingCopy.properties,
        // Include display_format only for review badges
        ...(settingCopy.badge_type === 'review' ? { display_format: settingCopy.display_format } : {})
      };
    }).filter(Boolean); // Remove any null entries
  };

  const currentStepInfo = WORKFLOW_STEPS[currentStep];
  const Icon = currentStepInfo.icon;

  const canProceed = (data?: StepData) => {
    const checkData = data || stepData;
    switch (currentStepInfo.id) {
      case "libraries":
        return checkData.libraries && checkData.libraries.length > 0 && 
               checkData.enabledBadges && checkData.enabledBadges.length > 0;
      case "selection":
        return checkData.selectedItems && checkData.selectedItems.length > 0;
      case "processing":
        return true; // Can always view summary after processing
      case "summary":
        return false; // Last step
      default:
        return false;
    }
  };

  const handleNext = async (updatedData?: StepData) => {
    const dataToCheck = updatedData || stepData;
    if (currentStep < WORKFLOW_STEPS.length - 1 && canProceed(dataToCheck)) {
      // Special handling for moving from selection to processing
      if (currentStepInfo.id === "selection" && dataToCheck.selectedItems) {
        try {
          setIsProcessing(true);
          
          // Create a job with the selected items
          const selectedItems = await fetchSelectedItemsDetails(dataToCheck.selectedItems);
          const jobName = `Badge Application - ${new Date().toISOString().replace(/[:.]/g, '-')}`;
          
          // Process badge settings for the job using our new helper function
          const processedBadgeSettings = prepareBadgeSettingsForJob(dataToCheck.badgeSettings);
          
          // Enhanced job payload with unified badge settings
          const jobPayload = {
            user_id: parseInt(user?.id || '1'),
            name: jobName,
            items: selectedItems.map(item => ({
              jellyfin_item_id: item.id,
              title: item.name
            })),
            badgeSettings: processedBadgeSettings
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
          toast.error('Failed to create job. Please try again.');
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

  // Get available badge types from the unified badge settings
  const availableBadgeTypes = useMemo(() => {
    return availableBadgeSettings.map(badge => badge.badge_type);
  }, [availableBadgeSettings]);

  const handleLibrarySelection = (selectedLibraries: string[], selectedBadgeTypes: string[]) => {
    // Filter badge settings based on selected badge types
    const selectedBadgeSettings = availableBadgeSettings.filter(badge => 
      selectedBadgeTypes.includes(badge.badge_type)
    );

    console.log('Selected badge types:', selectedBadgeTypes);
    console.log('Selected badge settings:', selectedBadgeSettings);
    
    const updatedData = {
      ...stepData,
      libraries: selectedLibraries,
      enabledBadges: selectedBadgeTypes,
      badgeSettings: selectedBadgeSettings
    };
    
    setStepData(updatedData);
    
    // Move to next step after updating state
    handleNext(updatedData);
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
            availableBadges={availableBadgeTypes}
          />
        );

      case "selection":
        return (
          <div className="space-y-4">
            <p className="text-muted-foreground">Select the media items you want to apply badges to.</p>
            <div className="text-sm text-muted-foreground mb-4">
              Selected libraries: {stepData.libraries?.length} | 
              Enabled badges: {stepData.enabledBadges?.join(', ')}
            </div>
            
            <ErrorBoundary>
              <PosterSelector
                libraryIds={stepData.libraries || []}
                onContinue={(selectedItems) => {
                  const updatedData = {
                    ...stepData,
                    selectedItems
                  };
                  setStepData(updatedData);
                  // Move to next step after updating state
                  handleNext(updatedData);
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
            <div className="border rounded-lg p-4">
              <h3 className="font-medium mb-2">Job Summary</h3>
              
              {jobStatus && (
                <div className="space-y-2">
                  <p className="text-sm">
                    Status: <span className="font-medium">{jobStatus.status}</span>
                  </p>
                  <p className="text-sm">
                    Total items: {jobStatus.totalItems || 0}
                  </p>
                  <p className="text-sm">
                    Successfully processed: {(jobStatus.totalItems || 0) - (jobStatus.failedCount || 0)}
                  </p>
                  {jobStatus.failedCount !== undefined && jobStatus.failedCount > 0 && (
                    <p className="text-sm text-destructive">
                      Failed items: {jobStatus.failedCount}
                    </p>
                  )}
                </div>
              )}
              
              <div className="mt-4">
                <h4 className="text-sm font-medium mb-2">Applied badges:</h4>
                <div className="flex flex-wrap gap-2">
                  {stepData.enabledBadges?.map(badgeType => (
                    <div key={badgeType} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/20 text-primary">
                      {badgeType.charAt(0).toUpperCase() + badgeType.slice(1)} Badge
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // Show loading state when badges are loading
  if (isLoadingBadges) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading badge settings...</p>
        </div>
      </div>
    );
  }

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
          {isProcessing ? (
            <>
              <span className="mr-2">Processing...</span>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
            </>
          ) : (
            <>
              {currentStep === WORKFLOW_STEPS.length - 1 ? "Finish" : "Next"}
              {currentStep < WORKFLOW_STEPS.length - 1 && <ChevronRight className="h-4 w-4 ml-2" />}
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
