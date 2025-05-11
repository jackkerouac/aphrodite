import React, { useState, useEffect } from "react";
import { PosterGrid } from "./poster-grid";
import { useLibraryItems } from "@/hooks/useLibraryItems";
import { Button } from "@/components/ui";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useUser } from "@/contexts/UserContext";

interface PosterSelectorProps {
  libraryIds: string[];
  onContinue: (selectedItems: string[]) => void;
  preselectedItems?: string[];
}

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

  // Fetch items for the selected libraries with search
  const { data, isLoading, error } = useLibraryItems({
    libraryIds,
    page,
    limit: 50,
    search,
    enabled: libraryIds.length > 0 && !userLoading
  });
  
  console.log('PosterSelector render:', { libraryIds, data, isLoading, error, userLoading });

  // Reset page when search changes
  useEffect(() => {
    setPage(1);
  }, [search]);

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

  console.log('PosterSelector data:', data);
  console.log('Selected libraries:', libraryIds);

  return (
    <div className="space-y-4">
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
            Page {page} of {Math.ceil(data.total / data.limit)} ({data.total} total items)
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

      {/* Continue button */}
      <div className="flex justify-end mt-6">
        <Button 
          onClick={handleContinue}
          disabled={!isValid}
        >
          Continue with {selectedItems.length} items
        </Button>
      </div>
    </div>
  );
};
