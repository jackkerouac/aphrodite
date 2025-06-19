"use client"

import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Search, X } from "lucide-react"

interface SearchFiltersProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  badgeFilter: 'all' | 'badged' | 'original'
  onBadgeFilterChange: (filter: 'all' | 'badged' | 'original') => void
  onClearFilters: () => void
}

export function SearchFilters({
  searchQuery,
  onSearchChange,
  badgeFilter,
  onBadgeFilterChange,
  onClearFilters
}: SearchFiltersProps) {
  const hasActiveFilters = searchQuery || badgeFilter !== 'all'

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex flex-col space-y-4">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by title..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filter Controls */}
          <div className="flex flex-wrap gap-4 items-center">
            {/* Badge Status Filter */}
            <Select value={badgeFilter} onValueChange={onBadgeFilterChange}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Badge Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Items</SelectItem>
                <SelectItem value="badged">Badged Only</SelectItem>
                <SelectItem value="original">Original Only</SelectItem>
              </SelectContent>
            </Select>

            {/* Clear Filters Button */}
            {hasActiveFilters && (
              <Button variant="outline" size="sm" onClick={onClearFilters}>
                <X className="h-4 w-4 mr-2" />
                Clear
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
