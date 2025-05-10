import React, { useState } from "react";
import { Button, Card, CardContent, Progress } from "@/components/ui";
import { ChevronLeft, ChevronRight, Library, Grid3X3, Zap, CheckCircle } from "lucide-react";
import { LibrarySelector } from "@/components/library-selector";
import { PosterSelector } from "@/components/poster-selector";
import { ErrorBoundary } from "@/components/error-boundary";

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

  const handleNext = () => {
    if (currentStep < WORKFLOW_STEPS.length - 1 && canProceed()) {
      setCurrentStep(currentStep + 1);
    }
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
            {/* JobStatus component will go here */}
            <div className="border rounded-lg p-4 text-center text-muted-foreground">
              JobStatus component will be implemented here
            </div>
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
