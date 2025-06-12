import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ResolutionSettings } from './types';

interface TextTabProps {
  settings: ResolutionSettings;
  updateSetting: (section: keyof ResolutionSettings, key: string, value: any) => void;
}

export function TextTab({ settings, updateSetting }: TextTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Text Settings</CardTitle>
        <CardDescription>
          Configure text appearance for resolution badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="font">Font</Label>
            <Input
              id="font"
              type="text"
              value={settings.Text.font}
              onChange={(e) => updateSetting('Text', 'font', e.target.value)}
              placeholder="AvenirNextLTProBold.otf"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="fallback-font">Fallback Font</Label>
            <Input
              id="fallback-font"
              type="text"
              value={settings.Text.fallback_font}
              onChange={(e) => updateSetting('Text', 'fallback_font', e.target.value)}
              placeholder="DejaVuSans.ttf"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="text-color">Text Color</Label>
            <div className="flex gap-2">
              <input
                type="color"
                value={settings.Text['text-color']}
                onChange={(e) => updateSetting('Text', 'text-color', e.target.value)}
                className="w-12 h-10 rounded border border-input"
              />
              <Input
                value={settings.Text['text-color']}
                onChange={(e) => updateSetting('Text', 'text-color', e.target.value)}
                placeholder="#FFFFFF"
                className="flex-1"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="text-size">Text Size</Label>
            <Input
              id="text-size"
              type="number"
              min="10"
              value={settings.Text['text-size']}
              onChange={(e) => updateSetting('Text', 'text-size', parseInt(e.target.value) || 90)}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
