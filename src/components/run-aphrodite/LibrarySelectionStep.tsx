import React from "react";
import { LibrarySelector } from "@/components/library-selector";
import { useRunAphrodite } from "./RunAphroditeContext";

export const LibrarySelectionStep: React.FC = () => {
  const { stepData, setStepData, handleNext, availableBadgeTypes, availableBadgeSettings } = useRunAphrodite();

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

  return (
    <LibrarySelector
      onContinue={handleLibrarySelection}
      preselectedLibraries={stepData.libraries}
      availableBadges={availableBadgeTypes}
    />
  );
};
