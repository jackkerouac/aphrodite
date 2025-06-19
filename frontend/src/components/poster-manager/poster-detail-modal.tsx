"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Calendar, Star, Tag, Image as ImageIcon, RotateCcw, Plus, Minus, ImageOff } from "lucide-react"
import Image from "next/image"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { BadgeSelectionModal } from "./badge-selection-modal"
import { ReplacePosterModal } from "./replace-poster-modal"

export const LoadingSpinner = ({className}: {className?: string}) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={cn("animate-spin", className)}
    >
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  )
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

interface PosterDetailModalProps {
  item: MediaItem | null
  isOpen: boolean
  onClose: () => void
  onTagUpdate: (itemId: string, hasTag: boolean) => void
  onPosterUpdate: (itemId: string, newPosterUrl: string) => void
  onRefreshGrid?: () => void
}

export function PosterDetailModal({ 
  item, 
  isOpen, 
  onClose, 
  onTagUpdate,
  onPosterUpdate,
  onRefreshGrid
}: PosterDetailModalProps) {
  const [imageError, setImageError] = useState(false)
  const [loading, setLoading] = useState(false)
  const [applyingBadges, setApplyingBadges] = useState(false)
  const [restoringOriginal, setRestoringOriginal] = useState(false)
  const [currentPosterUrl, setCurrentPosterUrl] = useState<string | undefined>(undefined)
  const [showBadgeSelection, setShowBadgeSelection] = useState(false)
  const [showReplacePoster, setShowReplacePoster] = useState(false)

  // Reset modal state when item changes
  useEffect(() => {
    if (item) {
      setCurrentPosterUrl(undefined)
      setImageError(false)
      setLoading(false)
      setApplyingBadges(false)
      setRestoringOriginal(false)
      setShowBadgeSelection(false)
    }
  }, [item?.id])

  const handlePosterReplaced = (itemId: string, newPosterUrl: string) => {
    // Update the current poster URL
    setCurrentPosterUrl(newPosterUrl)
    setImageError(false)
    
    // Update parent component
    onPosterUpdate(itemId, newPosterUrl)
    
    // Refresh grid if available
    if (onRefreshGrid) {
      onRefreshGrid()
    }
  }

  if (!item) return null

  // Use current poster URL or fall back to item's poster URL
  const displayPosterUrl = currentPosterUrl || item.poster_url

  const handleTagAction = async (action: 'add' | 'remove') => {
    if (!item) return
    
    try {
      setLoading(true)
      const endpoint = action === 'add' 
        ? '/api/v1/poster-manager/tags/add'
        : '/api/v1/poster-manager/tags/remove'
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_ids: [item.id] })
      })

      if (!response.ok) {
        throw new Error(`Failed to ${action} tag`)
      }

      const result = await response.json()
      
      if (result.success) {
        onTagUpdate(item.id, action === 'add')
        toast.success(`Tag ${action === 'add' ? 'added' : 'removed'} successfully`)
        onClose()
      } else {
        throw new Error(result.message || `Failed to ${action} tag`)
      }
    } catch (error) {
      console.error(`Error ${action}ing tag:`, error)
      toast.error(`Failed to ${action} tag`)
    } finally {
      setLoading(false)
    }
  }

  const handleReplaceAction = () => {
    setShowReplacePoster(true)
  }

  const handleRestoreAction = async () => {
    if (!item) return
    
    try {
      setRestoringOriginal(true)
      
      const response = await fetch('/api/v1/poster-manager/restore-original', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_id: item.id,
          jellyfin_id: item.jellyfin_id
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `Failed to restore original: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        // Create a cache-busted URL for the restored poster
        const timestamp = Date.now()
        const restoredPosterUrl = item.poster_url ? 
          `${item.poster_url}?restored=${timestamp}` : 
          `/api/v1/images/proxy/image/${item.jellyfin_id}/thumbnail?restored=${timestamp}`
        
        // Reset the poster URL to force refresh from Jellyfin with cache busting
        setCurrentPosterUrl(restoredPosterUrl)
        setImageError(false)
        
        // Remove the aphrodite-overlay tag (update badge status)
        onTagUpdate(item.id, false)
        
        // Update parent component with cache-busted original poster URL
        onPosterUpdate(item.id, restoredPosterUrl)
        
        // Refresh the grid to ensure updated state
        if (onRefreshGrid) {
          onRefreshGrid()
        }
        
        // Close the modal to show the refreshed grid
        onClose()
        
        toast.success(result.message)
      } else {
        throw new Error(result.message || 'Failed to restore original poster')
      }
    } catch (error) {
      console.error('Error restoring original poster:', error)
      toast.error(`Failed to restore original: ${error.message}`)
    } finally {
      setRestoringOriginal(false)
    }
  }

  const handleApplyBadgesAction = async (selectedBadges: string[]) => {
    if (!item) return
    
    try {
      setApplyingBadges(true)
      
      // Call poster-specific badge processing API
      const response = await fetch('/api/v1/poster-manager/apply-badges', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_id: item.id,
          jellyfin_id: item.jellyfin_id,
          badge_types: selectedBadges
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `Failed to apply badges: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        // Create a cache-busted URL for the newly badged poster
        const timestamp = Date.now()
        const newPosterUrl = `/api/v1/images/proxy/image/${item.jellyfin_id}/thumbnail?badged=${timestamp}`
        
        // Update the poster URL in modal with cache-busting
        setCurrentPosterUrl(newPosterUrl)
        setImageError(false)
        
        // Add the aphrodite-overlay tag (update badge status)
        onTagUpdate(item.id, true)
        
        // Update parent component with cache-busted poster URL
        onPosterUpdate(item.id, newPosterUrl)
        
        // Refresh the grid to ensure updated state
        if (onRefreshGrid) {
          onRefreshGrid()
        }
        
        // Close badge selection modal
        setShowBadgeSelection(false)
        
        // Close the modal to show the refreshed grid
        onClose()
        
        toast.success(`Badges applied successfully! (${result.applied_badges?.join(', ') || 'Unknown badges'})`)
      } else {
        throw new Error(result.message || 'Failed to apply badges')
      }
    } catch (error) {
      console.error('Error applying badges:', error)
      toast.error(`Failed to apply badges: ${error.message}`)
    } finally {
      setApplyingBadges(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl max-h-[95vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">{item.title}</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Column - Poster Image */}
          <div className="space-y-4">
            <div className="relative aspect-[2/3] bg-muted rounded-lg overflow-hidden">
              {/* Loading overlay when applying badges or restoring */}
              {(applyingBadges || restoringOriginal) && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
                  <div className="bg-background border rounded-lg p-4 flex flex-col items-center gap-2 shadow-lg">
                    <LoadingSpinner className="h-8 w-8 text-foreground" />
                    <span className="text-sm font-medium text-foreground">
                      {applyingBadges ? 'Applying badges...' : 'Restoring original...'}
                    </span>
                  </div>
                </div>
              )}
              
              {displayPosterUrl && !imageError ? (
                <Image
                  key={displayPosterUrl} // Force re-render when URL changes
                  src={displayPosterUrl}
                  alt={item.title}
                  fill
                  className="object-cover"
                  onError={() => setImageError(true)}
                  sizes="(max-width: 768px) 100vw, 50vw"
                />
              ) : (
                <div className="flex items-center justify-center h-full bg-muted">
                  <ImageOff className="h-16 w-16 text-muted-foreground" />
                </div>
              )}
              
              {/* Badge Status Overlay */}
              <div className="absolute top-4 left-4">
                <Badge 
                  variant={item.badge_status === "BADGED" ? "destructive" : "secondary"} 
                  className="text-sm"
                >
                  {item.badge_status}
                </Badge>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="space-y-3">
              <div className="grid grid-cols-1 gap-2">
                <Button
                  onClick={() => setShowBadgeSelection(true)}
                  disabled={applyingBadges || restoringOriginal}
                  className="w-full"
                >
                  <ImageIcon className="h-4 w-4 mr-2" />
                  Apply Badges
                </Button>
                
                {item.badge_status === "ORIGINAL" ? (
                  <Button
                    onClick={() => handleTagAction('add')}
                    disabled={loading || applyingBadges || restoringOriginal}
                    variant="outline"
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Aphrodite Tag
                  </Button>
                ) : (
                  <Button
                    onClick={() => handleTagAction('remove')}
                    disabled={loading || applyingBadges || restoringOriginal}
                    variant="outline"
                    className="w-full"
                  >
                    <Minus className="h-4 w-4 mr-2" />
                    Remove Aphrodite Tag
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 gap-2">
                <Button
                  onClick={handleReplaceAction}
                  disabled={applyingBadges || restoringOriginal}
                  variant="outline"
                  className="w-full"
                >
                  <ImageIcon className="h-4 w-4 mr-2" />
                  Replace Poster
                </Button>
                
                <Button
                  onClick={handleRestoreAction}
                  disabled={applyingBadges || restoringOriginal}
                  variant="outline"
                  className="w-full"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Restore to Original
                </Button>
              </div>
            </div>
          </div>

          {/* Right Column - Media Information */}
          <div className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>{item.year || 'Unknown Year'}</span>
                <Separator orientation="vertical" className="h-4" />
                <Badge variant="outline" className="capitalize">
                  {item.type}
                </Badge>
              </div>

              {/* Ratings */}
              {(item.community_rating || item.official_rating) && (
                <div className="flex items-center gap-4">
                  {item.community_rating && (
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm font-medium">
                        {item.community_rating.toFixed(1)}
                      </span>
                    </div>
                  )}
                  {item.official_rating && (
                    <Badge variant="secondary" className="text-xs">
                      {item.official_rating}
                    </Badge>
                  )}
                </div>
              )}
            </div>

            <Separator />

            {/* Genres */}
            {item.genres.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Genres
                </h4>
                <div className="flex flex-wrap gap-2">
                  {item.genres.map((genre) => (
                    <Badge key={genre} variant="outline" className="text-xs">
                      {genre}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <Separator />

            {/* Overview */}
            {item.overview && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Overview</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {item.overview}
                </p>
              </div>
            )}

            <Separator />

            {/* Technical Information */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Technical Details</h4>
              <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                <div>
                  <span className="font-medium">Jellyfin ID:</span>
                  <br />
                  <span className="font-mono break-all">{item.jellyfin_id}</span>
                </div>
                <div>
                  <span className="font-medium">Internal ID:</span>
                  <br />
                  <span className="font-mono break-all">{item.id}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Badge Selection Modal */}
        <BadgeSelectionModal
          isOpen={showBadgeSelection}
          onClose={() => setShowBadgeSelection(false)}
          onApply={handleApplyBadgesAction}
          isLoading={applyingBadges}
        />

        {/* Replace Poster Modal */}
        <ReplacePosterModal
          item={item}
          isOpen={showReplacePoster}
          onClose={() => setShowReplacePoster(false)}
          onPosterReplaced={handlePosterReplaced}
          onRefreshGrid={onRefreshGrid}
        />
      </DialogContent>
    </Dialog>
  )
}
