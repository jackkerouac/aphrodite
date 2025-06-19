"use client"

import { PosterCard } from "./poster-card"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, ImageOff } from "lucide-react"

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

interface PosterGridProps {
  items: MediaItem[]
  loading: boolean
  selectedItems?: Set<string>
  onSelectionChange?: (itemId: string, selected: boolean) => void
  selectionMode?: boolean
  onPosterClick?: (item: MediaItem) => void
}

export function PosterGrid({ 
  items, 
  loading, 
  selectedItems = new Set(), 
  onSelectionChange, 
  selectionMode = false,
  onPosterClick
}: PosterGridProps) {
  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-10">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading posters...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (items.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <ImageOff className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No items found</h3>
          <p className="text-muted-foreground text-center">
            Try adjusting your search criteria or filters
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {items.map((item) => (
        <PosterCard 
          key={item.id} 
          item={item}
          isSelected={selectedItems.has(item.id)}
          onSelectionChange={onSelectionChange}
          selectionMode={selectionMode}
          onPosterClick={onPosterClick}
        />
      ))}
    </div>
  )
}