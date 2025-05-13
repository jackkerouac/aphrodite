import React, { useState, useEffect } from "react";
import { Card, CardContent, Checkbox, Button, Input, Skeleton, Badge } from "@/components/ui";
import { 
  Search, 
  CheckCircle2, 
  Circle, 
  Image, 
  Loader2, 
  Film, 
  Tv,
  Volume2,
  Star,
  MonitorSmartphone,
  Badge as BadgeIcon
} from "lucide-react";
import { fetchApi } from "@/lib/api-client";
import { useUser } from "@/contexts/UserContext";

export interface PosterItem {
  id: string;
  title: string;
  year?: string;
  type: "Movie" | "Series" | "Season" | "Episode";
  posterUrl?: string;
  overview?: string;
  mediaType?: string;
  path?: string;
  serverId?: string;
  resolution?: string;
  audio?: string;
  review?: string;
}

interface PosterGridProps {
  items: PosterItem[];
  selectedItems: string[];
  onItemsChange: (items: string[]) => void;
  isLoading?: boolean;
  onValidationChange?: (isValid: boolean) => void;
  totalItems?: number;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  libraryIds: string[];
}

export const PosterGrid: React.FC<PosterGridProps> = ({
  items,
  selectedItems,
  onItemsChange,
  isLoading = false,
  onValidationChange,
  totalItems,
  searchQuery,
  onSearchChange,
  libraryIds
}) => {
  const { user } = useUser();
  const [selectAll, setSelectAll] = useState(false);
  const [isSelectingAllItems, setIsSelectingAllItems] = useState(false);
  const [searchDebounce, setSearchDebounce] = useState(searchQuery);

  // Update validation status when selection changes
  useEffect(() => {
    const isValid = selectedItems.length > 0;
    onValidationChange?.(isValid);
  }, [selectedItems, onValidationChange]);

  // Update select all checkbox state
  useEffect(() => {
    if (items.length > 0) {
      const allPageItemsSelected = items.every(item => 
        selectedItems.includes(item.id)
      );
      setSelectAll(allPageItemsSelected);
    }
  }, [selectedItems, items]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchChange(searchDebounce);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchDebounce, onSearchChange]);

  const handleItemToggle = (itemId: string) => {
    if (selectedItems.includes(itemId)) {
      onItemsChange(selectedItems.filter(id => id !== itemId));
    } else {
      onItemsChange([...selectedItems, itemId]);
    }
  };

  const handleSelectAllPage = () => {
    if (selectAll) {
      // Deselect all items on current page
      const pageIds = items.map(item => item.id);
      onItemsChange(selectedItems.filter(id => !pageIds.includes(id)));
    } else {
      // Select all items on current page
      const pageIds = items.map(item => item.id);
      const newSelection = [...new Set([...selectedItems, ...pageIds])];
      onItemsChange(newSelection);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex gap-2 mb-4">
          <Skeleton className="flex-1 h-10" />
          <Skeleton className="w-32 h-10" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {[...Array(12)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-2">
                <Skeleton className="aspect-[2/3] w-full mb-2" />
                <Skeleton className="h-4 w-full mb-1" />
                <Skeleton className="h-3 w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search input */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search titles, years, or content types..."
            value={searchDebounce}
            onChange={(e) => setSearchDebounce(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Selection summary */}
      <div className="text-sm text-muted-foreground flex flex-wrap items-center gap-2">
        <span className="font-medium">{selectedItems.length}</span> items selected
        {totalItems && totalItems > 0 && (
          <span className="text-muted-foreground">
            out of <span className="font-medium">{totalItems}</span> total
            {searchQuery && <span> matching "<span className="italic">{searchQuery}</span>"</span>}
          </span>
        )}
        {items.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSelectAllPage}
            className="h-7 px-2 ml-2"
          >
            {selectAll ? "Deselect Page" : "Select Page"}
          </Button>
        )}
      </div>

      {/* Grid of items */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 pb-4">
        {items.map((item) => {
          const isSelected = selectedItems.includes(item.id);
          
          return (
            <Card
              key={item.id}
              className={`cursor-pointer transition-all duration-200 ${
                isSelected ? "border-primary ring-2 ring-primary/20" : "hover:border-gray-300"
              }`}
              onClick={() => handleItemToggle(item.id)}
            >
              <CardContent className="p-2">
                <div className="relative aspect-[2/3] mb-2 bg-muted rounded overflow-hidden">
                  {item.posterUrl ? (
                    <img
                      src={item.posterUrl}
                      alt={item.title}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Image className="h-12 w-12 text-muted-foreground" />
                    </div>
                  )}
                  <div className="absolute top-2 right-2">
                    <div className={`rounded-full p-1 ${
                      isSelected ? "bg-primary text-primary-foreground" : "bg-black/50 text-white"
                    }`}>
                      {isSelected ? (
                        <CheckCircle2 className="h-4 w-4" />
                      ) : (
                        <Circle className="h-4 w-4" />
                      )}
                    </div>
                  </div>
                  
                  {/* Badge indicators */}
                  <div className="absolute bottom-1 left-1 flex gap-1">
                    {item.resolution === "4k" && (
                      <Badge variant="secondary" className="bg-black/70 text-white text-xs py-0 h-5">
                        <MonitorSmartphone className="h-3 w-3 mr-1" />4K
                      </Badge>
                    )}
                    {item.audio === "dolby-atmos" && (
                      <Badge variant="secondary" className="bg-black/70 text-white text-xs py-0 h-5">
                        <Volume2 className="h-3 w-3 mr-1" />Atmos
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="space-y-1">
                  <h4 className="text-sm font-medium line-clamp-2">{item.title}</h4>
                  <div className="flex justify-between items-center text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      {item.type === "Movie" ? (
                        <Film className="h-3 w-3" />
                      ) : item.type === "Series" ? (
                        <Tv className="h-3 w-3" />
                      ) : null}
                      {item.type}
                    </span>
                    {item.year && <span>{item.year}</span>}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Empty states */}
      {items.length === 0 && searchQuery && (
        <div className="text-center py-8 text-muted-foreground">
          <Image className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
          <p>No items match your search criteria.</p>
          <p className="text-sm mt-2">Try adjusting your filters or search terms.</p>
        </div>
      )}

      {items.length === 0 && !searchQuery && !isLoading && (
        <div className="text-center py-8 text-muted-foreground">
          <Image className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
          <p>No items available in the selected libraries.</p>
          <p className="text-sm mt-2">Try selecting different libraries or adjusting filters.</p>
        </div>
      )}
    </div>
  );
};
