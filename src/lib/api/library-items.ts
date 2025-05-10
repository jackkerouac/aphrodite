export interface LibraryItemsParams {
  libraryIds: string[];
  page: number;
  limit: number;
  search?: string;
  userId: string;
}

export interface LibraryItem {
  id: string;
  name: string;
  type: string;
  primaryImageItemId?: string;
  primaryImageTag?: string;
  serverId?: string;
}

export interface LibraryItemsResponse {
  items: LibraryItem[];
  totalCount: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

const libraryItemsApi = {
  async getItems(params: LibraryItemsParams): Promise<LibraryItemsResponse> {
    const { libraryIds, page, limit, search, userId } = params;
    
    const queryParams = new URLSearchParams({
      libraryIds: libraryIds.join(','),
      page: page.toString(),
      limit: limit.toString(),
      ...(search && { search }),
      userId
    });

    const response = await fetch(`/api/library-items?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch library items: ${response.statusText}`);
    }

    return response.json();
  }
};

export default libraryItemsApi;
