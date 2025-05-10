import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api-client";
import { useUser } from "@/contexts/UserContext";

export interface LibraryItem {
  id: string;
  title: string;
  year?: string;
  type: "Movie" | "Series" | "Season" | "Episode";
  posterUrl?: string;
  overview?: string;
  mediaType?: string;
  path?: string;
  serverId?: string;
}

interface UseLibraryItemsOptions {
  libraryIds: string[];
  page?: number;
  limit?: number;
  search?: string;
  enabled?: boolean;
}

interface ApiLibraryItemsResponse {
  success: boolean;
  items: LibraryItem[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

interface LibraryItemsResponse {
  items: LibraryItem[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export function useLibraryItems({
  libraryIds,
  page = 1,
  limit = 50,
  search = "",
  enabled = true
}: UseLibraryItemsOptions) {
  const { user } = useUser();
  console.log('useLibraryItems called with:', { libraryIds, page, limit, search, enabled, userId: user?.id });
  return useQuery<LibraryItemsResponse>({
    queryKey: ["library-items", libraryIds, page, limit, search, user?.id],
    queryFn: async () => {
      console.log('Library items query function called');
      if (!libraryIds.length) {
        console.log('No library IDs provided, returning empty');
        return {
          items: [],
          total: 0,
          page,
          limit,
          hasMore: false
        };
      }

      // Fetch items from multiple libraries
      const params = new URLSearchParams({
        page: String(page),
        limit: String(limit),
        ...(search && { search }),
        libraryIds: libraryIds.join(",")
      });
      
      const url = `/library-items/${user?.id || '1'}?${params}`;
      console.log('Fetching library items from:', url);

      const data = await fetchApi<ApiLibraryItemsResponse>(url);
      console.log('Library items API response:', data);
      // Extract the response data
      if (data.success !== undefined) {
        return {
          items: data.items || [],
          total: data.total || 0,
          page: data.page || page,
          limit: data.limit || limit,
          hasMore: data.hasMore || false
        };
      }
      throw new Error('Failed to fetch library items');
    },
    enabled: enabled && libraryIds.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook to fetch all items for selected libraries (without pagination, for export/processing)
export function useAllLibraryItems(libraryIds: string[], enabled = false) {
  const { user } = useUser();
  return useQuery<LibraryItem[]>({
    queryKey: ["all-library-items", libraryIds, user?.id],
    queryFn: async () => {
      if (!libraryIds.length) {
        return [];
      }

      const params = new URLSearchParams({
        libraryIds: libraryIds.join(","),
        all: "true" // Special flag to fetch all items
      });

      const data = await fetchApi<{ success: boolean; items: LibraryItem[] }>(`/library-items/${user?.id || '1'}?${params}`);
      // Extract items from response
      if (data.success && data.items) {
        return data.items;
      }
      throw new Error('Failed to fetch library items');
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
