"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"

interface BadgeSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  onApply: (selectedBadges: string[]) => Promise<void>
  isLoading: boolean
}

const AVAILABLE_BADGES = [
  {
    id: "audio",
    name: "Audio Codec",
    description: "DTS-HD MA, Atmos, Dolby Digital Plus, etc."
  },
  {
    id: "resolution", 
    name: "Resolution",
    description: "4K, 1080p, HDR, Dolby Vision, etc."
  },
  {
    id: "review",
    name: "Reviews & Ratings", 
    description: "IMDb, TMDb, Rotten Tomatoes, Metacritic"
  },
  {
    id: "awards",
    name: "Awards",
    description: "Oscars, Emmys, Golden Globes, etc."
  }
]

export function BadgeSelectionModal({
  isOpen,
  onClose,
  onApply,
  isLoading
}: BadgeSelectionModalProps) {
  const [selectedBadges, setSelectedBadges] = useState<string[]>([])

  const handleBadgeToggle = (badgeId: string) => {
    setSelectedBadges(prev => 
      prev.includes(badgeId)
        ? prev.filter(id => id !== badgeId)
        : [...prev, badgeId]
    )
  }

  const handleSelectAll = () => {
    setSelectedBadges(AVAILABLE_BADGES.map(badge => badge.id))
  }

  const handleSelectNone = () => {
    setSelectedBadges([])
  }

  const handleApply = async () => {
    if (selectedBadges.length === 0) {
      toast.error("Please select at least one badge type")
      return
    }

    try {
      await onApply(selectedBadges)
      setSelectedBadges([]) // Reset selection
    } catch (error) {
      // Error handling is done in parent component
    }
  }

  const handleClose = () => {
    if (!isLoading) {
      setSelectedBadges([])
      onClose()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Select Badges to Apply</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Choose which badge types to apply to this poster:
          </p>

          {/* Quick Actions */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
              disabled={isLoading}
            >
              Select All
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectNone}
              disabled={isLoading}
            >
              Select None
            </Button>
          </div>

          <Separator />

          {/* Badge Selection */}
          <div className="space-y-3">
            {AVAILABLE_BADGES.map((badge) => (
              <div key={badge.id} className="flex items-start space-x-3">
                <Checkbox
                  id={badge.id}
                  checked={selectedBadges.includes(badge.id)}
                  onCheckedChange={() => handleBadgeToggle(badge.id)}
                  disabled={isLoading}
                />
                <div className="grid gap-1.5 leading-none">
                  <Label
                    htmlFor={badge.id}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    {badge.name}
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    {badge.description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <Separator />

          {/* Action Buttons */}
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleApply}
              disabled={isLoading || selectedBadges.length === 0}
            >
              {isLoading ? "Applying..." : `Apply ${selectedBadges.length} Badge${selectedBadges.length !== 1 ? 's' : ''}`}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
