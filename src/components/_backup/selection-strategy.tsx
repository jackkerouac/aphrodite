import React from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, ListChecks } from "lucide-react";

interface SelectionStrategyProps {
  onSelectCurrentPage: () => void;
  onSelectAllInLibrary: () => void;
  onClearSelection: () => void;
  onInvertPage: () => void;
  totalItems?: number;
  currentPageItems: number;
  selectedCount: number;
  isSelectingAll?: boolean;
}

export const SelectionStrategy: React.FC<SelectionStrategyProps> = ({
  onSelectCurrentPage,
  onSelectAllInLibrary,
  onClearSelection,
  onInvertPage,
  totalItems,
  currentPageItems,
  selectedCount,
  isSelectingAll = false,
}) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="secondary" size="sm" disabled={isSelectingAll}>
          <ListChecks className="h-4 w-4 mr-2" />
          Selection Tools
          <ChevronDown className="h-4 w-4 ml-2" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Quick Actions</DropdownMenuLabel>
        <DropdownMenuItem onClick={onSelectCurrentPage}>
          Select All on Current Page ({currentPageItems})
        </DropdownMenuItem>
        {totalItems && totalItems > currentPageItems && (
          <DropdownMenuItem onClick={onSelectAllInLibrary}>
            Select All in Library ({totalItems})
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem 
          onClick={onClearSelection}
          disabled={selectedCount === 0}
        >
          Clear All Selection
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onInvertPage}>
          Invert Selection on Page
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <div className="px-2 py-1.5 text-sm text-muted-foreground">
          {selectedCount} items currently selected
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
