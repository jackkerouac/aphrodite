'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Trophy } from 'lucide-react';
import { AwardsSettings } from './types';

interface GeneralTabProps {
  settings: AwardsSettings;
  updateSetting: (section: keyof AwardsSettings, key: string, value: any) => void;
}

export function GeneralTab({ settings, updateSetting }: GeneralTabProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Trophy className="h-5 w-5" />
          <CardTitle>General Settings</CardTitle>
        </div>
        <CardDescription>
          Basic configuration for awards badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Enable Awards Badges */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="awards-enabled">Enable Awards Badges</Label>
            <div className="text-sm text-muted-foreground">
              Awards badges appear flush in the bottom-right corner when media has won specific awards
            </div>
          </div>
          <Switch
            id="awards-enabled"
            checked={settings.General.enabled}
            onCheckedChange={(checked) => updateSetting('General', 'enabled', checked)}
          />
        </div>

        {/* Badge Size */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="badge-size">Badge Size</Label>
            <Input
              id="badge-size"
              type="number"
              min={50}
              max={351}
              value={settings.General.general_badge_size}
              onChange={(e) => updateSetting('General', 'general_badge_size', e.target.value === '' ? 351 : parseInt(e.target.value))}
              disabled={!settings.General.enabled}
            />
            <div className="text-sm text-muted-foreground">
              Recommended: 351px (full native resolution)
            </div>
          </div>

          {/* Badge Position */}
          <div className="space-y-2">
            <Label>Badge Position</Label>
            <div className="p-3 border rounded-lg bg-muted/50">
              <div className="font-medium flex items-center gap-2">
                <Badge variant="outline">Bottom-Right Flush</Badge>
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                Awards badges are always positioned flush to the bottom-right corner with no padding for optimal ribbon appearance
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Sizing */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="dynamic-sizing">Use Dynamic Sizing</Label>
            <div className="text-sm text-muted-foreground">
              Automatically adjust badge size based on content
            </div>
          </div>
          <Switch
            id="dynamic-sizing"
            checked={settings.General.use_dynamic_sizing}
            onCheckedChange={(checked) => updateSetting('General', 'use_dynamic_sizing', checked)}
            disabled={!settings.General.enabled}
          />
        </div>

        {/* Edge and Text Padding - Read-only for awards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="edge-padding">Edge Padding</Label>
            <Input
              id="edge-padding"
              type="number"
              value={settings.General.general_edge_padding}
              disabled={true}
              className="opacity-50"
            />
            <div className="text-sm text-muted-foreground">
              Awards use 0 padding for flush positioning
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="text-padding">Text Padding</Label>
            <Input
              id="text-padding"
              type="number"
              value={settings.General.general_text_padding}
              disabled={true}
              className="opacity-50"
            />
            <div className="text-sm text-muted-foreground">
              Awards use 0 padding for flush positioning
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
