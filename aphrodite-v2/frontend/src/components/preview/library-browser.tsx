'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Library, Search, Film, Tv, Music, Book, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { JellyfinLibrary, MediaItem } from './types';

interface LibraryBrowserProps {
  libraries: JellyfinLibrary[];
  selectedLibrary?: string;
  mediaItems: MediaItem[];
  selectedMedia?: string;
  loading: {
    libraries: boolean;
    media: boolean;
  };
  onSelectLibrary: (libraryId: string) => void;
  onSelectMedia: (mediaId: string) => void;
  onLoadLibraries: () => void;
  onLoadMedia: (params: { search?: string }) => void;
  className?: string;
}

export function LibraryBrowser({
  libraries,
  selectedLibrary,
  mediaItems,
  selectedMedia,
  loading,
  onSelectLibrary,
  onSelectMedia,
  onLoadLibraries,
  onLoadMedia,
  className = ''
}: LibraryBrowserProps) {
  const [searchQuery, setSearchQuery] = React.useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLoadMedia({ search: searchQuery });
  };

  const getLibraryIcon = (type: string) => {
    switch (type) {
      case 'movies':
        return <Film className="h-4 w-4" />;
      case 'series':
        return <Tv className="h-4 w-4" />;
      case 'music':
        return <Music className="h-4 w-4" />;
      case 'books':
        return <Book className="h-4 w-4" />;
      default:
        return <Library className="h-4 w-4" />;
    }
  };

  const formatMediaType = (type: string) => {
    const typeMap: Record<string, string> = {
      'movie': 'Movie',
      'series': 'TV Series',
      'episode': 'Episode',
      'season': 'Season'
    };
    return typeMap[type] || type;
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Library className="h-5 w-5" />
          Media Library Browser
        </CardTitle>
        <CardDescription>
          Browse your Jellyfin libraries and select media for preview (coming soon)
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Feature Notice */}
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Library browsing is coming in a future update. Currently using example poster for consistent preview experience.
          </AlertDescription>
        </Alert>

        {/* Library Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Select Library</label>
          <div className="flex gap-2">
            <Select
              value={selectedLibrary}
              onValueChange={onSelectLibrary}
              disabled={loading.libraries || libraries.length === 0}
            >
              <SelectTrigger className="flex-1">
                <SelectValue placeholder="Choose a library..." />
              </SelectTrigger>
              <SelectContent>
                {libraries.map((library) => (
                  <SelectItem key={library.id} value={library.id}>
                    <div className="flex items-center gap-2">
                      {getLibraryIcon(library.type)}
                      {library.name}
                      {library.itemCount && (
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {library.itemCount}
                        </Badge>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              onClick={onLoadLibraries}
              disabled={loading.libraries}
            >
              {loading.libraries ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-foreground" />
              ) : (
                'Refresh'
              )}
            </Button>
          </div>
        </div>

        {/* Media Search */}
        {selectedLibrary && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Search Media</label>
            <form onSubmit={handleSearchSubmit} className="flex gap-2">
              <Input
                placeholder="Search for movies, shows, etc..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                disabled={loading.media}
              />
              <Button type="submit" variant="outline" disabled={loading.media}>
                <Search className="h-4 w-4" />
              </Button>
            </form>
          </div>
        )}

        {/* Media Grid */}
        {selectedLibrary && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Media Items</label>
              {mediaItems.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {mediaItems.length} items
                </Badge>
              )}
            </div>

            {loading.media ? (
              <div className="flex items-center justify-center py-8">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted border-t-primary" />
              </div>
            ) : mediaItems.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-h-64 overflow-y-auto">
                {mediaItems.map((item) => (
                  <div
                    key={item.id}
                    className={`
                      cursor-pointer rounded-lg border p-2 transition-colors hover:bg-accent
                      ${selectedMedia === item.id ? 'border-primary bg-accent' : 'border-muted'}
                    `}
                    onClick={() => onSelectMedia(item.id)}
                  >
                    <div className="aspect-[2/3] bg-muted rounded mb-2 flex items-center justify-center">
                      {item.poster_url ? (
                        <img
                          src={item.poster_url}
                          alt={item.name}
                          className="w-full h-full object-cover rounded"
                        />
                      ) : (
                        <Film className="h-8 w-8 text-muted-foreground" />
                      )}
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-medium truncate" title={item.name}>
                        {item.name}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-xs">
                          {formatMediaType(item.type)}
                        </Badge>
                        {item.year && (
                          <span className="text-xs text-muted-foreground">
                            {item.year}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : selectedLibrary ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                No media items found
                {searchQuery && (
                  <span className="block mt-1">
                    Try a different search term
                  </span>
                )}
              </div>
            ) : null}
          </div>
        )}

        {/* Selected Media Info */}
        {selectedMedia && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Selected Media</label>
            {(() => {
              const media = mediaItems.find(m => m.id === selectedMedia);
              if (!media) return null;
              
              return (
                <div className="flex items-center gap-3 p-3 border rounded-lg bg-accent/50">
                  <div className="w-12 h-16 bg-muted rounded flex items-center justify-center">
                    {media.poster_url ? (
                      <img
                        src={media.poster_url}
                        alt={media.name}
                        className="w-full h-full object-cover rounded"
                      />
                    ) : (
                      <Film className="h-6 w-6 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{media.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {formatMediaType(media.type)}
                      </Badge>
                      {media.year && (
                        <span className="text-sm text-muted-foreground">
                          {media.year}
                        </span>
                      )}
                    </div>
                    {media.overview && (
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                        {media.overview}
                      </p>
                    )}
                  </div>
                </div>
              );
            })()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
