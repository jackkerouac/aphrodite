import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Square } from 'lucide-react';
import { AwardsSettings } from './types';

interface BackgroundTabProps {
  settings: AwardsSettings;
  updateSetting: (section: keyof AwardsSettings, key: string, value: any) => void;
}

export function BackgroundTab({ settings, updateSetting }: BackgroundTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Square className="h-5 w-5" />
          Background Settings
        </CardTitle>
        <CardDescription>
          Configure background color and opacity for awards badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="background-color">Background Color</Label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={settings.Background['background-color']}
                onChange={(e) => updateSetting('Background', 'background-color', e.target.value)}
                disabled={!settings.General.enabled}
                className="w-12 h-10 border rounded cursor-pointer disabled:opacity-50"
              />
              <Input
                type="text"
                value={settings.Background['background-color']}
                onChange={(e) => updateSetting('Background', 'background-color', e.target.value)}
                disabled={!settings.General.enabled}
                className="flex-1"
                placeholder="#000000"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="background-opacity">Background Opacity (%)</Label>
            <Input
              id="background-opacity"
              type="number"
              min="0"
              max="100"
              value={settings.Background.background_opacity}
              onChange={(e) => updateSetting('Background', 'background_opacity', parseInt(e.target.value) || 40)}
              disabled={!settings.General.enabled}
              placeholder="40"
            />
            <div className="text-sm text-muted-foreground">
              Awards typically use lower opacity for ribbon visibility
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
