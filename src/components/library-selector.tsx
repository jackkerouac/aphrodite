import React, { useState, useEffect, useRef } from "react";
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
import { Switch } from "@/components/ui/switch";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Database, 
  Film, 
  Tv, 
  Book, 
  Music,
  AlertCircle,
  CheckCircle2,
  Volume2, 
  Monitor, 
  Star 
} from "lucide-react";
import useJellyfinLibraries from "@/hooks/useJellyfinLibraries";
import useEnabledBadges from "@/hooks/useEnabledBadges";
import { useUnifiedBadgeSettings } from "@/hooks/useUnifiedBadgeSettings";

// Props interface for the component
interface LibrarySelectorProps {
  onContinue: (selectedLibraries: string[], enabledBadges: string[]) => void;
  preselectedLibraries?: string[];
  availableBadges?: string[];
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
  preselectedLibraries = [],
  availableBadges = []
}) => {
  const { libraries, isLoading, error } = useJellyfinLibraries();
  const { enabledBadges, isLoading: badgesLoading, error: badgesError } = useEnabledBadges();
  // Get unified badge settings to check if they're loaded
  const { isLoading: badgeSettingsLoading } = useUnifiedBadgeSettings({ autoSave: false });
  const [selectedLibraries, setSelectedLibraries] = useState<string[]>(preselectedLibraries);
  const [selectedBadges, setSelectedBadges] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<string>("libraries");
  
  // Use a ref to track initialization
  const initializedRef = useRef(false);

  // Initialize selected libraries once
  useEffect(() => {
    if (preselectedLibraries.length > 0) {
      setSelectedLibraries(preselectedLibraries);
    }
  }, [preselectedLibraries]);

  // One-time initialization for badges
  useEffect(() => {
    // Skip if already initialized or if data is still loading
    if (initializedRef.current || badgesLoading || badgeSettingsLoading) {
      return;
    }
    
    // Skip if no badges available or if we already have selected badges
    if (availableBadges.length === 0 || selectedBadges.length > 0) {
      initializedRef.current = true;
      return;
    }
    
    // Initialize with enabled badges
    const initialBadges: string[] = [];
    
    // Try to add enabled badges first
    if (enabledBadges?.review && availableBadges.includes('review')) {
      initialBadges.push('review');
    }
    if (enabledBadges?.resolution && availableBadges.includes('resolution')) {
      initialBadges.push('resolution');
    }
    if (enabledBadges?.audio && availableBadges.includes('audio')) {
      initialBadges.push('audio');
    }
    
    // If no enabled badges, add the first available as fallback
    if (initialBadges.length === 0 && availableBadges.length > 0) {
      initialBadges.push(availableBadges[0]);
    }
    
    // Set selected badges if we have any
    if (initialBadges.length > 0) {
      setSelectedBadges(initialBadges);
    }
    
    // Mark as initialized to prevent infinite loops
    initializedRef.current = true;
  }, [enabledBadges, availableBadges, selectedBadges, badgesLoading, badgeSettingsLoading]);

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

  const handleBadgeToggle = (badgeType: string) => {
    setSelectedBadges(prev => 
      prev.includes(badgeType)
        ? prev.filter(type => type !== badgeType)
        : [...prev, badgeType]
    );
  };

  const handleContinue = () => {
    if (selectedLibraries.length > 0 && selectedBadges.length > 0) {
      onContinue(selectedLibraries, selectedBadges);
    }
  };

  // Loading state
  if (isLoading || badgesLoading || badgeSettingsLoading) {
    return (
      <div className="space-y-6">
        
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
        
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
            <br />
            Please check your Jellyfin connection in settings.
          </AlertDescription>
        </Alert>

        {badgesError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Failed to load badge settings: {badgesError}
            </AlertDescription>
          </Alert>
        )}
      </div>
    );
  }

  // Empty state
  if (libraries.length === 0) {
    return (
      <div className="space-y-6">
        
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
      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="libraries">Libraries</TabsTrigger>
          <TabsTrigger value="badges">Badge Types</TabsTrigger>
        </TabsList>

        <TabsContent value="libraries" className="pt-4">
          {/* Selection controls */}
          <div className="flex justify-between items-center mb-4">
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
        </TabsContent>
        
        <TabsContent value="badges" className="pt-4">

          {/* Badge Selection */}
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg">
              {!badgesLoading && !badgesError ? (
                <div className="space-y-4">
                  {availableBadges.length > 0 ? (
                    <div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {availableBadges.includes('audio') && (
                          <Card 
                            className={`cursor-pointer transition-all duration-200 ${
                              selectedBadges.includes('audio') ? "border-primary ring-1 ring-primary" : "hover:border-gray-300"
                            }`}
                            onClick={() => handleBadgeToggle('audio')}
                          >
                            <CardContent className="p-4">
                              <div className="flex flex-col items-center justify-center h-full py-4">
                                <Volume2 
                                  className={`h-10 w-10 mb-2 ${
                                    selectedBadges.includes('audio') ? 'text-primary' : 'text-muted-foreground'
                                  }`} 
                                />
                                <h3 className="font-medium text-center">Audio Badge</h3>
                                <p className="text-xs text-center text-muted-foreground mt-1">
                                  Dolby Atmos, DTS, etc.
                                </p>
                                <div className="mt-4">
                                  <Switch 
                                    checked={selectedBadges.includes('audio')} 
                                    onCheckedChange={() => handleBadgeToggle('audio')}
                                    disabled={!enabledBadges.audio}
                                  />
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                        
                        {availableBadges.includes('resolution') && (
                          <Card 
                            className={`cursor-pointer transition-all duration-200 ${
                              selectedBadges.includes('resolution') ? "border-primary ring-1 ring-primary" : "hover:border-gray-300"
                            }`}
                            onClick={() => handleBadgeToggle('resolution')}
                          >
                            <CardContent className="p-4">
                              <div className="flex flex-col items-center justify-center h-full py-4">
                                <Monitor 
                                  className={`h-10 w-10 mb-2 ${
                                    selectedBadges.includes('resolution') ? 'text-primary' : 'text-muted-foreground'
                                  }`} 
                                />
                                <h3 className="font-medium text-center">Resolution Badge</h3>
                                <p className="text-xs text-center text-muted-foreground mt-1">
                                  4K, HDR, 1080p, etc.
                                </p>
                                <div className="mt-4">
                                  <Switch 
                                    checked={selectedBadges.includes('resolution')} 
                                    onCheckedChange={() => handleBadgeToggle('resolution')}
                                    disabled={!enabledBadges.resolution}
                                  />
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                        
                        {availableBadges.includes('review') && (
                          <Card 
                            className={`cursor-pointer transition-all duration-200 ${
                              selectedBadges.includes('review') ? "border-primary ring-1 ring-primary" : "hover:border-gray-300"
                            }`}
                            onClick={() => handleBadgeToggle('review')}
                          >
                            <CardContent className="p-4">
                              <div className="flex flex-col items-center justify-center h-full py-4">
                                <Star 
                                  className={`h-10 w-10 mb-2 ${
                                    selectedBadges.includes('review') ? 'text-primary' : 'text-muted-foreground'
                                  }`} 
                                />
                                <h3 className="font-medium text-center">Review Badge</h3>
                                <p className="text-xs text-center text-muted-foreground mt-1">
                                  IMDb, Rotten Tomatoes, etc.
                                </p>
                                <div className="mt-4">
                                  <Switch 
                                    checked={selectedBadges.includes('review')} 
                                    onCheckedChange={() => handleBadgeToggle('review')}
                                    disabled={!enabledBadges.review}
                                  />
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )}
                      </div>
                      
                      {/* Badge count indicator */}
                      <div className="mt-6 text-center">
                        <p className="font-medium">
                          {selectedBadges.length} of {availableBadges.length} badge types selected
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No badge types are available.</p>
                  )}
                  
                  {/* Disabled badges warning */}
                  {(availableBadges.includes('audio') && !enabledBadges.audio) || 
                   (availableBadges.includes('resolution') && !enabledBadges.resolution) || 
                   (availableBadges.includes('review') && !enabledBadges.review) ? (
                    <Alert className="mt-3">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        Some badge types are disabled in your settings. 
                        Only enabled badges can be selected for processing.
                      </AlertDescription>
                    </Alert>
                  ) : null}
                </div>
              ) : badgesError ? (
                <p className="text-destructive">Failed to load badge settings.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Skeleton className="h-36 w-full" />
                  <Skeleton className="h-36 w-full" />
                  <Skeleton className="h-36 w-full" />
                </div>
              )}
            </div>
            
            <p className="text-sm text-muted-foreground">
              These badges will be applied to the selected libraries.
            </p>
            <p className="text-sm text-muted-foreground">
              Note: Some badges may not apply to certain media types (e.g., resolution badges won't apply to TV series, only to individual episodes).
            </p>
          </div>
        </TabsContent>
      </Tabs>

      {/* Selection summary */}
      <div className="p-4 bg-muted rounded-lg mt-6">
        <h3 className="text-lg font-semibold mb-2">Selection Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium mb-1">Selected Libraries ({selectedLibraries.length})</h4>
            {selectedLibraries.length > 0 ? (
              <div className="flex flex-wrap gap-1">
                {selectedLibraries.map(libId => {
                  const library = libraries.find(lib => lib.id === libId);
                  return (
                    <div key={libId} className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-secondary text-secondary-foreground">
                      {library?.name || libId}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No libraries selected</p>
            )}
          </div>
          <div>
            <h4 className="text-sm font-medium mb-1">Selected Badge Types ({selectedBadges.length})</h4>
            {selectedBadges.length > 0 ? (
              <div className="flex flex-wrap gap-1">
                {selectedBadges.map(badgeType => (
                  <div key={badgeType} className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-primary/20 text-primary">
                    {badgeType.charAt(0).toUpperCase() + badgeType.slice(1)}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No badge types selected</p>
            )}
          </div>
        </div>
      </div>

      {/* Validation messages */}
      {selectedLibraries.length === 0 && (
        <Alert>
          <AlertDescription>
            Please select at least one library to continue.
          </AlertDescription>
        </Alert>
      )}
      
      {selectedLibraries.length > 0 && selectedBadges.length === 0 && (
        <Alert>
          <AlertDescription>
            Please select at least one badge type to continue.
          </AlertDescription>
        </Alert>
      )}

      {/* Continue button */}
      <div className="flex justify-end">
        <Button
          onClick={handleContinue}
          disabled={selectedLibraries.length === 0 || selectedBadges.length === 0}
        >
          Continue
        </Button>
      </div>
    </div>
  );
};
