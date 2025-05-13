import React from "react";
import { useUnifiedBadgeSettings } from "@/hooks/useUnifiedBadgeSettings";
import { 
  RunAphroditeProvider, 
  WorkflowSteps, 
  StepContent, 
  StepNavigation 
} from "@/components/run-aphrodite";

export default function RunAphrodite() {
  const { isLoading: isLoadingBadges } = useUnifiedBadgeSettings({ autoSave: false });

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
    <RunAphroditeProvider>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Run Aphrodite</h1>
        
        {/* Progress and step indicators */}
        <WorkflowSteps />

        {/* Current step content */}
        <StepContent />

        {/* Navigation buttons */}
        <StepNavigation />
      </div>
    </RunAphroditeProvider>
  );
}
