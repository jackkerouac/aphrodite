import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Image, Plus, Minus, ArrowRight } from 'lucide-react';
import { AwardsSettings } from './types';

interface ImagesTabProps {
  settings: AwardsSettings;
  updateSetting: (section: keyof AwardsSettings, key: string, value: any) => void;
  addImageMapping?: (award: string, image: string) => void;
  removeImageMapping?: (award: string) => void;
  updateImageName?: (oldName: string, newName: string) => void;
}

export function ImagesTab({ 
  settings, 
  updateSetting, 
  addImageMapping, 
  removeImageMapping, 
  updateImageName 
}: ImagesTabProps) {
  const [newMapping, setNewMapping] = useState({ award: '', image: '' });
  const [tempMappings, setTempMappings] = useState<Record<string, string>>({});

  const handleAddMapping = () => {
    if (newMapping.award && newMapping.image) {
      updateSetting('ImageBadges', 'image_mapping', {
        ...settings.ImageBadges.image_mapping,
        [newMapping.award]: newMapping.image
      });
      setNewMapping({ award: '', image: '' });
      if (addImageMapping) {
        addImageMapping(newMapping.award, newMapping.image);
      }
    }
  };

  const handleRemoveMapping = (award: string) => {
    const newImageMapping = { ...settings.ImageBadges.image_mapping };
    delete newImageMapping[award];
    updateSetting('ImageBadges', 'image_mapping', newImageMapping);
    if (removeImageMapping) {
      removeImageMapping(award);
    }
  };

  const handleUpdateAwardName = (oldName: string, newName: string) => {
    if (oldName === newName || !newName.trim()) return;
    
    const oldValue = settings.ImageBadges.image_mapping[oldName];
    const newImageMapping = { ...settings.ImageBadges.image_mapping };
    delete newImageMapping[oldName];
    newImageMapping[newName] = oldValue;
    
    updateSetting('ImageBadges', 'image_mapping', newImageMapping);
    
    if (updateImageName) {
      updateImageName(oldName, newName);
    }
  };

  return (
    <div className="space-y-6">
      {/* Image Badge Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Image className="h-5 w-5" />
            Image Badge Settings
          </CardTitle>
          <CardDescription>
            Configure image-based badges for award ribbons
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="enable-image-badges"
                checked={settings.ImageBadges.enable_image_badges}
                onCheckedChange={(checked) => updateSetting('ImageBadges', 'enable_image_badges', checked)}
                disabled={!settings.General.enabled}
              />
              <Label htmlFor="enable-image-badges">Use Image Badges</Label>
            </div>
            
            <div className="p-3 border rounded-lg bg-muted/50">
              <div className="text-sm font-medium mb-1">Awards Image Configuration</div>
              <div className="text-sm text-muted-foreground">
                Awards are image-only (no text fallback). Images are organized in color-coded subdirectories.
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="image-directory">Awards Image Directory</Label>
              <Input
                id="image-directory"
                type="text"
                value={settings.ImageBadges.codec_image_directory}
                onChange={(e) => updateSetting('ImageBadges', 'codec_image_directory', e.target.value)}
                placeholder="images/awards"
                disabled={true}
                className="opacity-50"
              />
              <div className="text-sm text-muted-foreground">
                This directory contains color-coded subdirectories (black, gray, red, yellow)
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="image-padding">Image Padding</Label>
              <Input
                id="image-padding"
                type="number"
                min="0"
                value={settings.ImageBadges.image_padding}
                onChange={(e) => updateSetting('ImageBadges', 'image_padding', parseInt(e.target.value) || 0)}
                placeholder="0"
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

      {/* Image Mappings */}
      <Card>
        <CardHeader>
          <CardTitle>Award Image Mappings</CardTitle>
          <CardDescription>
            Map award names to image filenames (located in color-coded subdirectories)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {Object.entries(settings.ImageBadges.image_mapping).map(([awardName, imageName]) => (
              <div key={awardName} className="grid grid-cols-12 gap-2 items-center">
                <Input
                  value={tempMappings[awardName] || awardName}
                  onChange={(e) => setTempMappings(prev => ({ ...prev, [awardName]: e.target.value }))}
                  onBlur={(e) => {
                    const newName = e.target.value.trim();
                    if (newName && newName !== awardName) {
                      handleUpdateAwardName(awardName, newName);
                    }
                    setTempMappings(prev => {
                      const newMappings = { ...prev };
                      delete newMappings[awardName];
                      return newMappings;
                    });
                  }}
                  className="col-span-5"
                  placeholder="Award Name"
                  disabled={!settings.ImageBadges.enable_image_badges || !settings.General.enabled}
                />
                <ArrowRight className="col-span-1 h-4 w-4 text-muted-foreground justify-self-center" />
                <Input
                  value={imageName}
                  onChange={(e) => {
                    const newImageMapping = { ...settings.ImageBadges.image_mapping };
                    newImageMapping[awardName] = e.target.value;
                    updateSetting('ImageBadges', 'image_mapping', newImageMapping);
                  }}
                  className="col-span-5"
                  placeholder="Image Name"
                  disabled={!settings.ImageBadges.enable_image_badges || !settings.General.enabled}
                />
                <Button
                  onClick={() => handleRemoveMapping(awardName)}
                  variant="ghost"
                  size="sm"
                  className="col-span-1 h-8 w-8 p-0 text-red-500 hover:bg-red-50 hover:text-red-600"
                  disabled={!settings.ImageBadges.enable_image_badges || !settings.General.enabled}
                >
                  <Minus className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            {/* Add new mapping */}
            <div className="grid grid-cols-12 gap-2 items-center mt-4 pt-4 border-t">
              <Input
                value={newMapping.award}
                onChange={(e) => setNewMapping(prev => ({ ...prev, award: e.target.value }))}
                className="col-span-5"
                placeholder="Award Name"
                disabled={!settings.ImageBadges.enable_image_badges || !settings.General.enabled}
              />
              <ArrowRight className="col-span-1 h-4 w-4 text-muted-foreground justify-self-center" />
              <Input
                value={newMapping.image}
                onChange={(e) => setNewMapping(prev => ({ ...prev, image: e.target.value }))}
                className="col-span-5"
                placeholder="Image Name"
                disabled={!settings.ImageBadges.enable_image_badges || !settings.General.enabled}
              />
              <Button
                onClick={handleAddMapping}
                variant="ghost"
                size="sm"
                className="col-span-1 h-8 w-8 p-0 text-green-500 hover:bg-green-50 hover:text-green-600"
                disabled={!settings.ImageBadges.enable_image_badges || !settings.General.enabled || !newMapping.award || !newMapping.image}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {Object.keys(settings.ImageBadges.image_mapping).length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Image className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No award image mappings configured</p>
              <p className="text-sm">Add mappings above to use award badges</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
