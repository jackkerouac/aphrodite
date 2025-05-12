import React, { useState, useEffect, useCallback } from 'react';
import { useUnifiedBadgeSettings } from '@/hooks/useUnifiedBadgeSettings';
import { usePreviewState } from '@/hooks/usePreviewState';
import { UnifiedBadgePreview } from '@/components/badges/unified/UnifiedBadgePreview';
import { BadgeSettingsPanel } from './components/BadgeSettingsPanel';
import { PreviewControls } from './components/PreviewControls';
import { UnsavedChangesAlert } from './components/UnsavedChangesAlert';
import { BadgeRenderer } from '@/components/badges/unified/BadgeRenderer';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Save, 
  Undo, 
  Download, 
  AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';

/**
 * Main Preview Page component for managing and previewing badge settings
 */
export default function PreviewPage() {
  // Get badge settings from the hooks
  const {
    audioBadge,
    resolutionBadge,
    reviewBadge,
    setAudioBadge,
    setResolutionBadge,
    setReviewBadge,
    saveSettings,
    resetSettings,
    isLoading,
    isSaving,
    lastSaved
  } = useUnifiedBadgeSettings();

  // Get preview state from the hook
  const {
    theme,
    toggleTheme,
    visibleBadges,
    toggleBadgeVisibility,
    highlightedBadge,
    setHighlightedBadge
  } = usePreviewState();

  // Track if there are unsaved changes
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showUnsavedAlert, setShowUnsavedAlert] = useState(false);
  const [pendingAction, setPendingAction] = useState<() => void | null>(() => null);

  // Track the last time settings were saved
  const [saveTimeDisplay, setSaveTimeDisplay] = useState<string>('');

  // Function to download the current badge
  const handleDownload = useCallback(async () => {
    try {
      // Create a temporary canvas
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        throw new Error('Could not get canvas context');
      }

      // Set canvas dimensions
      canvas.width = 600;
      canvas.height = 600;

      // Create a badge renderer
      const renderer = new BadgeRenderer(ctx, canvas.width, canvas.height);

      // Determine which badge to download based on highlighted badge
      let badgeToDownload = null;
      if (highlightedBadge === 'audio' && audioBadge) {
        badgeToDownload = audioBadge;
      } else if (highlightedBadge === 'resolution' && resolutionBadge) {
        badgeToDownload = resolutionBadge;
      } else if (highlightedBadge === 'review' && reviewBadge) {
        badgeToDownload = reviewBadge;
      } else {
        // If no badge is highlighted, use the first visible badge
        if (visibleBadges.includes('audio') && audioBadge) {
          badgeToDownload = audioBadge;
        } else if (visibleBadges.includes('resolution') && resolutionBadge) {
          badgeToDownload = resolutionBadge;
        } else if (visibleBadges.includes('review') && reviewBadge) {
          badgeToDownload = reviewBadge;
        }
      }

      if (!badgeToDownload) {
        throw new Error('No badge selected for download');
      }

      // Render just the badge (with transparent background) to the canvas
      const badgeImage = await renderer.renderSingleBadge(badgeToDownload);

      // Create download link
      const link = document.createElement('a');
      link.download = `${badgeToDownload.badge_type}-badge.png`;
      link.href = badgeImage;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success('Badge downloaded successfully');
    } catch (error) {
      console.error('Error downloading badge:', error);
      toast.error('Failed to download badge');
    }
  }, [audioBadge, resolutionBadge, reviewBadge, highlightedBadge, visibleBadges]);

  // Handle saving settings
  const handleSave = useCallback(async () => {
    try {
      await saveSettings();
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  }, [saveSettings]);

  // Handle discarding changes
  const handleReset = useCallback(() => {
    if (hasUnsavedChanges) {
      setShowUnsavedAlert(true);
      setPendingAction(() => () => {
        resetSettings();
        setHasUnsavedChanges(false);
        toast.info('Changes discarded');
      });
    } else {
      resetSettings();
      toast.info('Settings reset to defaults');
    }
  }, [hasUnsavedChanges, resetSettings]);

  // Handle tab change to highlight the active badge
  const handleTabChange = useCallback((tab: string) => {
    setHighlightedBadge(tab);
  }, [setHighlightedBadge]);

  // Format the last saved time
  useEffect(() => {
    if (lastSaved) {
      const now = new Date();
      const diff = now.getTime() - lastSaved.getTime();
      
      if (diff < 60000) { // Less than a minute
        setSaveTimeDisplay('just now');
      } else if (diff < 3600000) { // Less than an hour
        const minutes = Math.floor(diff / 60000);
        setSaveTimeDisplay(`${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`);
      } else {
        const hours = Math.floor(diff / 3600000);
        setSaveTimeDisplay(`${hours} ${hours === 1 ? 'hour' : 'hours'} ago`);
      }
    } else {
      setSaveTimeDisplay('never');
    }
  }, [lastSaved]);

  // Update the unsaved changes state when settings change
  useEffect(() => {
    setHasUnsavedChanges(true);
  }, [audioBadge, resolutionBadge, reviewBadge]);

  // Filter visible badges for the preview
  const visibleBadgesForPreview = [
    audioBadge && visibleBadges.includes('audio') ? audioBadge : null,
    resolutionBadge && visibleBadges.includes('resolution') ? resolutionBadge : null,
    reviewBadge && visibleBadges.includes('review') ? reviewBadge : null,
  ].filter(Boolean);

  // Handle window beforeunload event for unsaved changes warning
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        return (e.returnValue = 'You have unsaved changes. Are you sure you want to leave?');
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedChanges]);

  return (
    <div className="container mx-auto py-6 px-4 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Badge Preview</h1>
          <p className="text-muted-foreground">
            Design and customize badges for your media collection
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {hasUnsavedChanges && (
            <Badge variant="outline" className="bg-yellow-100 dark:bg-yellow-900 border-yellow-300 dark:border-yellow-700 text-yellow-800 dark:text-yellow-300 flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              Unsaved Changes
            </Badge>
          )}
          
          <Button 
            variant="outline" 
            onClick={handleReset}
            disabled={isLoading}
          >
            <Undo className="mr-2 h-4 w-4" /> Reset
          </Button>
          
          <Button 
            onClick={handleSave}
            disabled={isLoading || isSaving || !hasUnsavedChanges}
          >
            <Save className="mr-2 h-4 w-4" /> Save
          </Button>
        </div>
      </div>

      {lastSaved && (
        <div className="text-sm text-muted-foreground">
          Last saved: {saveTimeDisplay}
        </div>
      )}
      
      <Separator className="my-6" />

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Settings Panel - Left Side */}
        <div className="lg:col-span-5 space-y-6">
          <BadgeSettingsPanel 
            audioBadge={audioBadge}
            resolutionBadge={resolutionBadge}
            reviewBadge={reviewBadge}
            onAudioBadgeChange={setAudioBadge}
            onResolutionBadgeChange={setResolutionBadge}
            onReviewBadgeChange={setReviewBadge}
            activeTab={highlightedBadge || undefined}
            onTabChange={handleTabChange}
          />
          
          <PreviewControls 
            theme={theme}
            onThemeToggle={toggleTheme}
            visibleBadges={visibleBadges}
            onToggleBadgeVisibility={toggleBadgeVisibility}
            onDownload={handleDownload}
          />
        </div>
        
        {/* Preview Area - Right Side */}
        <div className="lg:col-span-7">
          <Card className="p-6 flex items-center justify-center bg-muted/40">
            <div className="w-full max-w-md">
              <UnifiedBadgePreview 
                badges={visibleBadgesForPreview}
                activeBadgeType={highlightedBadge}
                isDarkMode={theme === 'dark'}
                className="w-full"
              />
              
              <div className="mt-4 text-center text-sm text-muted-foreground">
                Preview poster with applied badges
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Unsaved Changes Alert */}
      <UnsavedChangesAlert 
        isOpen={showUnsavedAlert}
        onCancel={() => {
          setShowUnsavedAlert(false);
          handleSave();
        }}
        onContinue={() => {
          setShowUnsavedAlert(false);
          if (pendingAction) {
            pendingAction();
          }
        }}
      />
    </div>
  );
}
