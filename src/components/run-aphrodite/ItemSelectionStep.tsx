import React from "react";
import { PosterSelector } from "@/components/poster-selector";
import { ErrorBoundary } from "@/components/error-boundary";
import { useRunAphrodite } from "./RunAphroditeContext";

export const ItemSelectionStep: React.FC = () => {
  const { stepData, setStepData, handleNext } = useRunAphrodite();

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
};
