import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Trash2 } from 'lucide-react';
import { ResolutionSettings } from './types';

interface ImagesTabProps {
  settings: ResolutionSettings;
  updateSetting: (section: keyof ResolutionSettings, key: string, value: any) => void;
  addResolutionMapping: (resolution: string, image: string) => void;
  removeResolutionMapping: (resolution: string) => void;
  updateResolutionName: (oldName: string, newName: string) => void;
}

export function ImagesTab({ 
  settings, 
  updateSetting, 
  addResolutionMapping, 
  removeResolutionMapping, 
  updateResolutionName 
}: ImagesTabProps) {
  const [newMapping, setNewMapping] = useState({ resolution: '', image: '' });

  const handleAddMapping = () => {
    if (newMapping.resolution && newMapping.image) {
      addResolutionMapping(newMapping.resolution, newMapping.image);
      setNewMapping({ resolution: '', image: '' });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Image Badge Settings</CardTitle>
        <CardDescription>
          Configure image-based badges and resolution mappings
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center space-x-2">
          <Switch
            id="enable-image-badges"
            checked={settings.ImageBadges.enable_image_badges}
            onCheckedChange={(checked) => updateSetting('ImageBadges', 'enable_image_badges', checked)}
          />
          <Label htmlFor="enable-image-badges">Enable Image Badges</Label>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="resolution-directory">Resolution Image Directory</Label>
            <Input
              id="resolution-directory"
              type="text"
              value={settings.ImageBadges.codec_image_directory}
              onChange={(e) => updateSetting('ImageBadges', 'codec_image_directory', e.target.value)}
              disabled={!settings.ImageBadges.enable_image_badges}
              placeholder="images/resolution"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="image-padding">Image Padding</Label>
            <Input
              id="image-padding"
              type="number"
              min="0"
              value={settings.ImageBadges.image_padding}
              onChange={(e) => updateSetting('ImageBadges', 'image_padding', parseInt(e.target.value) || 20)}
              disabled={!settings.ImageBadges.enable_image_badges}
            />
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Switch
            id="fallback-to-text"
            checked={settings.ImageBadges.fallback_to_text}
            onCheckedChange={(checked) => updateSetting('ImageBadges', 'fallback_to_text', checked)}
            disabled={!settings.ImageBadges.enable_image_badges}
          />
          <Label htmlFor="fallback-to-text">Fallback to Text</Label>
        </div>

        {/* Resolution Mappings */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h4 className="text-lg font-semibold">Resolution Image Mappings</h4>
            <Badge variant="secondary">{Object.keys(settings.ImageBadges.image_mapping).length} mappings</Badge>
          </div>
          
          <div className="max-h-60 overflow-y-auto space-y-2 border rounded-md p-4">
            {Object.entries(settings.ImageBadges.image_mapping).map(([resolution, image]) => (
              <div key={resolution} className="flex items-center gap-2">
                <Input
                  value={resolution}
                  onChange={(e) => updateResolutionName(resolution, e.target.value)}
                  disabled={!settings.ImageBadges.enable_image_badges}
                  className="flex-1"
                  placeholder="Resolution Name (e.g., 4K, 1080p)"
                />
                <span className="text-muted-foreground">→</span>
                <Input
                  value={image}
                  onChange={(e) => updateSetting('ImageBadges', 'image_mapping', { 
                    ...settings.ImageBadges.image_mapping, 
                    [resolution]: e.target.value 
                  })}
                  disabled={!settings.ImageBadges.enable_image_badges}
                  className="flex-1"
                  placeholder="Image Filename (e.g., 4K.png)"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removeResolutionMapping(resolution)}
                  disabled={!settings.ImageBadges.enable_image_badges}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            {/* Add new mapping */}
            <div className="flex items-center gap-2 pt-2 border-t">
              <Input
                value={newMapping.resolution}
                onChange={(e) => setNewMapping(prev => ({ ...prev, resolution: e.target.value }))}
                disabled={!settings.ImageBadges.enable_image_badges}
                placeholder="New resolution name"
                className="flex-1"
              />
              <span className="text-muted-foreground">→</span>
              <Input
                value={newMapping.image}
                onChange={(e) => setNewMapping(prev => ({ ...prev, image: e.target.value }))}
                disabled={!settings.ImageBadges.enable_image_badges}
                placeholder="Image filename"
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleAddMapping}
                disabled={!settings.ImageBadges.enable_image_badges || !newMapping.resolution || !newMapping.image}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
