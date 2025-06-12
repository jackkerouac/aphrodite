'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Settings, RotateCcw } from 'lucide-react';
import { BadgeType } from './types';

interface BadgeConfigurationPanelProps {
  availableBadgeTypes: BadgeType[];
  selectedBadgeTypes: string[];
  onToggleBadgeType: (badgeId: string) => void;
  onGeneratePreview: () => void;
  isGenerating: boolean;
  className?: string;
}

export function BadgeConfigurationPanel({
  availableBadgeTypes,
  selectedBadgeTypes,
  onToggleBadgeType,
  onGeneratePreview,
  isGenerating,
  className = ''
}: BadgeConfigurationPanelProps) {
  
  const handleResetToDefaults = () => {
    // Reset to default selection (audio and resolution)
    const defaults = ['audio', 'resolution'];
    
    // Clear all current selections first
    selectedBadgeTypes.forEach(badgeId => {
      if (!defaults.includes(badgeId)) {
        onToggleBadgeType(badgeId);
      }
    });
    
    // Then ensure defaults are selected
    defaults.forEach(badgeId => {
      if (!selectedBadgeTypes.includes(badgeId)) {
        onToggleBadgeType(badgeId);
      }
    });
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Badge Configuration
        </CardTitle>
        <CardDescription>
          Select which badges to apply to the preview poster. Aphrodite will use an example poster to demonstrate how badges look.
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Badge Types Selection */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">Badge Types</h4>
            <Badge variant="secondary" className="text-xs">
              {selectedBadgeTypes.length} selected
            </Badge>
          </div>
          
          <div className="space-y-3">
            {availableBadgeTypes.map((badgeType) => (
              <div key={badgeType.id} className="flex items-start space-x-3">
                <Checkbox
                  id={`badge-${badgeType.id}`}
                  checked={selectedBadgeTypes.includes(badgeType.id)}
                  onCheckedChange={() => onToggleBadgeType(badgeType.id)}
                  className="mt-0.5"
                />
                <div className="grid gap-1.5 leading-none">
                  <label
                    htmlFor={`badge-${badgeType.id}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {badgeType.name}
                  </label>
                  <p className="text-xs text-muted-foreground">
                    {badgeType.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button 
            onClick={onGeneratePreview}
            disabled={isGenerating || selectedBadgeTypes.length === 0}
            className="w-full"
            size="lg"
          >
            {isGenerating ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                Generating Preview...
              </>
            ) : (
              'Generate Preview'
            )}
          </Button>

          <Button
            variant="outline"
            onClick={handleResetToDefaults}
            disabled={isGenerating}
            className="w-full"
            size="sm"
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset to Defaults
          </Button>
        </div>

        {/* Help Text */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p>• Preview uses realistic demo data for consistent results</p>
          <p>• All badge settings from Settings page are applied</p>
          <p>• Select at least one badge type to generate preview</p>
        </div>
      </CardContent>
    </Card>
  );
}
