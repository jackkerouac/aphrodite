"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar, ImageOff } from "lucide-react"
import { makeAbsoluteUrl } from "@/lib/env-config"

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

interface PosterCardProps {
  item: MediaItem
  isSelected?: boolean
  onSelectionChange?: (itemId: string, selected: boolean) => void
  selectionMode?: boolean
  onPosterClick?: (item: MediaItem) => void
}

export function PosterCard({ 
  item, 
  isSelected = false, 
  onSelectionChange, 
  selectionMode = false,
  onPosterClick
}: PosterCardProps) {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)

  const handleSelectionChange = (checked: boolean) => {
    if (onSelectionChange) {
      onSelectionChange(item.id, checked)
    }
  }

  const handlePosterClick = (event: React.MouseEvent) => {
    if (selectionMode) {
      // In selection mode, toggle selection
      event.preventDefault()
      handleSelectionChange(!isSelected)
    } else {
      // In normal mode, open detail modal
      if (onPosterClick) {
        onPosterClick(item)
      }
    }
  }

  return (
    <Card 
      className={`group hover:shadow-lg transition-all duration-200 ${
        isSelected ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950' : ''
      } ${
        selectionMode ? 'cursor-pointer hover:ring-2 hover:ring-blue-300' : 'cursor-pointer'
      }`}
      onClick={handlePosterClick}
    >
      <CardContent className="p-0 relative">
        {/* Selection Checkbox */}
        {selectionMode && (
          <div className="absolute top-2 right-2 z-20">
            <div 
              className="bg-white/90 rounded p-1 shadow-sm cursor-pointer"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                handleSelectionChange(!isSelected)
              }}
            >
              <Checkbox
                checked={isSelected}
                onCheckedChange={handleSelectionChange}
                className="pointer-events-none"
              />
            </div>
          </div>
        )}
        
        {/* Poster Image */}
        <div className="relative aspect-[2/3] bg-muted rounded-t-lg overflow-hidden">
          {item.poster_url && !imageError ? (
            <>
              {/* Use regular img tag instead of Next.js Image to bypass optimization */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                key={item.poster_url} // Force re-render when URL changes
                src={makeAbsoluteUrl(item.poster_url)}
                alt={item.title}
                className="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
                onLoad={() => setImageLoading(false)}
                onError={() => {
                  setImageError(true)
                  setImageLoading(false)
                }}
              />
              {imageLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-muted">
                  <div className="animate-pulse">
                    <ImageOff className="h-8 w-8 text-muted-foreground" />
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full bg-muted">
              <ImageOff className="h-12 w-12 text-muted-foreground" />
            </div>
          )}

          {/* Badge Status */}
          <div className="absolute top-2 left-2">
            <Badge 
              variant={item.badge_status === "BADGED" ? "destructive" : "secondary"} 
              className="text-xs"
            >
              {item.badge_status}
            </Badge>
          </div>
        </div>

        {/* Content */}
        <div className="p-3 space-y-2">
          {/* Title */}
          <h3 className="font-medium text-sm line-clamp-2 leading-tight">
            {item.title}
          </h3>

          {/* Year */}
          {item.year && (
            <div className="flex items-center text-xs text-muted-foreground">
              <Calendar className="h-3 w-3 mr-1" />
              {item.year}
            </div>
          )}

          {/* Genres */}
          {item.genres.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {item.genres.slice(0, 2).map((genre) => (
                <Badge key={genre} variant="outline" className="text-xs px-1 py-0">
                  {genre}
                </Badge>
              ))}
              {item.genres.length > 2 && (
                <Badge variant="outline" className="text-xs px-1 py-0">
                  +{item.genres.length - 2}
                </Badge>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}