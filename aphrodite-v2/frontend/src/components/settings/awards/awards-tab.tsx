'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Star, Trophy } from 'lucide-react';
import { AwardsSettings, colorSchemes, awardSources } from './types';

interface AwardsTabProps {
  settings: AwardsSettings;
  updateSetting: (section: keyof AwardsSettings, key: string, value: any) => void;
  updateAwardSources: (sources: string[]) => void;
}

export function AwardsTab({ settings, updateSetting, updateAwardSources }: AwardsTabProps) {
  const handleColorSchemeChange = (colorScheme: string) => {
    updateSetting('Awards', 'color_scheme', colorScheme);
  };

  const handleAwardSourceToggle = (sourceValue: string, checked: boolean) => {
    const currentSources = settings.Awards.award_sources;
    let newSources: string[];
    
    if (checked) {
      newSources = [...currentSources, sourceValue];
    } else {
      newSources = currentSources.filter(source => source !== sourceValue);
    }
    
    updateAwardSources(newSources);
  };

  const selectedColorScheme = colorSchemes.find(scheme => scheme.value === settings.Awards.color_scheme);

  return (
    <div className="space-y-6">
      {/* Color Scheme Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Star className="h-5 w-5" />
            <CardTitle>Color Scheme</CardTitle>
          </div>
          <CardDescription>
            Choose the color scheme for award ribbons
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            {colorSchemes.map((color) => (
              <div key={color.value} className="relative">
                <input
                  id={`color-${color.value}`}
                  type="radio"
                  value={color.value}
                  checked={settings.Awards.color_scheme === color.value}
                  onChange={() => handleColorSchemeChange(color.value)}
                  disabled={!settings.General.enabled}
                  className="peer sr-only"
                />
                <label
                  htmlFor={`color-${color.value}`}
                  className={`flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-all ${
                    settings.Awards.color_scheme === color.value
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  } ${
                    !settings.General.enabled ? 'opacity-50 cursor-not-allowed' : ''
                  } ${color.bgClass}`}
                >
                  <div className="flex items-center space-x-2">
                    <div 
                      className={`w-4 h-4 rounded border-2 ${color.previewClass}`}
                    />
                    <span className={`text-sm font-medium ${color.textClass}`}>
                      {color.label}
                    </span>
                  </div>
                </label>
              </div>
            ))}
          </div>

          {/* Color Preview */}
          {settings.General.enabled && selectedColorScheme && (
            <div className="p-3 border rounded-lg bg-muted/50">
              <div className="text-sm font-medium mb-2">Preview:</div>
              <div className="flex items-center space-x-2">
                <div className={`w-8 h-8 rounded border-2 ${selectedColorScheme.previewClass}`} />
                <span className="text-sm text-muted-foreground">
                  {selectedColorScheme.label} scheme selected
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Award Sources Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            <CardTitle>Award Sources</CardTitle>
          </div>
          <CardDescription>
            Select which award types to detect and display
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="max-h-64 overflow-y-auto border rounded-lg p-3">
            <div className="space-y-3">
              {awardSources.map((source) => {
                const isChecked = settings.Awards.award_sources.includes(source.value);
                return (
                  <div key={source.value} className="flex items-center space-x-3">
                    <Checkbox
                      id={`award-${source.value}`}
                      checked={isChecked}
                      onCheckedChange={(checked) => 
                        handleAwardSourceToggle(source.value, checked as boolean)
                      }
                      disabled={!settings.General.enabled}
                    />
                    <label
                      htmlFor={`award-${source.value}`}
                      className={`flex-1 text-sm cursor-pointer ${
                        !settings.General.enabled ? 'opacity-50' : ''
                      }`}
                    >
                      {source.label}
                    </label>
                    {source.priority && (
                      <Badge variant="outline" className="text-xs">
                        {source.priority}
                      </Badge>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          
          <div className="text-sm text-muted-foreground">
            Selected awards will be detected automatically. Priority order: Oscars → Cannes → Golden Globe → BAFTA → Emmy → Others
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant="secondary">
              {settings.Awards.award_sources.length} sources selected
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Award Detection Info */}
      {settings.General.enabled && (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader>
            <CardTitle className="text-blue-900">Award Detection Info</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="font-medium text-blue-800 mb-2">Detection Sources:</div>
                <ul className="space-y-1 text-blue-700">
                  <li>• Static mapping database (140+ titles)</li>
                  <li>• TMDb API (real-time data)</li>
                  <li>• OMDB API (fallback data)</li>
                  <li>• 7-day API caching system</li>
                </ul>
              </div>
              <div>
                <div className="font-medium text-blue-800 mb-2">Coverage:</div>
                <ul className="space-y-1 text-blue-700">
                  <li>• 80+ award-winning movies</li>
                  <li>• 60+ award-winning TV shows</li>
                  <li>• {settings.Awards.award_sources.length} selected award types</li>
                  <li>• Priority-based detection system</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
