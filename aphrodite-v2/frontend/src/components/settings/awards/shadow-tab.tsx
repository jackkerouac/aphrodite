import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Cloud } from 'lucide-react';
import { AwardsSettings } from './types';

interface ShadowTabProps {
  settings: AwardsSettings;
  updateSetting: (section: keyof AwardsSettings, key: string, value: any) => void;
}

export function ShadowTab({ settings, updateSetting }: ShadowTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Cloud className="h-5 w-5" />
          Shadow Settings
        </CardTitle>
        <CardDescription>
          Configure shadow effects for awards badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <Switch
            id="shadow-enable"
            checked={settings.Shadow.shadow_enable}
            onCheckedChange={(checked) => updateSetting('Shadow', 'shadow_enable', checked)}
            disabled={!settings.General.enabled}
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
              onChange={(e) => updateSetting('Shadow', 'shadow_blur', parseInt(e.target.value) || 8)}
              placeholder="8"
              disabled={!settings.Shadow.shadow_enable || !settings.General.enabled}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="shadow-x">Shadow X Offset</Label>
            <Input
              id="shadow-x"
              type="number"
              value={settings.Shadow.shadow_offset_x}
              onChange={(e) => updateSetting('Shadow', 'shadow_offset_x', parseInt(e.target.value) || 2)}
              placeholder="2"
              disabled={!settings.Shadow.shadow_enable || !settings.General.enabled}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="shadow-y">Shadow Y Offset</Label>
            <Input
              id="shadow-y"
              type="number"
              value={settings.Shadow.shadow_offset_y}
              onChange={(e) => updateSetting('Shadow', 'shadow_offset_y', parseInt(e.target.value) || 2)}
              placeholder="2"
              disabled={!settings.Shadow.shadow_enable || !settings.General.enabled}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
