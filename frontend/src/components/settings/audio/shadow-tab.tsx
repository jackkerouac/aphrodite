import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { AudioSettings } from './types';

interface ShadowTabProps {
  settings: AudioSettings;
  updateSetting: (path: string, value: any) => void;
}

export function ShadowTab({ settings, updateSetting }: ShadowTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Shadow Settings</CardTitle>
        <CardDescription>
          Configure badge drop shadow effects for audio badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <Switch
            id="shadow-enable"
            checked={settings.Shadow.shadow_enable}
            onCheckedChange={(checked) => updateSetting('Shadow.shadow_enable', checked)}
          />
          <Label htmlFor="shadow-enable">Enable Shadow</Label>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="shadow-blur">Shadow Blur</Label>
            <Input
              id="shadow-blur"
              type="number"
              min="0"
              value={settings.Shadow.shadow_blur}
              onChange={(e) => updateSetting('Shadow.shadow_blur', parseInt(e.target.value) || 8)}
              disabled={!settings.Shadow.shadow_enable}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="shadow-offset-x">Shadow Offset X</Label>
            <Input
              id="shadow-offset-x"
              type="number"
              value={settings.Shadow.shadow_offset_x}
              onChange={(e) => updateSetting('Shadow.shadow_offset_x', parseInt(e.target.value) || 2)}
              disabled={!settings.Shadow.shadow_enable}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="shadow-offset-y">Shadow Offset Y</Label>
            <Input
              id="shadow-offset-y"
              type="number"
              value={settings.Shadow.shadow_offset_y}
              onChange={(e) => updateSetting('Shadow.shadow_offset_y', parseInt(e.target.value) || 2)}
              disabled={!settings.Shadow.shadow_enable}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
