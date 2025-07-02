/**
 * Poster Replacement Modal
 * 
 * Modal for bulk poster replacement with language selection and progress tracking
 */

import React, { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { CheckCircle, XCircle, AlertCircle, Loader2, Image, Clock } from "lucide-react"
import { LanguageSelector } from "@/components/ui/language-selector"
import { toast } from "sonner"

interface MediaItem {
  id: string
  title: string
  poster_url?: string
}

interface BulkItemResult {
  item_id: string
  jellyfin_id: string
  success: boolean
  message: string
  new_poster_url?: string
  selected_poster?: {
    source: string
    url: string
  }
  error_details?: string
}

interface BulkReplacePosterResponse {
  success: boolean
  message: string
  processed_count: number
  successful_replacements: number
  failed_replacements: number
  processing_results: BulkItemResult[]
  processing_time: number
}

interface PosterReplacementModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  selectedItems: MediaItem[]
  onSuccess: () => void
}

export const PosterReplacementModal: React.FC<PosterReplacementModalProps> = ({
  open,
  onOpenChange,
  selectedItems,
  onSuccess
}) => {
  const [language, setLanguage] = useState("en")
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState<BulkReplacePosterResponse | null>(null)
  const [currentStep, setCurrentStep] = useState<'setup' | 'processing' | 'results'>('setup')

  const handleStartReplacement = async () => {
    setIsProcessing(true)
    setCurrentStep('processing')
    
    try {
      const response = await fetch('/api/v1/poster-replacement/bulk-replace-posters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_ids: selectedItems.map(item => item.id),
          jellyfin_ids: selectedItems.map(item => item.id), // Assuming item.id is jellyfin_id
          language_preference: language,
          random_selection: true
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to replace posters')
      }

      const result: BulkReplacePosterResponse = await response.json()
      setResults(result)
      setCurrentStep('results')
      
      // Show toast notification
      if (result.successful_replacements > 0) {
        toast.success(`Successfully replaced ${result.successful_replacements} poster${result.successful_replacements !== 1 ? 's' : ''}`)
        onSuccess() // Trigger grid refresh
      }
      
    } catch (error) {
      console.error('Error replacing posters:', error)
      toast.error(error instanceof Error ? error.message : "Failed to replace posters")
      setCurrentStep('setup')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleClose = () => {
    if (!isProcessing) {
      onOpenChange(false)
      // Reset state after modal closes
      setTimeout(() => {
        setCurrentStep('setup')
        setResults(null)
        setLanguage('en')
      }, 300)
    }
  }

  const renderSetupStep = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center space-x-2">
          <Image className="h-5 w-5 text-blue-600" />
          <span className="text-lg font-medium">Replace {selectedItems.length} Poster{selectedItems.length !== 1 ? 's' : ''}</span>
        </div>
        <p className="text-sm text-muted-foreground">
          This will replace the selected posters with random alternatives from external sources
        </p>
      </div>

      <Separator />

      <LanguageSelector
        value={language}
        onValueChange={setLanguage}
        label="Poster Language Preference"
      />

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Note</AlertTitle>
        <AlertDescription>
          Current posters will be backed up and the "aphrodite-overlay" tag will be removed from replaced items.
        </AlertDescription>
      </Alert>

      <div className="flex space-x-3">
        <Button
          onClick={handleStartReplacement}
          className="flex-1"
          disabled={isProcessing}
        >
          <Image className="h-4 w-4 mr-2" />
          Start Replacement
        </Button>
        <Button
          variant="outline"
          onClick={handleClose}
          disabled={isProcessing}
        >
          Cancel
        </Button>
      </div>
    </div>
  )

  const renderProcessingStep = () => (
    <div className="space-y-6 text-center">
      <div className="space-y-2">
        <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <h3 className="text-lg font-medium">Replacing Posters...</h3>
        <p className="text-sm text-muted-foreground">
          Processing {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''}. This may take a moment.
        </p>
      </div>
      
      <Progress value={66} className="w-full" />
      
      <div className="text-xs text-muted-foreground">
        Searching for alternatives and updating posters...
      </div>
    </div>
  )

  const renderResultsStep = () => {
    if (!results) return null

    const hasFailures = results.failed_replacements > 0
    const successRate = Math.round((results.successful_replacements / results.processed_count) * 100)

    return (
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center space-x-2">
            {results.successful_replacements > 0 ? (
              <CheckCircle className="h-6 w-6 text-green-600" />
            ) : (
              <XCircle className="h-6 w-6 text-red-600" />
            )}
            <h3 className="text-lg font-medium">
              {results.successful_replacements > 0 ? 'Replacement Complete' : 'Replacement Failed'}
            </h3>
          </div>
          <p className="text-sm text-muted-foreground">
            {results.message}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{results.successful_replacements}</div>
            <div className="text-sm text-green-700">Successful</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{results.failed_replacements}</div>
            <div className="text-sm text-red-700">Failed</div>
          </div>
        </div>

        <div className="flex items-center justify-center space-x-4 text-xs text-muted-foreground">
          <div className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>{results.processing_time.toFixed(1)}s</span>
          </div>
          <div>
            {successRate}% success rate
          </div>
        </div>

        {hasFailures && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Some items failed</AlertTitle>
            <AlertDescription>
              {results.failed_replacements} item{results.failed_replacements !== 1 ? 's' : ''} could not be processed. 
              This may be due to missing metadata or unavailable poster sources.
            </AlertDescription>
          </Alert>
        )}

        <Button
          onClick={handleClose}
          className="w-full"
        >
          Close
        </Button>
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            Bulk Poster Replacement
          </DialogTitle>
          <DialogDescription>
            Replace multiple posters with alternatives from external sources
          </DialogDescription>
        </DialogHeader>
        
        {currentStep === 'setup' && renderSetupStep()}
        {currentStep === 'processing' && renderProcessingStep()}
        {currentStep === 'results' && renderResultsStep()}
      </DialogContent>
    </Dialog>
  )
}
