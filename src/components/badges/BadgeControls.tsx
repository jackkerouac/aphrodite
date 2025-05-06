import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card.jsx";
import { Switch } from "../ui/switch.jsx";
import { Label } from "../ui/label.jsx";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select.jsx";

interface BadgeControlsProps {
  badgeSettings: any;
  toggleBadge: (badgeType: string) => void;
  updateBadgeSetting: (badgeType: string, key: string, value: any) => void;
}

export const BadgeControls = ({ 
  badgeSettings, 
  toggleBadge, 
  updateBadgeSetting 
}: BadgeControlsProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Badge Settings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Audio Badge Controls */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="audio-badge-toggle" className="font-medium">Audio Badge</Label>
            <Switch 
              id="audio-badge-toggle" 
              checked={badgeSettings.audio.enabled}
              onCheckedChange={() => toggleBadge('audio')}
            />
          </div>
          {badgeSettings.audio.enabled && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="audio-format">Format</Label>
                <Select 
                  value={badgeSettings.audio.format} 
                  onValueChange={(value) => updateBadgeSetting('audio', 'format', value)}
                >
                  <SelectTrigger id="audio-format">
                    <SelectValue placeholder="Select format" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Dolby Atmos">Dolby Atmos</SelectItem>
                    <SelectItem value="DTS-HD">DTS-HD</SelectItem>
                    <SelectItem value="Dolby Digital">Dolby Digital</SelectItem>
                    <SelectItem value="Stereo">Stereo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="audio-position">Position</Label>
                <Select 
                  value={badgeSettings.audio.position} 
                  onValueChange={(value) => updateBadgeSetting('audio', 'position', value)}
                >
                  <SelectTrigger id="audio-position">
                    <SelectValue placeholder="Select position" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="top-left">Top Left</SelectItem>
                    <SelectItem value="top-right">Top Right</SelectItem>
                    <SelectItem value="bottom-left">Bottom Left</SelectItem>
                    <SelectItem value="bottom-right">Bottom Right</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </div>

        {/* Resolution Badge Controls */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="resolution-badge-toggle" className="font-medium">Resolution Badge</Label>
            <Switch 
              id="resolution-badge-toggle" 
              checked={badgeSettings.resolution.enabled}
              onCheckedChange={() => toggleBadge('resolution')}
            />
          </div>
          {badgeSettings.resolution.enabled && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="resolution-format">Format</Label>
                <Select 
                  value={badgeSettings.resolution.format} 
                  onValueChange={(value) => updateBadgeSetting('resolution', 'format', value)}
                >
                  <SelectTrigger id="resolution-format">
                    <SelectValue placeholder="Select format" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="4K">4K</SelectItem>
                    <SelectItem value="1080p">1080p</SelectItem>
                    <SelectItem value="720p">720p</SelectItem>
                    <SelectItem value="SD">SD</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="resolution-position">Position</Label>
                <Select 
                  value={badgeSettings.resolution.position} 
                  onValueChange={(value) => updateBadgeSetting('resolution', 'position', value)}
                >
                  <SelectTrigger id="resolution-position">
                    <SelectValue placeholder="Select position" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="top-left">Top Left</SelectItem>
                    <SelectItem value="top-right">Top Right</SelectItem>
                    <SelectItem value="bottom-left">Bottom Left</SelectItem>
                    <SelectItem value="bottom-right">Bottom Right</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </div>

        {/* Review Badge Controls */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="review-badge-toggle" className="font-medium">Review Badge</Label>
            <Switch 
              id="review-badge-toggle" 
              checked={badgeSettings.review.enabled}
              onCheckedChange={() => toggleBadge('review')}
            />
          </div>
          {badgeSettings.review.enabled && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="review-source">Source</Label>
                <Select 
                  value={badgeSettings.review.source} 
                  onValueChange={(value) => updateBadgeSetting('review', 'source', value)}
                >
                  <SelectTrigger id="review-source">
                    <SelectValue placeholder="Select source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tmdb">TMDB</SelectItem>
                    <SelectItem value="imdb">IMDb</SelectItem>
                    <SelectItem value="rottentomatoes">Rotten Tomatoes</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="review-position">Position</Label>
                <Select 
                  value={badgeSettings.review.position} 
                  onValueChange={(value) => updateBadgeSetting('review', 'position', value)}
                >
                  <SelectTrigger id="review-position">
                    <SelectValue placeholder="Select position" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="top-left">Top Left</SelectItem>
                    <SelectItem value="top-right">Top Right</SelectItem>
                    <SelectItem value="bottom-left">Bottom Left</SelectItem>
                    <SelectItem value="bottom-right">Bottom Right</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
