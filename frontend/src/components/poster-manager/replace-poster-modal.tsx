"use client"

import { useState, useEffect, useMemo } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LoadingSpinner } from "./poster-detail-modal"
import { Search, Download, X, Filter } from "lucide-react"
import Image from "next/image"
import { toast } from "sonner"

// Language code to display name mapping
const LANGUAGE_NAMES: Record<string, string> = {
  'en': 'English',
  'de': 'German',
  'fr': 'French',
  'es': 'Spanish',
  'it': 'Italian',
  'ja': 'Japanese',
  'ko': 'Korean',
  'zh': 'Chinese',
  'pt': 'Portuguese',
  'ru': 'Russian',
  'nl': 'Dutch',
  'sv': 'Swedish',
  'da': 'Danish',
  'no': 'Norwegian',
  'fi': 'Finnish',
  'pl': 'Polish',
  'cs': 'Czech',
  'hu': 'Hungarian',
  'tr': 'Turkish',
  'ar': 'Arabic',
  'he': 'Hebrew',
  'th': 'Thai',
  'hi': 'Hindi',
  'ta': 'Tamil'
}

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
  const [languageFilter, setLanguageFilter] = useState<string>('en')

  // Reset state when modal opens/closes or item changes
  useEffect(() => {
    if (isOpen && item) {
      searchPosterSources()
    } else {
      setPosterOptions([])
      setSelectedPoster(null)
      setError(null)
      setLanguageFilter('en')
    }
  }, [isOpen, item?.id])

  // Auto-adjust language filter if 'en' is not available
  useEffect(() => {
    if (posterOptions.length > 0 && languageFilter === 'en') {
      const hasEnglish = posterOptions.some(poster => poster.language === 'en')
      if (!hasEnglish) {
        // If English is not available, default to 'all'
        setLanguageFilter('all')
      }
    }
  }, [posterOptions, languageFilter])

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

  // Compute available languages from poster options
  const availableLanguages = useMemo(() => {
    const languages = new Set<string>()
    posterOptions.forEach(poster => {
      if (poster.language) {
        languages.add(poster.language)
      } else {
        languages.add('textless')
      }
    })
    
    // Convert to array and sort: EN first, then alphabetically by language name
    const langArray = Array.from(languages).filter(lang => lang !== 'textless')
    const sortedLanguages = langArray.sort((a, b) => {
      // English first
      if (a === 'en') return -1
      if (b === 'en') return 1
      
      // Then sort alphabetically by display name
      const nameA = LANGUAGE_NAMES[a] || a.toUpperCase()
      const nameB = LANGUAGE_NAMES[b] || b.toUpperCase()
      return nameA.localeCompare(nameB)
    })
    
    // Add textless at the end if it exists
    if (languages.has('textless')) {
      sortedLanguages.push('textless')
    }
    
    return sortedLanguages
  }, [posterOptions])

  // Filter posters by selected language
  const filteredPosterOptions = useMemo(() => {
    if (languageFilter === 'all') {
      return posterOptions
    }
    if (languageFilter === 'textless') {
      return posterOptions.filter(poster => !poster.language)
    }
    return posterOptions.filter(poster => poster.language === languageFilter)
  }, [posterOptions, languageFilter])

  // Clear selection if the selected poster is not in the filtered results
  useEffect(() => {
    if (selectedPoster && !filteredPosterOptions.find(p => p.id === selectedPoster.id)) {
      setSelectedPoster(null)
    }
  }, [filteredPosterOptions, selectedPoster])

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

        {/* Language Filter & Poster Grid */}
        {!isSearching && !error && posterOptions.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Language Filter:</span>
              </div>
              <Select value={languageFilter} onValueChange={setLanguageFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Languages ({posterOptions.length})</SelectItem>
                  {availableLanguages.map(lang => {
                    const count = lang === 'textless' 
                      ? posterOptions.filter(p => !p.language).length
                      : posterOptions.filter(p => p.language === lang).length
                    
                    if (lang === 'textless') {
                      return (
                        <SelectItem key={lang} value={lang}>
                          Textless ({count})
                        </SelectItem>
                      )
                    }
                    
                    const displayName = LANGUAGE_NAMES[lang] || lang.toUpperCase()
                    return (
                      <SelectItem key={lang} value={lang}>
                        {displayName} ({count})
                      </SelectItem>
                    )
                  })}
                </SelectContent>
              </Select>
            </div>
            
            <div className="text-sm text-muted-foreground">
              {languageFilter === 'all' 
                ? `Found ${posterOptions.length} alternative posters. Click to select:` 
                : `Showing ${filteredPosterOptions.length} of ${posterOptions.length} posters. Click to select:`
              }
              {filteredPosterOptions.length === 0 && languageFilter !== 'all' && (
                <span className="text-amber-600 ml-2">
                  No posters available for selected language filter.
                </span>
              )}
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredPosterOptions.map((poster) => (
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
