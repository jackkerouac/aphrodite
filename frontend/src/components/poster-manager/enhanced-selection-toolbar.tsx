/**
 * Enhanced Selection Toolbar with Workflow Integration
 * 
 * Integrates 1 vs 2+ poster processing decision logic
 */

import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { X, Zap, Users, Settings, Download, Trash2 } from "lucide-react"
import { ProcessingDecision, BatchJobCreator } from '@/components/workflow'
import { useNotifications } from '@/components/workflow'
import { useRouter } from 'next/navigation'

interface MediaItem {
  id: string
  title: string
  poster_url?: string
}

interface EnhancedSelectionToolbarProps {
  selectedCount: number
  selectedItems: Set<string>
  allItems: MediaItem[]
  onClearSelection: () => void
  onRefreshItems: () => Promise<void>
  disabled?: boolean
}

export const EnhancedSelectionToolbar: React.FC<EnhancedSelectionToolbarProps> = ({
  selectedCount,
  selectedItems,
  allItems,
  onClearSelection,
  onRefreshItems,
  disabled = false
}) => {
  const [showBatchCreator, setShowBatchCreator] = useState(false)
  const { showJobCreated } = useNotifications()
  const router = useRouter()

  // Get selected poster objects
  const selectedPosters = allItems.filter(item => selectedItems.has(item.id))

  const handleImmediateProcess = (poster: MediaItem) => {
    // Navigate to existing preview page for single poster
    router.push(`/preview?posterId=${poster.id}`)
  }

  const handleBatchProcess = () => {
    setShowBatchCreator(true)
  }

  const handleJobCreated = (jobId: string) => {
    showJobCreated(`Batch Job Created`, selectedCount)
    setShowBatchCreator(false)
    onClearSelection()
    
    // Optional: Switch to Jobs tab to show the new job
    // This could be implemented as a callback prop
  }

  if (selectedCount === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      {/* Selection Summary */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CardTitle className="text-lg">
                {selectedCount} poster{selectedCount !== 1 ? 's' : ''} selected
              </CardTitle>
              <Badge variant="secondary">{selectedCount}</Badge>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onClearSelection}
              disabled={disabled}
            >
              <X className="h-4 w-4 mr-2" />
              Clear Selection
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Processing Decision */}
          <ProcessingDecision
            selectedPosters={selectedPosters}
            onImmediateProcess={handleImmediateProcess}
            onBatchProcess={handleBatchProcess}
          />

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {selectedCount === 1 ? (
              <Button
                onClick={() => handleImmediateProcess(selectedPosters[0])}
                disabled={disabled}
                className="flex-1"
              >
                <Zap className="h-4 w-4 mr-2" />
                Generate Preview
              </Button>
            ) : (
              <Button
                onClick={handleBatchProcess}
                disabled={disabled}
                className="flex-1"
              >
                <Users className="h-4 w-4 mr-2" />
                Create Batch Job
              </Button>
            )}

            <Separator orientation="vertical" className="h-8" />

            {/* Additional Actions */}
            <Button variant="outline" size="sm" disabled={disabled}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            
            <Button variant="outline" size="sm" disabled={disabled}>
              <Settings className="h-4 w-4 mr-2" />
              Bulk Edit
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Batch Job Creator Modal */}
      {showBatchCreator && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="max-w-2xl w-full">
            <BatchJobCreator
              selectedPosters={selectedPosters}
              onJobCreated={handleJobCreated}
              onCancel={() => setShowBatchCreator(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}
