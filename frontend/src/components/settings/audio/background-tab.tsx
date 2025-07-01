import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AudioSettings } from './types';

interface BackgroundTabProps {
  settings: AudioSettings;
  updateSetting: (path: string, value: any) => void;
}

export function BackgroundTab({ settings, updateSetting }: BackgroundTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Background Settings</CardTitle>
        <CardDescription>
          Configure badge background appearance for audio badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="background-color">Background Color</Label>
            <div className="flex gap-2">
              <input
                type="color"
                value={settings.Background['background-color']}
                onChange={(e) => updateSetting('Background.background-color', e.target.value)}
                className="w-12 h-10 rounded border border-input"
              />
              <Input
                value={settings.Background['background-color']}
                onChange={(e) => updateSetting('Background.background-color', e.target.value)}
                placeholder="#000000"
                className="flex-1"
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
              onChange={(e) => updateSetting('Background.background_opacity', parseInt(e.target.value) || 40)}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
