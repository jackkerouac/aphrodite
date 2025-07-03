"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { LoadingSpinner } from "./poster-detail-modal"
import { Search, Download, X } from "lucide-react"
import Image from "next/image"
import { toast } from "sonner"

interface PosterOption {
  id: string
  source: string
  url: string
  thumbnail_url?: string
  width?: number
  height?: number
  language?: string
  vote_average?: number
  vote_count?: number
  file_size_estimate?: string
  quality_score?: number
}

interface MediaItem {
  id: string
  title: string
  type: string
  year?: number
  jellyfin_id: string
}

interface ReplacePosterModalProps {
  item: MediaItem | null
  isOpen: boolean
  onClose: () => void
  onPosterReplaced: (itemId: string, newPosterUrl: string) => void
  onRefreshGrid?: () => void
}

export function ReplacePosterModal({ 
  item, 
  isOpen, 
  onClose, 
  onPosterReplaced,
  onRefreshGrid
}: ReplacePosterModalProps) {
  const [isSearching, setIsSearching] = useState(false)
  const [isReplacing, setIsReplacing] = useState(false)
  const [posterOptions, setPosterOptions] = useState<PosterOption[]>([])
  const [selectedPoster, setSelectedPoster] = useState<PosterOption | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Reset state when modal opens/closes or item changes
  useEffect(() => {
    if (isOpen && item) {
      searchPosterSources()
    } else {
      setPosterOptions([])
      setSelectedPoster(null)
      setError(null)
    }
  }, [isOpen, item?.id])

  const searchPosterSources = async () => {
    if (!item) return

    setIsSearching(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/v1/poster-replacement/items/${item.id}/poster-sources`)
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        setPosterOptions(result.posters || [])
        if (result.posters?.length === 0) {
          setError("No alternative posters found from external sources")
        }
      } else {
        setError(result.message || "Failed to search for posters")
      }
    } catch (err) {
      console.error('Error searching poster sources:', err)
      setError(`Search failed: ${err.message}`)
    } finally {
      setIsSearching(false)
    }
  }

  const handlePosterSelect = (poster: PosterOption) => {
    setSelectedPoster(poster)
  }

  const handleReplacePoster = async () => {
    if (!item || !selectedPoster) return

    setIsReplacing(true)
    
    try {
      const response = await fetch(`/api/v1/poster-replacement/items/${item.id}/replace-poster`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_id: item.id,
          jellyfin_id: item.jellyfin_id,
          selected_poster: selectedPoster
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `Replace failed: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        // Notify parent components
        onPosterReplaced(item.id, result.new_poster_url)
        
        if (onRefreshGrid) {
          onRefreshGrid()
        }
        
        toast.success(result.message)
        onClose()
      } else {
        throw new Error(result.message || 'Failed to replace poster')
      }
    } catch (err) {
      console.error('Error replacing poster:', err)
      toast.error(`Failed to replace poster: ${err.message}`)
    } finally {
      setIsReplacing(false)
    }
  }

  if (!item) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Replace Poster: {item.title}
          </DialogTitle>
        </DialogHeader>

        {/* Search Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-blue-800">
            <Search className="h-4 w-4" />
            <span className="text-sm">
              Searching external sources for alternative posters for <strong>{item.title}</strong>
              {item.year && ` (${item.year})`}
            </span>
          </div>
        </div>

        {/* Loading State */}
        {isSearching && (
          <div className="flex flex-col items-center justify-center py-12">
            <LoadingSpinner className="h-8 w-8 mb-4" />
            <p>Searching external sources...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-800">
              <X className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}

        {/* Poster Grid */}
        {!isSearching && !error && posterOptions.length > 0 && (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              Found {posterOptions.length} alternative posters. Click to select:
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {posterOptions.map((poster) => (
                <div
                  key={poster.id}
                  className={`cursor-pointer rounded-lg border-2 transition-all hover:shadow-lg ${
                    selectedPoster?.id === poster.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handlePosterSelect(poster)}
                >
                  <div className="relative aspect-[2/3] bg-muted rounded-t-lg overflow-hidden">
                    {poster.thumbnail_url && (
                      <Image
                        src={poster.thumbnail_url}
                        alt={`${poster.source} poster`}
                        fill
                        className="object-cover"
                        onError={(e) => {
                          // Fallback to main URL if thumbnail fails
                          e.currentTarget.src = poster.url
                        }}
                      />
                    )}
                    
                    {/* Source Badge */}
                    <div className="absolute top-2 left-2">
                      <Badge variant="secondary" className="text-xs">
                        {poster.source.toUpperCase()}
                      </Badge>
                    </div>
                    
                    {/* Textless Badge */}
                    {!poster.language && (
                      <div className="absolute top-2 left-2 mt-6">
                        <Badge variant="outline" className="text-xs bg-green-100 text-green-800 border-green-300">
                          Textless
                        </Badge>
                      </div>
                    )}
                    
                    {/* Resolution Badge */}
                    {poster.width && poster.height && (
                      <div className="absolute top-2 right-2">
                        <Badge variant="outline" className="text-xs">
                          {poster.width}×{poster.height}
                        </Badge>
                      </div>
                    )}
                    
                    {/* Selection Indicator */}
                    {selectedPoster?.id === poster.id && (
                      <div className="absolute inset-0 bg-blue-500 bg-opacity-20 flex items-center justify-center">
                        <div className="bg-blue-500 text-white rounded-full p-2">
                          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="p-3 space-y-1">
                    <div className="text-xs space-y-1">
                      <div>
                        <strong>Language:</strong> {poster.language ? poster.language.toUpperCase() : 'Textless'}
                      </div>
                      {poster.file_size_estimate && (
                        <div><strong>Size:</strong> {poster.file_size_estimate}</div>
                      )}
                      {poster.vote_count && poster.vote_count > 0 && (
                        <div>
                          <strong>Rating:</strong> {poster.vote_average?.toFixed(1) || 'N/A'}/10 
                          ({poster.vote_count} votes)
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            {selectedPoster && (
              <>Selected: {selectedPoster.source.toUpperCase()} poster 
              {selectedPoster.width && selectedPoster.height && 
                ` (${selectedPoster.width}×${selectedPoster.height})`}
              </>
            )}
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose} disabled={isReplacing}>
              Cancel
            </Button>
            <Button 
              onClick={handleReplacePoster}
              disabled={!selectedPoster || isReplacing}
              className="min-w-[120px]"
            >
              {isReplacing ? (
                <>
                  <LoadingSpinner className="h-4 w-4 mr-2" />
                  Replacing...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Replace Poster
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
