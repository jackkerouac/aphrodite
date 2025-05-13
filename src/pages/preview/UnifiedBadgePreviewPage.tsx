import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useUnifiedBadgeSettings } from '@/hooks';
import { usePreviewState, BadgeType } from '@/hooks';
import UnifiedBadgePreview from '@/components/badges/unified/UnifiedBadgePreview';
import { BadgeSettingsPanel } from './components/BadgeSettingsPanel';
import { PreviewControls } from './components/PreviewControls';
import { UnsavedChangesAlert } from './components/UnsavedChangesAlert';
import { BadgeRenderer } from '@/components/badges/unified/BadgeRenderer';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Save, 
  Undo, 
  AlertTriangle,
  Loader2,
  Info
} from 'lucide-react';
import { toast } from 'sonner';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { UnifiedBadgeSettings, AudioBadgeSettings } from '@/types/unifiedBadgeSettings';
import { badgeSettingsApi } from '@/api/badgeSettingsApi';

/**
 * Main Preview Page component for managing and previewing badge settings
 */
export default function UnifiedBadgePreviewPage() {
  // Get badge settings from the refactored hook
  const {
    audioBadge,
    resolutionBadge,
    reviewBadge,
    updateAudioBadge,
    updateResolutionBadge,
    updateReviewBadge,
    saveAllBadges,
    resetAllBadges,
    isLoading,
    isSaving,
    hasUnsavedChanges,
    lastSaved,
    error
  } = useUnifiedBadgeSettings({ autoSave: false });

  // Get preview state from the refactored hook
  const {
    theme,
    toggleTheme,
    visibleBadges,
    toggleBadgeVisibility,
    highlightedBadge,
    setHighlightedBadge
  } = usePreviewState();

  // State for unsaved changes alert
  const [showUnsavedAlert, setShowUnsavedAlert] = useState(false);
  const [pendingAction, setPendingAction] = useState<() => void>(() => () => {});

  // Display for last saved time
  const [saveTimeDisplay, setSaveTimeDisplay] = useState<string>('');

  // State to store the direct database badge settings
  const [directDbAudioSize, setDirectDbAudioSize] = useState<number | null>(null);
  const [directDbResolutionSize, setDirectDbResolutionSize] = useState<number | null>(null);
  const [directDbReviewSize, setDirectDbReviewSize] = useState<number | null>(null);
  
  // State to store complete badge settings
  const [directDbAudioSettings, setDirectDbAudioSettings] = useState<AudioBadgeSettings | null>(null);
  const [directDbResolutionSettings, setDirectDbResolutionSettings] = useState<ResolutionBadgeSettings | null>(null);
  const [directDbReviewSettings, setDirectDbReviewSettings] = useState<ReviewBadgeSettings | null>(null);
  
  // Fetch the direct database settings for all badge types
  useEffect(() => {
    const fetchDirectSettings = async () => {
      try {
        // Make direct fetches to the API endpoints for all badge types
        const fetchBadgeSettings = async (badgeType: string) => {
          try {
            const response = await fetch(`http://localhost:5000/api/v1/unified-badge-settings/${badgeType}?user_id=1`);
            const data = await response.json();
            
            console.log(`DIRECT DB QUERY - Raw response for ${badgeType}:`, data);
            
            // Extract the badge settings based on the response structure
            let badgeSettings;
            if (data.success && data.data) {
              badgeSettings = data.data;
            } else if (data.badge_type === badgeType) {
              badgeSettings = data;
            } else {
              console.error(`DIRECT DB QUERY - Could not find valid settings in ${badgeType} response`);
              return null;
            }
            
            console.log(`DIRECT DB QUERY - ${badgeType} badge settings from database:`, badgeSettings);
            return badgeSettings;
          } catch (error) {
            console.error(`Error querying ${badgeType} badge directly:`, error);
            return null;
          }
        };

        // Fetch settings for all badge types in parallel
        const [audioSettings, resolutionSettings, reviewSettings] = await Promise.all([
          fetchBadgeSettings('audio'),
          fetchBadgeSettings('resolution'),
          fetchBadgeSettings('review')
        ]);
        
        // Set the state for each badge type
        if (audioSettings !== null) {
          setDirectDbAudioSize(audioSettings.badge_size);
          setDirectDbAudioSettings(audioSettings);
        }
        if (resolutionSettings !== null) {
          setDirectDbResolutionSize(resolutionSettings.badge_size);
          setDirectDbResolutionSettings(resolutionSettings);
        }
        if (reviewSettings !== null) {
          setDirectDbReviewSize(reviewSettings.badge_size);
          setDirectDbReviewSettings(reviewSettings);
        }
      } catch (error) {
        console.error('Error querying database directly:', error);
      }
    };
    
    fetchDirectSettings();
  }, []);

  // State to track whether initial syncing has happened for each badge type
  const [initialAudioSyncDone, setInitialAudioSyncDone] = useState(false);
  const [initialResolutionSyncDone, setInitialResolutionSyncDone] = useState(false);
  const [initialReviewSyncDone, setInitialReviewSyncDone] = useState(false);
  
  // Effect to update badges when direct DB sizes change, but only once at the beginning for each badge type
  
  // Audio badge sync
  useEffect(() => {
    if (directDbAudioSettings && audioBadge && !initialAudioSyncDone) {
      // Only sync the database settings once when it's first loaded
      console.log(`Initial sync: Database audio badge settings synced to local state:`, directDbAudioSettings);
      
      // Update with all properties from database settings
      updateAudioBadge(directDbAudioSettings);
      
      setInitialAudioSyncDone(true);
    }
  }, [directDbAudioSettings, audioBadge, updateAudioBadge, initialAudioSyncDone]);
  
  // Resolution badge sync
  useEffect(() => {
    if (directDbResolutionSettings && resolutionBadge && !initialResolutionSyncDone) {
      // Only sync the database settings once when it's first loaded
      console.log(`Initial sync: Database resolution badge settings synced to local state:`, directDbResolutionSettings);
      
      // Update with all properties from database settings
      updateResolutionBadge(directDbResolutionSettings);
      
      setInitialResolutionSyncDone(true);
    }
  }, [directDbResolutionSettings, resolutionBadge, updateResolutionBadge, initialResolutionSyncDone]);
  
  // Review badge sync
  useEffect(() => {
    if (directDbReviewSettings && reviewBadge && !initialReviewSyncDone) {
      // Only sync the database settings once when it's first loaded
      console.log(`Initial sync: Database review badge settings synced to local state:`, directDbReviewSettings);
      
      // Update with all properties from database settings
      updateReviewBadge(directDbReviewSettings);
      
      setInitialReviewSyncDone(true);
    }
  }, [directDbReviewSettings, reviewBadge, updateReviewBadge, initialReviewSyncDone]);

  // Create wrappers for updating badge settings that handle all updates correctly
  const handleAudioBadgeChange = useCallback((settings: Partial<AudioBadgeSettings>) => {
    // For any update, just update directly without overriding with database values
    console.log(`Audio badge update: `, settings);
    updateAudioBadge(settings);
  }, [updateAudioBadge]);
  
  // Wrappers for resolution and review badges to ensure consistent behavior
  const handleResolutionBadgeChange = useCallback((settings: Partial<AudioBadgeSettings>) => {
    console.log(`Resolution badge update: `, settings);
    updateResolutionBadge(settings);
  }, [updateResolutionBadge]);
  
  const handleReviewBadgeChange = useCallback((settings: Partial<AudioBadgeSettings>) => {
    console.log(`Review badge update: `, settings);
    updateReviewBadge(settings);
  }, [updateReviewBadge]);

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
      let badgeToDownload: UnifiedBadgeSettings | null = null;
      
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
      console.log(`Saving settings with audio badge size: ${audioBadge?.badge_size}`);
      await saveAllBadges();
      toast.success('All badge settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save badge settings');
    }
  }, [saveAllBadges, audioBadge]);

  // Handle discarding changes
  const handleReset = useCallback(() => {
    if (hasUnsavedChanges) {
      setShowUnsavedAlert(true);
      setPendingAction(() => () => {
        resetAllBadges();
        toast.info('Changes discarded');
      });
    } else {
      resetAllBadges();
      toast.info('Settings reset to defaults');
    }
  }, [hasUnsavedChanges, resetAllBadges]);

  // Handle tab change to highlight the active badge
  const handleTabChange = useCallback((tab: string) => {
    setHighlightedBadge(tab as BadgeType);
  }, [setHighlightedBadge]);

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

  // Handle errors
  useEffect(() => {
    if (error) {
      toast.error(`Error: ${error.message}`);
    }
  }, [error]);

  // Filter visible badges for the preview
  const visibleBadgesForPreview = [
    audioBadge && visibleBadges.includes('audio') ? audioBadge : null,
    resolutionBadge && visibleBadges.includes('resolution') ? resolutionBadge : null,
    reviewBadge && visibleBadges.includes('review') ? reviewBadge : null,
  ].filter(Boolean) as UnifiedBadgeSettings[];

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
            disabled={isLoading || isSaving}
          >
            <Undo className="mr-2 h-4 w-4" /> Reset
          </Button>
          
          <Button 
            onClick={handleSave}
            disabled={isLoading || isSaving || !hasUnsavedChanges}
          >
            {isSaving ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            Save
          </Button>
        </div>
      </div>

      {lastSaved && (
        <div className="text-sm text-muted-foreground">
          Last saved: {saveTimeDisplay}
        </div>
      )}
      
      <Separator className="my-6" />

      {/* Loading State */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
          <p className="text-lg text-muted-foreground">Loading badge settings...</p>
        </div>
      ) : (
        /* Main Content */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Settings Panel - Left Side */}
          <div className="lg:col-span-5 space-y-6">
            
            <BadgeSettingsPanel 
              audioBadge={audioBadge}
              resolutionBadge={resolutionBadge}
              reviewBadge={reviewBadge}
              onAudioBadgeChange={handleAudioBadgeChange}
              onResolutionBadgeChange={handleResolutionBadgeChange}
              onReviewBadgeChange={handleReviewBadgeChange}
              activeTab={highlightedBadge || undefined}
              onTabChange={handleTabChange}
              disabled={isSaving}
            />
            
            <PreviewControls 
              theme={theme}
              onThemeToggle={toggleTheme}
              visibleBadges={visibleBadges}
              onToggleBadgeVisibility={toggleBadgeVisibility}
              onDownload={handleDownload}
              disabled={isSaving}
            />
          </div>
          
          {/* Preview Area - Right Side */}
          <div className="lg:col-span-7">
            <Card className="p-6 flex items-center justify-center bg-muted/40">
              <div className="w-full max-w-md">
                
                {/* The preview component uses our fixed badges */}
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
      )}

      {/* Unsaved Changes Alert */}
      <UnsavedChangesAlert 
        isOpen={showUnsavedAlert}
        onCancel={() => {
          setShowUnsavedAlert(false);
        }}
        onContinue={() => {
          setShowUnsavedAlert(false);
          pendingAction();
        }}
      />
    </div>
  );
}