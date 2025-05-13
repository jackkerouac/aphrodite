import React, { useState, useEffect } from "react";
import { PosterGrid } from "./poster-grid";
import { useLibraryItems } from "@/hooks/useLibraryItems";
import { 
  Button, 
  Card, 
  CardContent,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Badge,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui";
import { 
  ChevronLeft, 
  ChevronRight, 
  Filter, 
  Wand, 
  Check, 
  Film, 
  Tv, 
  MonitorSmartphone, 
  AlertTriangle,
  RefreshCw
} from "lucide-react";
import { useUser } from "@/contexts/UserContext";
import { fetchApi } from "@/lib/api-client";

interface PosterSelectorProps {
  libraryIds: string[];
  onContinue: (selectedItems: string[]) => void;
  preselectedItems?: string[];
}

// Media type options
const mediaTypeOptions = [
  { value: "all", label: "All Types" },
  { value: "Movie", label: "Movies" },
  { value: "Series", label: "TV Series" },
  { value: "Season", label: "Seasons" },
  { value: "Episode", label: "Episodes" }
];

// Filter presets
const filterPresets = [
  { 
    id: "4k-content", 
    name: "All 4K Content", 
    description: "All media items with 4K resolution",
    filter: { resolution: "4k" } 
  },
  { 
    id: "dolby-atmos", 
    name: "All Dolby Atmos", 
    description: "All media items with Dolby Atmos audio",
    filter: { audio: "dolby-atmos" } 
  },
  { 
    id: "unrated", 
    name: "Unrated Content", 
    description: "Content without ratings",
    filter: { review: "none" } 
  },
  { 
    id: "recent-4k", 
    name: "Recent 4K Content", 
    description: "Recently added 4K content",
    filter: { resolution: "4k", recent: true } 
  }
];

export const PosterSelector: React.FC<PosterSelectorProps> = ({
  libraryIds,
  onContinue,
  preselectedItems = []
}) => {
  const { user, isLoading: userLoading } = useUser();
  const [selectedItems, setSelectedItems] = useState<string[]>(preselectedItems);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [isValid, setIsValid] = useState(false);
  
  // New state for advanced filtering
  const [mediaType, setMediaType] = useState<string>("all");
  const [activeFilters, setActiveFilters] = useState<string[]>([]);
  const [filterView, setFilterView] = useState<"basic" | "advanced">("basic");
  const [filterQuery, setFilterQuery] = useState<Record<string, any>>({});
  const [activePreset, setActivePreset] = useState<string | null>(null);
  
  // Fetch items for the selected libraries with search and filters
  const { data, isLoading, error, refetch } = useLibraryItems({
    libraryIds,
    page,
    limit: 50,
    search,
    enabled: libraryIds.length > 0 && !userLoading,
    mediaType: mediaType !== "all" ? mediaType : undefined,
    ...filterQuery
  });
  
  // Reset page when search or filters change
  useEffect(() => {
    setPage(1);
  }, [search, mediaType, filterQuery]);

  // Update preselected items if they change
  useEffect(() => {
    if (preselectedItems.length > 0) {
      setSelectedItems(preselectedItems);
    }
  }, [preselectedItems]);

  const handleContinue = () => {
    if (selectedItems.length > 0) {
      onContinue(selectedItems);
    }
  };

  const handlePreviousPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (data?.hasMore) {
      setPage(page + 1);
    }
  };
  
  const handleMediaTypeChange = (value: string) => {
    setMediaType(value);
    // Update filter badge display
    if (value !== "all") {
      if (!activeFilters.includes("mediaType")) {
        setActiveFilters([...activeFilters, "mediaType"]);
      }
    } else {
      setActiveFilters(activeFilters.filter(f => f !== "mediaType"));
    }
  };
  
  const applyFilterPreset = (presetId: string) => {
    const preset = filterPresets.find(p => p.id === presetId);
    if (preset) {
      setActivePreset(presetId);
      setFilterQuery(preset.filter);
      setActiveFilters(["preset"]);
      
      // Reset other filters to default state
      setMediaType("all");
    }
  };
  
  const clearFilters = () => {
    setMediaType("all");
    setActiveFilters([]);
    setFilterQuery({});
    setActivePreset(null);
  };
  
  const selectAllItems = async () => {
    if (!user?.id) return;
    
    if (!libraryIds.length) {
      alert('No libraries selected');
      return;
    }

    try {
      // Build query params for fetching all items
      const params = new URLSearchParams({
        libraryIds: libraryIds.join(','),
        all: 'true',
        ...(search && { search }),
        ...(mediaType !== "all" && { mediaType }),
        ...Object.entries(filterQuery).reduce((acc, [key, value]) => {
          acc[key] = String(value);
          return acc;
        }, {} as Record<string, string>)
      });
      
      const response = await fetchApi<{ success: boolean; items: any[] }>(
        `/library-items/${user.id}?${params}`
      );
      
      if (response.success && response.items) {
        const allItemIds = response.items.map(item => item.id);
        setSelectedItems(allItemIds);
        
        // Show confirmation
        const message = `Selected ${allItemIds.length} items ${search ? `matching "${search}"` : ''} with current filters`;
        alert(message);
      }
    } catch (error) {
      console.error('Failed to select all items:', error);
      alert('Failed to select all items. Please try again.');
    }
  };
  
  const deselectAllItems = () => {
    setSelectedItems([]);
  };

  if (userLoading) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Loading user data...
      </div>
    );
  }

  if (error) {
    console.error('PosterSelector error:', error);
    return (
      <div className="text-center py-8 text-red-500">
        Error loading library items: {(error as Error).message}
        <Button onClick={() => refetch()} className="mt-4" variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" /> Try Again
        </Button>
      </div>
    );
  }

  if (!libraryIds.length) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No libraries selected. Please go back and select at least one library.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filtering UI */}
      <Card className="overflow-hidden">
        <CardContent className="p-4">
          <Tabs defaultValue="basic" onValueChange={(v) => setFilterView(v as "basic" | "advanced")}>
            <div className="flex justify-between items-center mb-4">
              <TabsList>
                <TabsTrigger value="basic">Basic Filters</TabsTrigger>
                <TabsTrigger value="advanced">Advanced Filters</TabsTrigger>
              </TabsList>
              
              {activeFilters.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFilters}
                  className="text-xs"
                >
                  Clear All Filters
                </Button>
              )}
            </div>
            
            <TabsContent value="basic" className="space-y-4">
              <div className="flex flex-wrap gap-2 items-center">
                <div className="flex-1 min-w-[200px]">
                  <Select
                    value={mediaType}
                    onValueChange={handleMediaTypeChange}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Filter by media type" />
                    </SelectTrigger>
                    <SelectContent>
                      {mediaTypeOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.value === "Movie" && <Film className="w-4 h-4 mr-2 inline" />}
                          {option.value === "Series" && <Tv className="w-4 h-4 mr-2 inline" />}
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Wand className="w-4 h-4 mr-2" />
                      Filter Presets
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    {filterPresets.map(preset => (
                      <DropdownMenuItem
                        key={preset.id}
                        onClick={() => applyFilterPreset(preset.id)}
                      >
                        {activePreset === preset.id && <Check className="w-4 h-4 mr-2" />}
                        <span className="font-medium">{preset.name}</span>
                        <span className="text-xs text-muted-foreground ml-2">
                          {preset.description}
                        </span>
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              
              {/* Active filter badges */}
              {activeFilters.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {activeFilters.includes("mediaType") && (
                    <Badge variant="secondary" className="gap-1">
                      {mediaType === "Movie" ? <Film className="w-3 h-3" /> : 
                       mediaType === "Series" ? <Tv className="w-3 h-3" /> : null}
                      {mediaTypeOptions.find(o => o.value === mediaType)?.label}
                    </Badge>
                  )}
                  
                  {activeFilters.includes("preset") && activePreset && (
                    <Badge variant="secondary" className="gap-1">
                      <Wand className="w-3 h-3" />
                      {filterPresets.find(p => p.id === activePreset)?.name}
                    </Badge>
                  )}
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="advanced" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="border-dashed">
                  <CardContent className="p-4">
                    <h3 className="text-sm font-medium mb-2 flex items-center">
                      <MonitorSmartphone className="w-4 h-4 mr-2" />
                      Resolution Filters
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant={filterQuery.resolution === "4k" ? "default" : "outline"}
                        size="sm"
                        onClick={() => {
                          setFilterQuery({...filterQuery, resolution: "4k"});
                          setActiveFilters([...activeFilters.filter(f => f !== "resolution"), "resolution"]);
                        }}
                      >
                        4K Content
                      </Button>
                      <Button
                        variant={filterQuery.resolution === "hd" ? "default" : "outline"}
                        size="sm"
                        onClick={() => {
                          setFilterQuery({...filterQuery, resolution: "hd"});
                          setActiveFilters([...activeFilters.filter(f => f !== "resolution"), "resolution"]);
                        }}
                      >
                        HD Content
                      </Button>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-dashed">
                  <CardContent className="p-4">
                    <h3 className="text-sm font-medium mb-2 flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-2" />
                      Status Filters
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant={filterQuery.status === "missing" ? "default" : "outline"}
                        size="sm"
                        onClick={() => {
                          setFilterQuery({...filterQuery, status: "missing"});
                          setActiveFilters([...activeFilters.filter(f => f !== "status"), "status"]);
                        }}
                      >
                        Missing Badges
                      </Button>
                      <Button
                        variant={filterQuery.status === "needsUpdate" ? "default" : "outline"}
                        size="sm"
                        onClick={() => {
                          setFilterQuery({...filterQuery, status: "needsUpdate"});
                          setActiveFilters([...activeFilters.filter(f => f !== "status"), "status"]);
                        }}
                      >
                        Needs Update
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Batch Selection Controls */}
      <div className="flex flex-wrap gap-2 mb-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={selectAllItems}
          disabled={isLoading}
        >
          Select All Filtered Items
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={deselectAllItems}
          disabled={selectedItems.length === 0}
        >
          Deselect All
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            // Invert selection on current page
            const currentPageIds = data?.items.map(item => item.id) || [];
            const currentPageSelected = selectedItems.filter(id => currentPageIds.includes(id));
            const currentPageNotSelected = currentPageIds.filter(id => !selectedItems.includes(id));
            const otherPagesSelected = selectedItems.filter(id => !currentPageIds.includes(id));
            
            setSelectedItems([...otherPagesSelected, ...currentPageNotSelected]);
          }}
        >
          Invert Selection
        </Button>
      </div>

      {/* Pass search handler and library IDs to PosterGrid */}
      <PosterGrid
        items={data?.items || []}
        selectedItems={selectedItems}
        onItemsChange={setSelectedItems}
        isLoading={isLoading}
        onValidationChange={setIsValid}
        totalItems={data?.total}
        searchQuery={search}
        onSearchChange={setSearch}
        libraryIds={libraryIds}
      />

      {/* Pagination controls */}
      {data && data.total > data.limit && (
        <div className="space-y-4">
          <div className="text-center text-sm text-muted-foreground">
            Page {page} of {Math.ceil(data.total / data.limit)} ({data.total} total items
            {activeFilters.length > 0 ? " with current filters" : ""})
          </div>
          <div className="flex justify-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handlePreviousPage}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleNextPage}
              disabled={!data.hasMore}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Selected items summary */}
      <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
        <div className="text-sm">
          <span className="font-medium">{selectedItems.length}</span> items selected
          {data?.total && (
            <span className="text-muted-foreground"> out of {data.total} total</span>
          )}
        </div>
        <Button 
          onClick={handleContinue}
          disabled={!isValid}
        >
          Continue with Selection
        </Button>
      </div>
    </div>
  );
};
