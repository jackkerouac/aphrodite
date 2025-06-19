"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, Library, Tv, Film } from "lucide-react"

interface Library {
  id: string
  name: string
  type: string
  path: string[]
}

interface LibrarySelectorProps {
  libraries: Library[]
  selectedLibrary: string
  onLibraryChange: (libraryId: string) => void
  loading: boolean
}

export function LibrarySelector({ libraries, selectedLibrary, onLibraryChange, loading }: LibrarySelectorProps) {
  const getIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "movies": return <Film className="h-4 w-4" />
      case "tvshows": return <Tv className="h-4 w-4" />
      default: return <Library className="h-4 w-4" />
    }
  }

  if (loading && libraries.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-6">
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
          <span>Loading libraries...</span>
        </CardContent>
      </Card>
    )
  }

  if (libraries.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-6">
          <Library className="h-8 w-8 text-muted-foreground mb-2" />
          <p className="text-muted-foreground">No media libraries found</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Library className="h-5 w-5" />
          <span>Select Library</span>
        </CardTitle>
        <CardDescription>
          Choose a Jellyfin library to browse and manage posters
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Select value={selectedLibrary} onValueChange={onLibraryChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select a library..." />
          </SelectTrigger>
          <SelectContent>
            {libraries.map((library) => (
              <SelectItem key={library.id} value={library.id}>
                <div className="flex items-center space-x-2">
                  {getIcon(library.type)}
                  <span>{library.name}</span>
                  <Badge variant="outline">{library.type}</Badge>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </CardContent>
    </Card>
  )
}