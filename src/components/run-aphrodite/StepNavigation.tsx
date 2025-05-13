import React from "react";
import { Button } from "@/components/ui";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRunAphrodite } from "./RunAphroditeContext";

export const StepNavigation: React.FC = () => {
  const { 
    currentStep, 
    workflowSteps, 
    canProceed, 
    handleNext, 
    handlePrevious, 
    isProcessing 
  } = useRunAphrodite();

  return (
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
        onClick={() => handleNext()}
        disabled={!canProceed() || isProcessing}
      >
        {isProcessing ? (
          <>
            <span className="mr-2">Processing...</span>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
          </>
        ) : (
          <>
            {currentStep === workflowSteps.length - 1 ? "Finish" : "Next"}
            {currentStep < workflowSteps.length - 1 && <ChevronRight className="h-4 w-4 ml-2" />}
          </>
        )}
      </Button>
    </div>
  );
};
