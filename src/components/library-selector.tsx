import React, { useState, useEffect } from "react";
import { 
  Card, 
  CardContent, 
  CardHeader,
  CardTitle,
  CardDescription 
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Database, 
  Film, 
  Tv, 
  Book, 
  Music,
  AlertCircle
} from "lucide-react";
import useJellyfinLibraries from "@/hooks/useJellyfinLibraries";

// Props interface for the component
interface LibrarySelectorProps {
  onContinue: (selectedLibraries: string[], enabledBadges: string[]) => void;
  preselectedLibraries?: string[];
}

// Function to get an icon based on library type/name (reused from dashboard)
const getLibraryIcon = (name: string) => {
  name = name.toLowerCase();
  
  if (name.includes("movie") || name.includes("film")) return Film;
  if (name.includes("tv") || name.includes("show") || name.includes("series")) return Tv;
  if (name.includes("book") || name.includes("audio")) return Book;
  if (name.includes("music")) return Music;
  
  return Database; // Default icon
};

export const LibrarySelector: React.FC<LibrarySelectorProps> = ({
  onContinue,
  preselectedLibraries = []
}) => {
  const { libraries, isLoading, error } = useJellyfinLibraries();
  const [selectedLibraries, setSelectedLibraries] = useState<string[]>(preselectedLibraries);

  // Initialize preselected libraries when they change
  useEffect(() => {
    if (preselectedLibraries.length > 0) {
      setSelectedLibraries(preselectedLibraries);
    }
  }, [preselectedLibraries]);

  const handleLibraryToggle = (libraryId: string) => {
    setSelectedLibraries(prev => 
      prev.includes(libraryId)
        ? prev.filter(id => id !== libraryId)
        : [...prev, libraryId]
    );
  };

  const handleSelectAll = () => {
    setSelectedLibraries(libraries.map(lib => lib.id));
  };

  const handleClearSelection = () => {
    setSelectedLibraries([]);
  };

  const handleContinue = () => {
    if (selectedLibraries.length > 0) {
      // TODO: Fetch enabled badges from database
      // For now, pass empty array. Will be implemented in next step
      onContinue(selectedLibraries, []);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-2">Select Libraries</h2>
          <p className="text-muted-foreground">
            Choose which libraries to process with Aphrodite
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <Skeleton className="h-5 w-5 rounded mt-1" />
                  <div className="flex-1">
                    <Skeleton className="h-6 w-3/4 mb-2" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-2">Select Libraries</h2>
          <p className="text-muted-foreground">
            Choose which libraries to process with Aphrodite
          </p>
        </div>
        
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
            <br />
            Please check your Jellyfin connection in settings.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Empty state
  if (libraries.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-2">Select Libraries</h2>
          <p className="text-muted-foreground">
            Choose which libraries to process with Aphrodite
          </p>
        </div>
        
        <Alert>
          <AlertDescription>
            No libraries found. Please configure your Jellyfin connection in settings.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight mb-2">Select Libraries</h2>
        <p className="text-muted-foreground">
          Choose which libraries to process with Aphrodite
        </p>
      </div>

      {/* Selection controls */}
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">
          {selectedLibraries.length} of {libraries.length} libraries selected
        </p>
        <div className="space-x-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleSelectAll}
          >
            Select All
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleClearSelection}
          >
            Clear Selection
          </Button>
        </div>
      </div>

      {/* Library grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {libraries.map((library) => {
          const Icon = getLibraryIcon(library.name);
          const isSelected = selectedLibraries.includes(library.id);

          return (
            <Card 
              key={library.id} 
              className={`cursor-pointer transition-all duration-200 ${
                isSelected ? "border-primary ring-1 ring-primary" : "hover:border-gray-300"
              }`}
              onClick={() => handleLibraryToggle(library.id)}
            >
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={() => handleLibraryToggle(library.id)}
                    onClick={(e) => e.stopPropagation()}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <Icon className="h-5 w-5 mr-2 text-muted-foreground" />
                      <h4 className="font-medium">{library.name}</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {library.itemCount.toLocaleString()} items
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Validation message */}
      {selectedLibraries.length === 0 && (
        <Alert>
          <AlertDescription>
            Please select at least one library to continue.
          </AlertDescription>
        </Alert>
      )}

      {/* Continue button */}
      <div className="flex justify-end">
        <Button
          onClick={handleContinue}
          disabled={selectedLibraries.length === 0}
        >
          Continue
        </Button>
      </div>
    </div>
  );
};
