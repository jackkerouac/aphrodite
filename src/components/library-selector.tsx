import React, { useState, useEffect } from "react";
import { Card, CardContent, Checkbox, Button, Skeleton } from "@/components/ui";
import { Library, Check, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import useJellyfinLibraries from "@/hooks/useJellyfinLibraries";

// Function to get an icon based on library type/name (reused from dashboard)
const getLibraryIcon = (name: string) => {
  name = name.toLowerCase();
  
  if (name.includes("movie") || name.includes("film")) return Library;
  if (name.includes("tv") || name.includes("show") || name.includes("series")) return Library;
  if (name.includes("book") || name.includes("audio")) return Library;
  if (name.includes("music")) return Library;
  
  return Library; // Default icon
};

interface LibrarySelectorProps {
  selectedLibraries: string[];
  onLibrariesChange: (libraries: string[]) => void;
  onValidationChange?: (isValid: boolean) => void;
}

export const LibrarySelector: React.FC<LibrarySelectorProps> = ({
  selectedLibraries,
  onLibrariesChange,
  onValidationChange
}) => {
  const { libraries, isLoading, error } = useJellyfinLibraries();
  const [selectAll, setSelectAll] = useState(false);

  // Update validation status when selection changes
  useEffect(() => {
    const isValid = selectedLibraries.length > 0;
    onValidationChange?.(isValid);
  }, [selectedLibraries, onValidationChange]);

  // Update select all checkbox state
  useEffect(() => {
    if (libraries.length > 0) {
      setSelectAll(selectedLibraries.length === libraries.length);
    }
  }, [selectedLibraries, libraries]);

  const handleLibraryToggle = (libraryId: string) => {
    if (selectedLibraries.includes(libraryId)) {
      onLibrariesChange(selectedLibraries.filter(id => id !== libraryId));
    } else {
      onLibrariesChange([...selectedLibraries, libraryId]);
    }
  };

  const handleSelectAll = () => {
    if (selectAll) {
      onLibrariesChange([]);
    } else {
      onLibrariesChange(libraries.map(lib => lib.id));
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <Skeleton className="h-5 w-5 rounded" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-3/4 mb-2" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load libraries: {error}. Please check your Jellyfin connection in settings.
        </AlertDescription>
      </Alert>
    );
  }

  if (libraries.length === 0) {
    return (
      <Alert>
        <AlertDescription>
          No libraries found. Please configure your Jellyfin connection in settings.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          {selectedLibraries.length} of {libraries.length} libraries selected
        </p>
        <Button
          variant="secondary"
          size="sm"
          onClick={handleSelectAll}
        >
          {selectAll ? "Deselect All" : "Select All"}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {libraries.map((library) => {
          const Icon = getLibraryIcon(library.name);
          const isSelected = selectedLibraries.includes(library.id);

          return (
            <Card 
              key={library.id} 
              className={`cursor-pointer transition-all duration-200 ${
                isSelected ? "border-primary ring-2 ring-primary/20" : "hover:border-gray-300"
              }`}
              onClick={() => handleLibraryToggle(library.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={() => handleLibraryToggle(library.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <Icon className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <h4 className="text-sm font-medium">{library.name}</h4>
                    <p className="text-xs text-muted-foreground">
                      {library.itemCount} items
                    </p>
                  </div>
                  {isSelected && (
                    <Check className="h-4 w-4 text-primary" />
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {selectedLibraries.length === 0 && (
        <Alert>
          <AlertDescription>
            Please select at least one library to continue.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};
