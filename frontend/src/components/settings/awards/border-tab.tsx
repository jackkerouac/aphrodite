import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Square } from 'lucide-react';
import { AwardsSettings } from './types';

interface BorderTabProps {
  settings: AwardsSettings;
  updateSetting: (section: keyof AwardsSettings, key: string, value: any) => void;
}

export function BorderTab({ settings, updateSetting }: BorderTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Square className="h-5 w-5" />
          Border Settings
        </CardTitle>
        <CardDescription>
          Configure border appearance for awards badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="border-color">Border Color</Label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={settings.Border['border-color']}
                onChange={(e) => updateSetting('Border', 'border-color', e.target.value)}
                disabled={!settings.General.enabled}
                className="w-12 h-10 border rounded cursor-pointer disabled:opacity-50"
              />
              <Input
                type="text"
                value={settings.Border['border-color']}
                onChange={(e) => updateSetting('Border', 'border-color', e.target.value)}
                disabled={!settings.General.enabled}
                className="flex-1"
                placeholder="#000000"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="border-width">Border Width</Label>
            <Input
              id="border-width"
              type="number"
              min="0"
              value={settings.Border.border_width}
              onChange={(e) => updateSetting('Border', 'border_width', parseInt(e.target.value) || 0)}
              disabled={!settings.General.enabled}
              placeholder="1"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="border-radius">Border Radius</Label>
            <Input
              id="border-radius"
              type="number"
              min="0"
              value={settings.Border['border_radius']}
              onChange={(e) => updateSetting('Border', 'border_radius', parseInt(e.target.value) || 10)}
              disabled={!settings.General.enabled}
              placeholder="10"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
