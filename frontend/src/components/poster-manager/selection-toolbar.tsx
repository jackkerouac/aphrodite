"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { X, Plus, Minus, Loader2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

interface SelectionToolbarProps {
  selectedCount: number
  selectedItems: Set<string>
  onClearSelection: () => void
  onRefreshItems: () => void
  disabled?: boolean
}

interface BulkTagResponse {
  success: boolean
  processed_count: number
  failed_items: string[]
  errors: string[]
}

export function SelectionToolbar({
  selectedCount,
  selectedItems,
  onClearSelection,
  onRefreshItems,
  disabled = false
}: SelectionToolbarProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentOperation, setCurrentOperation] = useState<string | null>(null)

  const handleBulkTagOperation = async (operation: 'add' | 'remove') => {
    if (selectedItems.size === 0) return

    setIsProcessing(true)
    setCurrentOperation(operation)

    try {
      const endpoint = operation === 'add' ? '/api/v1/poster-manager/tags/add' : '/api/v1/poster-manager/tags/remove'
      const actionText = operation === 'add' ? 'Adding' : 'Removing'
      
      toast.info(`${actionText} aphrodite-overlay tag ${operation === 'add' ? 'to' : 'from'} ${selectedItems.size} items...`)

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_ids: Array.from(selectedItems),
          tag_name: 'aphrodite-overlay'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result: BulkTagResponse = await response.json()

      if (result.success) {
        toast.success(
          `Successfully ${operation === 'add' ? 'added' : 'removed'} tag ${operation === 'add' ? 'to' : 'from'} ${result.processed_count} items`
        )
        
        // Clear selection immediately
        onClearSelection()
        
        // Force a refresh of the items to show updated badge status
        toast.info('Refreshing library to show updated badges...')
        setTimeout(async () => {
          await onRefreshItems()
          toast.success('Library refreshed - badge status updated!')
        }, 1000) // Longer delay to ensure Jellyfin processes the changes
      } else {
        toast.warning(
          `Completed with partial success: ${result.processed_count}/${selectedItems.size} items processed`
        )
        
        // Still refresh even with partial success
        onClearSelection()
        setTimeout(async () => {
          await onRefreshItems()
        }, 1000)
      }

      // Show errors if any
      if (result.errors.length > 0) {
        result.errors.forEach(error => {
          toast.error(error)
        })
      }

    } catch (error) {
      console.error('Bulk tag operation error:', error)
      toast.error(`Failed to ${operation} tag: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsProcessing(false)
      setCurrentOperation(null)
    }
  }

  if (selectedCount === 0) {
    return null
  }

  return (
    <Card className="mb-4 border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
      <CardContent className="p-4">
        <div className="flex items-center justify-between gap-4">
          {/* Selection Info */}
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="text-sm">
              {selectedCount} item{selectedCount !== 1 ? 's' : ''} selected
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearSelection}
              disabled={disabled || isProcessing}
            >
              <X className="h-4 w-4 mr-1" />
              Clear Selection
            </Button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <Button
              variant="default"
              size="sm"
              onClick={() => handleBulkTagOperation('add')}
              disabled={disabled || isProcessing}
            >
              {isProcessing && currentOperation === 'add' ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Plus className="h-4 w-4 mr-2" />
              )}
              Add Aphrodite Tag
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkTagOperation('remove')}
              disabled={disabled || isProcessing}
            >
              {isProcessing && currentOperation === 'remove' ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Minus className="h-4 w-4 mr-2" />
              )}
              Remove Aphrodite Tag
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
