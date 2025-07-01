import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Plus, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { AudioSettings } from './types';

interface ImagesTabProps {
  settings: AudioSettings;
  updateSetting: (path: string, value: any) => void;
  addAudioMapping: (codec: string, image: string) => boolean;
  removeAudioMapping: (codec: string) => void;
  updateCodecName: (oldName: string, newName: string) => void;
}

export function ImagesTab({ 
  settings, 
  updateSetting, 
  addAudioMapping, 
  removeAudioMapping, 
  updateCodecName 
}: ImagesTabProps) {
  const [newMapping, setNewMapping] = useState({ codec: '', image: '' });

  const handleAddMapping = () => {
    if (addAudioMapping(newMapping.codec, newMapping.image)) {
      setNewMapping({ codec: '', image: '' });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Image Badge Settings</CardTitle>
        <CardDescription>
          Configure image-based badges and audio codec mappings
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center space-x-2">
          <Switch
            id="enable-image-badges"
            checked={settings.ImageBadges.enable_image_badges}
            onCheckedChange={(checked) => updateSetting('ImageBadges.enable_image_badges', checked)}
          />
          <Label htmlFor="enable-image-badges">Enable Image Badges</Label>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="codec-directory">Audio Image Directory</Label>
            <Input
              id="codec-directory"
              type="text"
              value={settings.ImageBadges.codec_image_directory}
              onChange={(e) => updateSetting('ImageBadges.codec_image_directory', e.target.value)}
              disabled={!settings.ImageBadges.enable_image_badges}
              placeholder="images/audio"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="image-padding">Image Padding</Label>
            <Input
              id="image-padding"
              type="number"
              min="0"
              value={settings.ImageBadges.image_padding}
              onChange={(e) => updateSetting('ImageBadges.image_padding', parseInt(e.target.value) || 0)}
              disabled={!settings.ImageBadges.enable_image_badges}
            />
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Switch
            id="fallback-to-text"
            checked={settings.ImageBadges.fallback_to_text}
            onCheckedChange={(checked) => updateSetting('ImageBadges.fallback_to_text', checked)}
            disabled={!settings.ImageBadges.enable_image_badges}
          />
          <Label htmlFor="fallback-to-text">Fallback to Text</Label>
        </div>

        {/* Audio Mappings */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h4 className="text-lg font-semibold">Audio Codec Image Mappings</h4>
            <Badge variant="secondary">{Object.keys(settings.ImageBadges.image_mapping).length} mappings</Badge>
          </div>
          
          <div className="max-h-60 overflow-y-auto space-y-2 border rounded-md p-4">
            {Object.entries(settings.ImageBadges.image_mapping).map(([codec, image]) => (
              <div key={codec} className="flex items-center gap-2">
                <Input
                  value={codec}
                  onChange={(e) => updateCodecName(codec, e.target.value)}
                  disabled={!settings.ImageBadges.enable_image_badges}
                  className="flex-1"
                  placeholder="Audio Codec Name"
                />
                <span className="text-muted-foreground">→</span>
                <Input
                  value={image}
                  onChange={(e) => updateSetting(`ImageBadges.image_mapping.${codec}`, e.target.value)}
                  disabled={!settings.ImageBadges.enable_image_badges}
                  className="flex-1"
                  placeholder="Image Filename"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removeAudioMapping(codec)}
                  disabled={!settings.ImageBadges.enable_image_badges}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            {/* Add new mapping */}
            <div className="flex items-center gap-2 pt-2 border-t">
              <Input
                value={newMapping.codec}
                onChange={(e) => setNewMapping(prev => ({ ...prev, codec: e.target.value }))}
                disabled={!settings.ImageBadges.enable_image_badges}
                placeholder="New audio codec name"
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
                disabled={!settings.ImageBadges.enable_image_badges || !newMapping.codec || !newMapping.image}
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
