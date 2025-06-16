"use client"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"

interface SelectionCounterProps {
  totalItems: number
  selectedCount: number
  allSelected: boolean
  onSelectAll: () => void
  onSelectNone: () => void
  onToggleSelectionMode: () => void
  selectionMode: boolean
}

export function SelectionCounter({
  totalItems,
  selectedCount,
  allSelected,
  onSelectAll,
  onSelectNone,
  onToggleSelectionMode,
  selectionMode
}: SelectionCounterProps) {
  if (!selectionMode) {
    return (
      <div className="flex items-center justify-between">
        <Badge variant="outline" className="text-sm">
          {totalItems} item{totalItems !== 1 ? 's' : ''} total
        </Badge>
        <Button
          variant="outline"
          size="sm"
          onClick={onToggleSelectionMode}
        >
          Select Items
        </Button>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex items-center space-x-2">
          <Checkbox
            checked={allSelected}
            onCheckedChange={(checked) => {
              if (checked) {
                onSelectAll()
              } else {
                onSelectNone()
              }
            }}
            className={selectedCount > 0 && !allSelected ? 'data-[state=indeterminate]:bg-primary' : ''}
          />
          <label className="text-sm font-medium">
            Select All
          </label>
        </div>
        
        <Badge variant="secondary" className="text-sm">
          {selectedCount} of {totalItems} selected
        </Badge>
      </div>
      
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleSelectionMode}
      >
        Cancel Selection
      </Button>
    </div>
  )
}
