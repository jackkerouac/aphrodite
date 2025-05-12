import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Sun, Moon, Download, Eye, EyeOff } from 'lucide-react';

interface PreviewControlsProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
  visibleBadges: string[];
  onToggleBadgeVisibility: (badgeType: string) => void;
  onDownload?: () => void;
  className?: string;
}

/**
 * Component for displaying preview controls (theme toggle, badge visibility, etc.)
 */
export const PreviewControls: React.FC<PreviewControlsProps> = ({
  theme,
  onThemeToggle,
  visibleBadges,
  onToggleBadgeVisibility,
  onDownload,
  className = ''
}) => {
  const isAudioVisible = visibleBadges.includes('audio');
  const isResolutionVisible = visibleBadges.includes('resolution');
  const isReviewVisible = visibleBadges.includes('review');

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle>Preview Controls</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Theme Toggle */}
        <div className="flex items-center justify-between">
          <Label htmlFor="theme-toggle" className="font-medium">
            Poster Theme
          </Label>
          <Button
            variant="outline"
            size="icon"
            onClick={onThemeToggle}
            title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
          >
            {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </Button>
        </div>
        
        <Separator />
        
        {/* Badge Visibility Toggles */}
        <div className="space-y-3">
          <Label className="font-medium">Badge Visibility</Label>
          
          <div className="grid gap-2">
            {/* Audio Badge Toggle */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`p-1 rounded ${isAudioVisible ? 'text-primary' : 'text-muted-foreground'}`}>
                  {isAudioVisible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </div>
                <Label htmlFor="audio-visible" className="cursor-pointer">
                  Audio Badge
                </Label>
              </div>
              <Switch
                id="audio-visible"
                checked={isAudioVisible}
                onCheckedChange={() => onToggleBadgeVisibility('audio')}
              />
            </div>
            
            {/* Resolution Badge Toggle */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`p-1 rounded ${isResolutionVisible ? 'text-primary' : 'text-muted-foreground'}`}>
                  {isResolutionVisible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </div>
                <Label htmlFor="resolution-visible" className="cursor-pointer">
                  Resolution Badge
                </Label>
              </div>
              <Switch
                id="resolution-visible"
                checked={isResolutionVisible}
                onCheckedChange={() => onToggleBadgeVisibility('resolution')}
              />
            </div>
            
            {/* Review Badge Toggle */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`p-1 rounded ${isReviewVisible ? 'text-primary' : 'text-muted-foreground'}`}>
                  {isReviewVisible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </div>
                <Label htmlFor="review-visible" className="cursor-pointer">
                  Review Badge
                </Label>
              </div>
              <Switch
                id="review-visible"
                checked={isReviewVisible}
                onCheckedChange={() => onToggleBadgeVisibility('review')}
              />
            </div>
          </div>
        </div>
        
        {/* Download Button */}
        {onDownload && (
          <>
            <Separator />
            <Button 
              variant="default" 
              className="w-full" 
              onClick={onDownload}
              disabled={visibleBadges.length === 0}
            >
              <Download className="mr-2 h-4 w-4" /> Download Badge
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default PreviewControls;
