import { UnifiedBadgeSettings } from "@/types/unifiedBadgeSettings";
import { ReactNode } from "react";

// Step definition type
export interface WorkflowStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
}

// Data shared between steps
export interface StepData {
  libraries?: string[];
  enabledBadges?: string[];
  badgeSettings?: UnifiedBadgeSettings[];
  selectedItems?: string[];
  jobId?: string;
}

// Job status interface
export interface JobStatus {
  status: string;
  totalItems?: number;
  processedCount?: number;
  failedCount?: number;
}

// Job progress interface
export interface JobProgress {
  progress: number;
  status: string;
  error?: string;
}

// Job error interface
export interface JobError {
  error: string;
}

// Context provider props
export interface RunAphroditeProviderProps {
  children: ReactNode;
}

// Context value interface
export interface RunAphroditeContextValue {
  currentStep: number;
  stepData: StepData;
  isProcessing: boolean;
  jobStatus?: JobStatus;
  jobProgress?: JobProgress;
  jobError?: JobError;
  connected: boolean;
  isReconnecting: boolean;
  reconnectAttempts: number;
  cancelJob: () => void;
  setCurrentStep: (step: number) => void;
  setStepData: (data: StepData | ((prev: StepData) => StepData)) => void;
  setIsProcessing: (isProcessing: boolean) => void;
  handleNext: (updatedData?: StepData) => Promise<void>;
  handlePrevious: () => void;
  canProceed: (data?: StepData) => boolean;
  availableBadgeSettings: UnifiedBadgeSettings[];
  availableBadgeTypes: string[];
  workflowSteps: WorkflowStep[];
}
