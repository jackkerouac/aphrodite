import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AudioSettings } from './types';

interface GeneralTabProps {
  settings: AudioSettings;
  updateSetting: (path: string, value: any) => void;
}

export function GeneralTab({ settings, updateSetting }: GeneralTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>General Badge Settings</CardTitle>
        <CardDescription>
          Configure basic badge positioning and sizing for audio badges
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
              onChange={(e) => updateSetting('General.general_badge_size', parseInt(e.target.value) || 100)}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="edge-padding">Edge Padding</Label>
            <Input
              id="edge-padding"
              type="number"
              min="0"
              value={settings.General.general_edge_padding}
              onChange={(e) => updateSetting('General.general_edge_padding', parseInt(e.target.value) || 30)}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="badge-position">Badge Position</Label>
            <Select 
              value={settings.General.general_badge_position} 
              onValueChange={(value) => updateSetting('General.general_badge_position', value)}
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
              onChange={(e) => updateSetting('General.general_text_padding', parseInt(e.target.value) || 12)}
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Switch
            id="dynamic-sizing"
            checked={settings.General.use_dynamic_sizing}
            onCheckedChange={(checked) => updateSetting('General.use_dynamic_sizing', checked)}
          />
          <Label htmlFor="dynamic-sizing">Use Dynamic Sizing</Label>
        </div>
      </CardContent>
    </Card>
  );
}
