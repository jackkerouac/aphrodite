import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import BadgeSettings from '@/components/badges/unified/BadgeSettings';
import UnifiedBadgePreview from '@/components/badges/unified/UnifiedBadgePreview';
import ThemeToggle from '@/components/badges/unified/ThemeToggle';
import useUnifiedBadgeSettings from '@/hooks/useUnifiedBadgeSettings';
import { Save, RotateCcw, Download } from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import { BadgeRenderer } from '@/components/badges/unified/BadgeRenderer';
import { UnifiedBadgeSettings } from '@/types/unifiedBadgeSettings';

/**
 * Main page component for the unified badge preview and settings
 */
const UnifiedBadgePreviewPage: React.FC = () => {
  // State for theme and debug mode
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const [debugMode, setDebugMode] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('audio');
  
  // Get badge settings from the hook
  const {
    audioBadge,
    resolutionBadge,
    reviewBadge,
    isLoading,
    isSaving,
    error,
    setAudioBadge,
    setResolutionBadge,
    setReviewBadge,
    saveSettings,
    resetSettings,
    lastSaved
  } = useUnifiedBadgeSettings({ autoSave: false });
  
  const { toast } = useToast();
  
  // Determine the active badge type based on the active tab
  const getActiveBadgeType = (): string | null => {
    switch (activeTab) {
      case 'audio':
        return audioBadge ? 'audio' : null;
      case 'resolution':
        return resolutionBadge ? 'resolution' : null;
      case 'review':
        return reviewBadge ? 'review' : null;
      default:
        return null;
    }
  };
  
  // Get all enabled badges for rendering
  const getEnabledBadges = (): UnifiedBadgeSettings[] => {
    const badges: UnifiedBadgeSettings[] = [];
    
    if (audioBadge) badges.push(audioBadge);
    if (resolutionBadge) badges.push(resolutionBadge);
    if (reviewBadge) badges.push(reviewBadge);
    
    return badges;
  };
  
  // Handler for saving settings
  const handleSave = async () => {
    try {
      await saveSettings();
      toast({
        title: 'Success',
        description: 'Badge settings saved successfully',
        variant: 'default',
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to save badge settings',
        variant: 'destructive',
      });
    }
  };
  
  // Handler for resetting settings
  const handleReset = () => {
    resetSettings();
    toast({
      title: 'Reset',
      description: 'Badge settings reset to defaults',
      variant: 'default',
    });
  };
  
  // Handler for downloading badge images
  const handleDownload = async (badgeType: 'audio' | 'resolution' | 'review') => {
    let badge: UnifiedBadgeSettings | null = null;
    
    switch (badgeType) {
      case 'audio':
        badge = audioBadge;
        break;
      case 'resolution':
        badge = resolutionBadge;
        break;
      case 'review':
        badge = reviewBadge;
        break;
    }
    
    if (!badge) {
      toast({
        title: 'Error',
        description: `${badgeType} badge is not enabled`,
        variant: 'destructive',
      });
      return;
    }
    
    // Create a temporary canvas to render the badge
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      toast({
        title: 'Error',
        description: 'Could not create canvas context',
        variant: 'destructive',
      });
      return;
    }
    
    canvas.width = 500;
    canvas.height = 500;
    
    // Create a badge renderer
    const renderer = new BadgeRenderer(ctx, 500, 500, false);
    
    // Render the badge
    const badgeCanvas = await renderer.renderBadge(badge);
    
    if (!badgeCanvas) {
      toast({
        title: 'Error',
        description: 'Failed to render badge',
        variant: 'destructive',
      });
      return;
    }
    
    // Extract the PNG data
    const pngData = BadgeRenderer.extractBadgeWithTransparency(badgeCanvas);
    
    // Create a download link
    const link = document.createElement('a');
    link.href = pngData;
    link.download = `${badge.badge_type}-badge.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast({
      title: 'Success',
      description: `${badge.badge_type} badge downloaded successfully`,
      variant: 'default',
    });
  };
  
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Badge Preview</h1>
        <p className="text-gray-500 mt-2">
          Design and customize badges for your media library
        </p>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <p>Loading badge settings...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left column: Badge settings */}
          <div className="lg:col-span-5">
            <Card>
              <CardHeader>
                <CardTitle>Badge Settings</CardTitle>
                <CardDescription>
                  Configure appearance and behavior of badges
                </CardDescription>
              </CardHeader>
              <CardContent>
                <BadgeSettings
                  audioBadge={audioBadge}
                  resolutionBadge={resolutionBadge}
                  reviewBadge={reviewBadge}
                  onAudioBadgeChange={setAudioBadge}
                  onResolutionBadgeChange={setResolutionBadge}
                  onReviewBadgeChange={setReviewBadge}
                />
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button
                  variant="outline"
                  onClick={handleReset}
                  disabled={isSaving}
                  className="flex items-center gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Reset to Defaults
                </Button>
                <Button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  {isSaving ? 'Saving...' : 'Save Settings'}
                </Button>
              </CardFooter>
            </Card>
            
            {lastSaved && (
              <p className="text-xs text-gray-500 mt-2 text-right">
                Last saved: {lastSaved.toLocaleTimeString()}
              </p>
            )}
          </div>
          
          {/* Right column: Badge preview */}
          <div className="lg:col-span-7">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Badge Preview</CardTitle>
                  <ThemeToggle
                    isDarkMode={isDarkMode}
                    onToggle={setIsDarkMode}
                  />
                </div>
                <CardDescription>
                  Preview how badges will appear on media posters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <UnifiedBadgePreview
                  badges={getEnabledBadges()}
                  activeBadgeType={getActiveBadgeType()}
                  isDarkMode={isDarkMode}
                  debugMode={debugMode}
                  className="w-full max-w-md mx-auto"
                />
              </CardContent>
              <CardFooter className="flex flex-col items-stretch gap-4">
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-500">
                    Enable badges to see them in the preview
                  </p>
                  <div className="flex items-center gap-2">
                    <label htmlFor="debug-mode" className="text-sm cursor-pointer">
                      Debug Mode
                    </label>
                    <input
                      id="debug-mode"
                      type="checkbox"
                      checked={debugMode}
                      onChange={(e) => setDebugMode(e.target.checked)}
                      className="h-4 w-4"
                    />
                  </div>
                </div>
                
                <Separator />
                
                <div className="flex flex-wrap gap-2 justify-center">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload('audio')}
                    disabled={!audioBadge}
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Download Audio Badge
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload('resolution')}
                    disabled={!resolutionBadge}
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Download Resolution Badge
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload('review')}
                    disabled={!reviewBadge}
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Download Review Badge
                  </Button>
                </div>
              </CardFooter>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedBadgePreviewPage;
