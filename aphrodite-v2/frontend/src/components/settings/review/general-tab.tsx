import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ReviewSettings } from './types';

interface GeneralTabProps {
  settings: ReviewSettings;
  updateSetting: (section: keyof ReviewSettings, key: string, value: any) => void;
}

export function GeneralTab({ settings, updateSetting }: GeneralTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>General Settings</CardTitle>
        <CardDescription>
          Configure basic badge positioning and sizing for review badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="badge-size">Badge Size</Label>
            <Input
              id="badge-size"
              type="number"
              min="10"
              value={settings.General.general_badge_size}
              onChange={(e) => updateSetting('General', 'general_badge_size', parseInt(e.target.value) || 100)}
              placeholder="100"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="edge-padding">Edge Padding</Label>
            <Input
              id="edge-padding"
              type="number"
              min="0"
              value={settings.General.general_edge_padding}
              onChange={(e) => updateSetting('General', 'general_edge_padding', parseInt(e.target.value) || 30)}
              placeholder="30"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="badge-position">Badge Position</Label>
            <Select 
              value={settings.General.general_badge_position} 
              onValueChange={(value) => updateSetting('General', 'general_badge_position', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="top-left">Top Left</SelectItem>
                <SelectItem value="top-right">Top Right</SelectItem>
                <SelectItem value="bottom-left">Bottom Left</SelectItem>
                <SelectItem value="bottom-right">Bottom Right</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="text-padding">Text Padding</Label>
            <Input
              id="text-padding"
              type="number"
              min="0"
              value={settings.General.general_text_padding}
              onChange={(e) => updateSetting('General', 'general_text_padding', parseInt(e.target.value) || 20)}
              placeholder="20"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="badge-orientation">Badge Orientation</Label>
            <Select 
              value={settings.General.badge_orientation} 
              onValueChange={(value) => updateSetting('General', 'badge_orientation', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="horizontal">Horizontal</SelectItem>
                <SelectItem value="vertical">Vertical</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="badge-spacing">Badge Spacing</Label>
            <Input
              id="badge-spacing"
              type="number"
              min="0"
              value={settings.General.badge_spacing}
              onChange={(e) => updateSetting('General', 'badge_spacing', parseInt(e.target.value) || 15)}
              placeholder="15"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="max-badges">Max Badges to Display</Label>
            <Input
              id="max-badges"
              type="number"
              min="1"
              value={settings.General.max_badges_to_display}
              onChange={(e) => updateSetting('General', 'max_badges_to_display', parseInt(e.target.value) || 4)}
              placeholder="4"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Switch
            id="dynamic-sizing"
            checked={settings.General.use_dynamic_sizing}
            onCheckedChange={(checked) => updateSetting('General', 'use_dynamic_sizing', checked)}
          />
          <Label htmlFor="dynamic-sizing">Use Dynamic Sizing</Label>
        </div>
      </CardContent>
    </Card>
  );
}
