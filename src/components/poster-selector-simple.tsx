import React, { useState } from "react";
import { Button } from "@/components/ui";

interface PosterSelectorSimpleProps {
  libraryIds: string[];
  onContinue: (selectedItems: string[]) => void;
  preselectedItems?: string[];
}

export const PosterSelectorSimple: React.FC<PosterSelectorSimpleProps> = ({
  libraryIds,
  onContinue,
  preselectedItems = []
}) => {
  const [selectedItems, setSelectedItems] = useState<string[]>(preselectedItems);

  const handleContinue = () => {
    onContinue(selectedItems);
  };

  return (
    <div className="space-y-4">
      <div className="p-4 border rounded">
        <h3 className="font-medium mb-2">Simple Poster Selector</h3>
        <p>Libraries: {libraryIds.join(', ')}</p>
        <p>Selected items: {selectedItems.length}</p>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleContinue}>
          Continue (Simple)
        </Button>
      </div>
    </div>
  );
};
