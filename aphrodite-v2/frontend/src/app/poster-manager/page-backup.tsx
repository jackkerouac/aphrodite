"use client"

import { useState, useEffect } from "react"
import { LibrarySelector } from "@/components/poster-manager/library-selector"
import { PosterGrid } from "@/components/poster-manager/poster-grid"
import { SearchFilters } from "@/components/poster-manager/search-filters"
import { SelectionToolbar } from "@/components/poster-manager/selection-toolbar"
import { SelectionCounter } from "@/components/poster-manager/selection-counter"
import { PaginationControls } from "@/components/poster-manager/pagination-controls"
import { PosterDetailModal } from "@/components/poster-manager/poster-detail-modal"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, RefreshCw } from "lucide-react"
import { toast } from "sonner"

interface Library {
  id: string
  name: string
  type: string
  path: string[]
}

interface MediaItem {
  id: string
  title: string
  type: string
  year?: number
  overview: string
  genres: string[]
  community_rating?: number
  official_rating?: string
  poster_url?: string
  jellyfin_id: string
  badge_status: string
}

interface LibraryStats {
  total_items: number
  movies: number
  tv_shows: number
  other: number
  years: number[]
  genres: string[]
}

export default function PosterManagerPage() {
  const [libraries, setLibraries] = useState<Library[]>([])
  const [selectedLibrary, setSelectedLibrary] = useState<string>("")
  const [items, setItems] = useState<MediaItem[]>([])
  const [stats, setStats] = useState<LibraryStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [badgeFilter, setBadgeFilter] = useState<'all' | 'badged' | 'original'>('all')
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(50)
  const [totalItems, setTotalItems] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  
  // Selection state
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [selectionMode, setSelectionMode] = useState(false)
  
  // Modal state
  const [selectedPoster, setSelectedPoster] = useState<MediaItem | null>(null)
  const [showDetailModal, setShowDetailModal] = useState(false)

  // Load libraries on component mount
  useEffect(() => {
    loadLibraries()
  }, [])

  // Load items when library selection changes
  useEffect(() => {
    if (selectedLibrary) {
      loadLibraryItems()
      loadLibraryStats()
    }
  }, [selectedLibrary])

  // Search when filters change
  useEffect(() => {
    if (selectedLibrary) {
      setCurrentPage(1) // Reset to first page when filters change
      if (searchQuery || badgeFilter !== 'all') {
        searchItems(1)
      } else {
        loadLibraryItems(1)
      }
    }
  }, [searchQuery, badgeFilter])

  const loadLibraries = async () => {
    try {
      setLoading(true)
      const response = await fetch("/api/v1/poster-manager/libraries")
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      setLibraries(data.libraries || [])
      
      // Auto-select first library if available
      if (data.libraries && data.libraries.length > 0) {
        setSelectedLibrary(data.libraries[0].id)
      }
    } catch (error) {
      console.error("Error loading libraries:", error)
      toast.error("Failed to load Jellyfin libraries. Please check your connection.")
    } finally {
      setLoading(false)
    }
  }

  const loadLibraryItems = async (page: number = 1) => {
    if (!selectedLibrary) return
    
    try {
      setLoading(true)
      const offset = (page - 1) * itemsPerPage
      const response = await fetch(`/api/v1/poster-manager/libraries/${selectedLibrary}/items?limit=${itemsPerPage}&offset=${offset}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      setItems(data.items || [])
      setTotalItems(data.total_count || 0)
      setHasMore(data.has_more || false)
      setCurrentPage(page)
    } catch (error) {
      console.error("Error loading library items:", error)
      toast.error("Failed to load library items")
    } finally {
      setLoading(false)
    }
  }

  const loadLibraryStats = async () => {
    if (!selectedLibrary) return
    
    try {
      const response = await fetch(`/api/v1/poster-manager/libraries/${selectedLibrary}/stats`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error("Error loading library stats:", error)
      // Don't show error toast for stats, it's not critical
    }
  }

  const searchItems = async (page: number = 1) => {
    if (!selectedLibrary) return
    
    try {
      setLoading(true)
      const offset = (page - 1) * itemsPerPage
      const params = new URLSearchParams({
        library_id: selectedLibrary,
        limit: itemsPerPage.toString(),
        offset: offset.toString()
      })
      
      if (searchQuery.trim()) params.append("query", searchQuery.trim())
      if (badgeFilter !== 'all') {
        params.append("badge_filter", badgeFilter)
      }
      
      const response = await fetch(`/api/v1/poster-manager/search?${params}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      setItems(data.items || [])
      setTotalItems(data.total_count || 0)
      setHasMore(data.has_more || false)
      setCurrentPage(page)
    } catch (error) {
      console.error("Error searching items:", error)
      toast.error("Failed to search items")
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadLibraries()
    if (selectedLibrary) {
      await loadLibraryItems()
      await loadLibraryStats()
    }
    
    // Force refresh all poster URLs to bypass cache
    const timestamp = Date.now()
    setItems(prevItems => 
      prevItems.map(item => {
        if (item.poster_url) {
          const refreshedUrl = item.poster_url.includes('?')
            ? `${item.poster_url}&refresh=${timestamp}`
            : `${item.poster_url}?refresh=${timestamp}`
          return { ...item, poster_url: refreshedUrl }
        }
        return item
      })
    )
    
    setRefreshing(false)
    toast.success("Library refreshed successfully")
  }

  const clearFilters = () => {
    setSearchQuery("")
    setBadgeFilter('all')
  }

  // Selection handlers
  const handleSelectionChange = (itemId: string, selected: boolean) => {
    setSelectedItems(prev => {
      const newSelection = new Set(prev)
      if (selected) {
        newSelection.add(itemId)
      } else {
        newSelection.delete(itemId)
      }
      return newSelection
    })
  }

  const handleSelectAll = () => {
    const allItemIds = new Set(items.map(item => item.id))
    setSelectedItems(allItemIds)
  }

  const handleSelectNone = () => {
    setSelectedItems(new Set())
  }

  const handleToggleSelectionMode = () => {
    setSelectionMode(!selectionMode)
    if (selectionMode) {
      // Clear selection when exiting selection mode
      setSelectedItems(new Set())
    }
  }

  const refreshItemsAndClearSelection = async () => {
    // Refresh the items to show updated badge status
    if (selectedLibrary) {
      if (searchQuery || badgeFilter !== 'all') {
        await searchItems(currentPage)
      } else {
        await loadLibraryItems(currentPage)
      }
    }
    // Clear selection after refresh
    setSelectedItems(new Set())
  }

  // Pagination handlers
  const handlePageChange = (page: number) => {
    if (searchQuery || badgeFilter !== 'all') {
      searchItems(page)
    } else {
      loadLibraryItems(page)
    }
    // Clear selection when changing pages
    setSelectedItems(new Set())
    setSelectionMode(false)
  }

  const handleItemsPerPageChange = (newItemsPerPage: number) => {
    setItemsPerPage(newItemsPerPage)
    setCurrentPage(1)
    if (searchQuery || badgeFilter !== 'all') {
      searchItems(1)
    } else {
      loadLibraryItems(1)
    }
    // Clear selection when changing page size
    setSelectedItems(new Set())
    setSelectionMode(false)
  }

  // Modal handlers
  const handlePosterClick = (item: MediaItem) => {
    setSelectedPoster(item)
    setShowDetailModal(true)
  }

  const handleModalTagUpdate = (itemId: string, hasTag: boolean) => {
    // Update the item in the current list
    setItems(prevItems => 
      prevItems.map(item => {
        if (item.id === itemId) {
          // If removing tag (restoring), add cache-busting to poster URL
          if (!hasTag && item.poster_url) {
            const timestamp = Date.now()
            const cacheBustedUrl = item.poster_url.includes('?') 
              ? `${item.poster_url}&refresh=${timestamp}`
              : `${item.poster_url}?refresh=${timestamp}`
            
            return { 
              ...item, 
              badge_status: 'ORIGINAL',
              poster_url: cacheBustedUrl
            }
          }
          
          return { ...item, badge_status: hasTag ? 'BADGED' : 'ORIGINAL' }
        }
        return item
      })
    )
  }

  const handleModalPosterUpdate = (itemId: string, newPosterUrl: string) => {
    // Determine if this is a restoration (has restored parameter) or badge application
    const isRestoration = newPosterUrl.includes('?restored=')
    
    // Update the item's poster URL in the current list
    setItems(prevItems => 
      prevItems.map(item => 
        item.id === itemId 
          ? { 
              ...item, 
              poster_url: newPosterUrl, 
              badge_status: isRestoration ? 'ORIGINAL' : 'BADGED' 
            }
          : item
      )
    )
  }

  // Computed values
  const allSelected = items.length > 0 && selectedItems.size === items.length

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Poster Manager</h1>
          <p className="text-muted-foreground">
            Browse and manage your Jellyfin library posters
          </p>
        </div>
        <Button 
          onClick={handleRefresh} 
          disabled={refreshing}
          variant="outline"
        >
          {refreshing ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          Refresh
        </Button>
      </div>

      {/* Library Selection */}
      <LibrarySelector
        libraries={libraries}
        selectedLibrary={selectedLibrary}
        onLibraryChange={setSelectedLibrary}
        loading={loading}
      />

      {/* Library Stats */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Library Overview</CardTitle>
            <CardDescription>
              Statistics for the selected library
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.total_items}</div>
                <div className="text-sm text-muted-foreground">Total Items</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.movies}</div>
                <div className="text-sm text-muted-foreground">Movies</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.tv_shows}</div>
                <div className="text-sm text-muted-foreground">TV Shows</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.genres.length}</div>
                <div className="text-sm text-muted-foreground">Genres</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search and Filters */}
      {selectedLibrary && (
        <SearchFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          badgeFilter={badgeFilter}
          onBadgeFilterChange={setBadgeFilter}
          onClearFilters={clearFilters}
        />
      )}

      {/* Selection Counter */}
      {selectedLibrary && items.length > 0 && (
        <SelectionCounter
          totalItems={items.length}
          selectedCount={selectedItems.size}
          allSelected={allSelected}
          onSelectAll={handleSelectAll}
          onSelectNone={handleSelectNone}
          onToggleSelectionMode={handleToggleSelectionMode}
          selectionMode={selectionMode}
        />
      )}

      {/* Selection Toolbar */}
      <SelectionToolbar
        selectedCount={selectedItems.size}
        selectedItems={selectedItems}
        onClearSelection={handleSelectNone}
        onRefreshItems={refreshItemsAndClearSelection}
        disabled={loading}
      />

      {/* Poster Grid */}
      {selectedLibrary && (
        <>
          {/* Top Pagination */}
          {totalItems > 0 && (
            <PaginationControls
              currentPage={currentPage}
              totalItems={totalItems}
              itemsPerPage={itemsPerPage}
              onPageChange={handlePageChange}
              onItemsPerPageChange={handleItemsPerPageChange}
              loading={loading}
            />
          )}
          
          <PosterGrid
            items={items}
            loading={loading}
            selectedItems={selectedItems}
            onSelectionChange={handleSelectionChange}
            selectionMode={selectionMode}
            onPosterClick={handlePosterClick}
          />
          
          {/* Bottom Pagination */}
          {totalItems > 0 && (
            <PaginationControls
              currentPage={currentPage}
              totalItems={totalItems}
              itemsPerPage={itemsPerPage}
              onPageChange={handlePageChange}
              onItemsPerPageChange={handleItemsPerPageChange}
              loading={loading}
            />
          )}
        </>
      )}

      {/* Empty State */}
      {!selectedLibrary && !loading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-10">
            <p className="text-muted-foreground text-center">
              Select a library to view your media posters
            </p>
          </CardContent>
        </Card>
      )}

      {/* Poster Detail Modal */}
      <PosterDetailModal
        item={selectedPoster}
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false)
          setSelectedPoster(null)
        }}
        onTagUpdate={handleModalTagUpdate}
        onPosterUpdate={handleModalPosterUpdate}
        onRefreshGrid={refreshItemsAndClearSelection}
      />
    </div>
  )
}
