import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Image, Plus, Minus, ArrowRight } from 'lucide-react';
import { ReviewSettings } from './types';

interface ImagesTabProps {
  settings: ReviewSettings;
  updateSetting: (section: keyof ReviewSettings, key: string, value: any) => void;
  addImageMapping?: (rating: string, image: string) => void;
  removeImageMapping?: (rating: string) => void;
  updateImageName?: (oldName: string, newName: string) => void;
}

export function ImagesTab({ 
  settings, 
  updateSetting, 
  addImageMapping, 
  removeImageMapping, 
  updateImageName 
}: ImagesTabProps) {
  const [newMapping, setNewMapping] = useState({ rating: '', image: '' });
  const [tempMappings, setTempMappings] = useState<Record<string, string>>({});

  const handleAddMapping = () => {
    if (newMapping.rating && newMapping.image) {
      updateSetting('ImageBadges', 'image_mapping', {
        ...settings.ImageBadges.image_mapping,
        [newMapping.rating]: newMapping.image
      });
      setNewMapping({ rating: '', image: '' });
      if (addImageMapping) {
        addImageMapping(newMapping.rating, newMapping.image);
      }
    }
  };

  const handleRemoveMapping = (rating: string) => {
    const newImageMapping = { ...settings.ImageBadges.image_mapping };
    delete newImageMapping[rating];
    updateSetting('ImageBadges', 'image_mapping', newImageMapping);
    if (removeImageMapping) {
      removeImageMapping(rating);
    }
  };

  const handleUpdateRatingName = (oldName: string, newName: string) => {
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
            Configure image-based badges for review sources
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="enable-image-badges"
                checked={settings.ImageBadges.enable_image_badges}
                onCheckedChange={(checked) => updateSetting('ImageBadges', 'enable_image_badges', checked)}
              />
              <Label htmlFor="enable-image-badges">Use Image Badges</Label>
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
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="image-directory">Image Directory</Label>
              <Input
                id="image-directory"
                type="text"
                value={settings.ImageBadges.codec_image_directory}
                onChange={(e) => updateSetting('ImageBadges', 'codec_image_directory', e.target.value)}
                placeholder="images/rating"
                disabled={!settings.ImageBadges.enable_image_badges}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="image-padding">Image Padding</Label>
              <Input
                id="image-padding"
                type="number"
                min="0"
                value={settings.ImageBadges.image_padding}
                onChange={(e) => updateSetting('ImageBadges', 'image_padding', parseInt(e.target.value) || 5)}
                placeholder="5"
                disabled={!settings.ImageBadges.enable_image_badges}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Image Mappings */}
      <Card>
        <CardHeader>
          <CardTitle>Image Mappings</CardTitle>
          <CardDescription>
            Map rating names to image filenames
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {Object.entries(settings.ImageBadges.image_mapping).map(([ratingName, imageName]) => (
              <div key={ratingName} className="grid grid-cols-12 gap-2 items-center">
                <Input
                  value={tempMappings[ratingName] || ratingName}
                  onChange={(e) => setTempMappings(prev => ({ ...prev, [ratingName]: e.target.value }))}
                  onBlur={(e) => {
                    const newName = e.target.value.trim();
                    if (newName && newName !== ratingName) {
                      handleUpdateRatingName(ratingName, newName);
                    }
                    setTempMappings(prev => {
                      const newMappings = { ...prev };
                      delete newMappings[ratingName];
                      return newMappings;
                    });
                  }}
                  className="col-span-5"
                  placeholder="Rating Name"
                  disabled={!settings.ImageBadges.enable_image_badges}
                />
                <ArrowRight className="col-span-1 h-4 w-4 text-muted-foreground justify-self-center" />
                <Input
                  value={imageName}
                  onChange={(e) => {
                    const newImageMapping = { ...settings.ImageBadges.image_mapping };
                    newImageMapping[ratingName] = e.target.value;
                    updateSetting('ImageBadges', 'image_mapping', newImageMapping);
                  }}
                  className="col-span-5"
                  placeholder="Image Name"
                  disabled={!settings.ImageBadges.enable_image_badges}
                />
                <Button
                  onClick={() => handleRemoveMapping(ratingName)}
                  variant="ghost"
                  size="sm"
                  className="col-span-1 h-8 w-8 p-0 text-red-500 hover:bg-red-50 hover:text-red-600"
                  disabled={!settings.ImageBadges.enable_image_badges}
                >
                  <Minus className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            {/* Add new mapping */}
            <div className="grid grid-cols-12 gap-2 items-center mt-4 pt-4 border-t">
              <Input
                value={newMapping.rating}
                onChange={(e) => setNewMapping(prev => ({ ...prev, rating: e.target.value }))}
                className="col-span-5"
                placeholder="Rating Name"
                disabled={!settings.ImageBadges.enable_image_badges}
              />
              <ArrowRight className="col-span-1 h-4 w-4 text-muted-foreground justify-self-center" />
              <Input
                value={newMapping.image}
                onChange={(e) => setNewMapping(prev => ({ ...prev, image: e.target.value }))}
                className="col-span-5"
                placeholder="Image Name"
                disabled={!settings.ImageBadges.enable_image_badges}
              />
              <Button
                onClick={handleAddMapping}
                variant="ghost"
                size="sm"
                className="col-span-1 h-8 w-8 p-0 text-green-500 hover:bg-green-50 hover:text-green-600"
                disabled={!settings.ImageBadges.enable_image_badges || !newMapping.rating || !newMapping.image}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {Object.keys(settings.ImageBadges.image_mapping).length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Image className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No image mappings configured</p>
              <p className="text-sm">Add mappings above to use image badges</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
