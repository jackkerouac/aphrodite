import React, { useState, useEffect } from "react";
import { Card, CardContent, Checkbox, Button, Input, Skeleton } from "@/components/ui";
import { Search, CheckCircle2, Circle, Image, Loader2 } from "lucide-react";
import { fetchApi } from "@/lib/api-client";
import { useUser } from "@/contexts/UserContext";

export interface PosterItem {
  id: string;
  title: string;
  year?: string;
  type: "Movie" | "Series";
  posterUrl?: string;
  overview?: string;
  mediaType?: string;
  path?: string;
  serverId?: string;
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

  const handleSelectAllInLibrary = async () => {
    if (!user?.id) return;
    
    if (!libraryIds.length) {
      alert('No libraries selected');
      return;
    }

    try {
      setIsSelectingAllItems(true);
      
      // Build query params for fetching all items
      const params = new URLSearchParams({
        libraryIds: libraryIds.join(','),
        all: 'true',
        ...(searchQuery && { search: searchQuery })
      });
      
      const response = await fetchApi<{ success: boolean; items: PosterItem[] }>(
        `/library-items/${user.id}?${params}`
      );
      
      if (response.success && response.items) {
        const allItemIds = response.items.map(item => item.id);
        onItemsChange(allItemIds);
        
        // Show confirmation
        const message = searchQuery 
          ? `Selected ${allItemIds.length} items matching "${searchQuery}" from all pages`
          : `Selected all ${allItemIds.length} items in the library`;
        alert(message);
      }
    } catch (error) {
      console.error('Failed to select all items:', error);
      alert('Failed to select all items. Please try again.');
    } finally {
      setIsSelectingAllItems(false);
    }
  };

  const handleClearSelection = () => {
    onItemsChange([]);
  };

  const handleInvertSelection = () => {
    const currentPageIds = items.map(item => item.id);
    const currentPageSelected = selectedItems.filter(id => currentPageIds.includes(id));
    const currentPageNotSelected = currentPageIds.filter(id => !selectedItems.includes(id));
    const otherPagesSelected = selectedItems.filter(id => !currentPageIds.includes(id));
    
    onItemsChange([...otherPagesSelected, ...currentPageNotSelected]);
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
      {/* Search and selection tools */}
      <div className="flex flex-col gap-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search all items..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleSelectAllPage}
          >
            {selectAll ? "Deselect All" : "Select All on Page"}
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleSelectAllInLibrary}
            disabled={isSelectingAllItems}
          >
            {isSelectingAllItems ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Selecting...
              </>
            ) : (
              `Select All Items in Library${searchQuery ? ' (filtered)' : ''}`
            )}
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleClearSelection}
            disabled={selectedItems.length === 0}
          >
            Clear Selection
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleInvertSelection}
          >
            Invert Selection
          </Button>
        </div>
      </div>

      {/* Selection summary */}
      <div className="text-sm text-muted-foreground">
        {selectedItems.length} items selected
        {totalItems && totalItems > items.length && (
          <span> (out of {totalItems} total in library{searchQuery ? ` matching "${searchQuery}"` : ''})</span>
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
                </div>
                <div className="space-y-1">
                  <h4 className="text-sm font-medium line-clamp-2">{item.title}</h4>
                  <div className="flex justify-between items-center text-xs text-muted-foreground">
                    <span>{item.type}</span>
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
          No items match your search criteria.
        </div>
      )}

      {items.length === 0 && !searchQuery && !isLoading && (
        <div className="text-center py-8 text-muted-foreground">
          No items available in the selected libraries.
        </div>
      )}
    </div>
  );
};

// Note: This component is prepared for virtualization but currently uses a simple grid.
// To add virtualization:
// 1. Install react-window: npm install react-window @types/react-window
// 2. Replace the grid div with a FixedSizeGrid from react-window
// 3. Implement cell renderer for virtualized items
// 4. Add InfiniteLoader for pagination if needed
// 5. Handle window resize to adjust grid columns dynamically
