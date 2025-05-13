import React from "react";
import { Card, CardContent } from "@/components/ui";
import { LibrarySelectionStep } from "./LibrarySelectionStep";
import { ItemSelectionStep } from "./ItemSelectionStep";
import { ProcessingStep } from "./ProcessingStep";
import { SummaryStep } from "./SummaryStep";
import { useRunAphrodite } from "./RunAphroditeContext";

export const StepContent: React.FC = () => {
  const { currentStep, workflowSteps } = useRunAphrodite();
  const currentStepInfo = workflowSteps[currentStep];
  const Icon = currentStepInfo?.icon;

  // Render the appropriate step content based on current step ID
  const renderStepContent = () => {
    switch (currentStepInfo?.id) {
      case "libraries":
        return <LibrarySelectionStep />;
      case "selection":
        return <ItemSelectionStep />;
      case "processing":
        return <ProcessingStep />;
      case "summary":
        return <SummaryStep />;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <Icon className="h-6 w-6 text-primary" />
          <div>
            <h2 className="text-xl font-semibold">{currentStepInfo?.title}</h2>
            <p className="text-sm text-muted-foreground">{currentStepInfo?.description}</p>
          </div>
        </div>
        
        {renderStepContent()}
      </CardContent>
    </Card>
  );
};
