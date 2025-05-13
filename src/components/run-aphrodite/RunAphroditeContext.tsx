import React, { createContext, useState, useContext, useMemo } from "react";
import { useUser } from "@/contexts/UserContext";
import { useCreateJob } from "@/hooks/useCreateJob";
import { useJobWebSocket } from "@/hooks/useJobWebSocket";
import { useUnifiedBadgeSettings } from "@/hooks/useUnifiedBadgeSettings";
import apiClient from "@/lib/api-client";
import { toast } from "sonner";
import { ChevronLeft, ChevronRight, Library, Grid3X3, Zap, CheckCircle } from "lucide-react";
import { 
  StepData, 
  WorkflowStep, 
  RunAphroditeContextValue, 
  RunAphroditeProviderProps,
  UnifiedBadgeSettings
} from "./shared/types";
import { fetchSelectedItemsDetails, prepareBadgeSettingsForJob } from "./shared/helpers";

// Workflow steps definition
export const WORKFLOW_STEPS: WorkflowStep[] = [
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

// Create context with default value
const RunAphroditeContext = createContext<RunAphroditeContextValue | undefined>(undefined);

// Provider component
export const RunAphroditeProvider: React.FC<RunAphroditeProviderProps> = ({ children }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepData, setStepData] = useState<StepData>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const { user } = useUser();
  const createJob = useCreateJob();
  const { 
    connected, 
    jobStatus, 
    jobProgress, 
    jobError,
    isReconnecting,
    reconnectAttempts,
    cancelJob 
  } = useJobWebSocket(stepData.jobId);

  // Get unified badge settings from the hook
  const {
    audioBadge,
    resolutionBadge,
    reviewBadge,
  } = useUnifiedBadgeSettings({ autoSave: false });

  // Prepare unified badge settings for processing
  const availableBadgeSettings = useMemo(() => {
    return [audioBadge, resolutionBadge, reviewBadge].filter(Boolean) as UnifiedBadgeSettings[];
  }, [audioBadge, resolutionBadge, reviewBadge]);

  // Get available badge types from the unified badge settings
  const availableBadgeTypes = useMemo(() => {
    return availableBadgeSettings.map(badge => badge.badge_type);
  }, [availableBadgeSettings]);

  const currentStepInfo = WORKFLOW_STEPS[currentStep];

  const canProceed = (data?: StepData) => {
    const checkData = data || stepData;
    switch (currentStepInfo?.id) {
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
          
          // Get badge settings for job creation
          let badgeSettingsToUse = dataToCheck.badgeSettings;
          
          // If no settings in step data, use the available badge settings
          if (!badgeSettingsToUse || badgeSettingsToUse.length === 0) {
            badgeSettingsToUse = availableBadgeSettings;
            console.log('Using available badge settings:', badgeSettingsToUse.map(b => b.badge_type));
          }
          
          // Process badge settings for the job using our helper function
          // Filter based on enabled badges selected by the user
          const processedBadgeSettings = prepareBadgeSettingsForJob(
            badgeSettingsToUse, 
            dataToCheck.enabledBadges
          );
          
          // Check if we have any badge settings to apply
          if (!processedBadgeSettings || processedBadgeSettings.length === 0) {
            throw new Error('No badge settings available for job creation. Please select at least one badge type.');
          }
          
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
          
          console.log('Creating job with payload:', {
            user_id: jobPayload.user_id,
            name: jobPayload.name,
            items_count: jobPayload.items.length,
            badge_settings_count: jobPayload.badgeSettings.length,
            badge_types: jobPayload.badgeSettings.map(b => b.badge_type)
          });
          
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

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Context value
  const contextValue: RunAphroditeContextValue = {
    currentStep,
    stepData,
    isProcessing,
    jobStatus,
    jobProgress,
    jobError,
    connected,
    isReconnecting,
    reconnectAttempts,
    cancelJob,
    setCurrentStep,
    setStepData,
    setIsProcessing,
    handleNext,
    handlePrevious,
    canProceed,
    availableBadgeSettings,
    availableBadgeTypes,
    workflowSteps: WORKFLOW_STEPS,
  };

  return (
    <RunAphroditeContext.Provider value={contextValue}>
      {children}
    </RunAphroditeContext.Provider>
  );
};

// Custom hook to use the context
export const useRunAphrodite = (): RunAphroditeContextValue => {
  const context = useContext(RunAphroditeContext);
  if (context === undefined) {
    throw new Error("useRunAphrodite must be used within a RunAphroditeProvider");
  }
  return context;
};
