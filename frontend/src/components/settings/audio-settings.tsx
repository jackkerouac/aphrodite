'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Save, Plus, Trash2, Volume2, Type } from 'lucide-react';
import { toast } from 'sonner';
import { saveSettingsWithCacheClear } from '@/lib/settings-utils';
import { FontSelect } from '@/components/ui/font-select';
import { loadAvailableFonts } from '@/lib/font-utils';

interface AudioSettings {
  General: {
    general_badge_size: number;
    general_edge_padding: number;
    general_badge_position: string;
    general_text_padding: number;
    use_dynamic_sizing: boolean;
  };
  Text: {
    font: string;
    fallback_font: string;
    'text-color': string;
    'text-size': number;
  };
  Background: {
    'background-color': string;
    background_opacity: number;
  };
  Border: {
    'border-color': string;
    'border-radius': number;
    border_width: number;
  };
  Shadow: {
    shadow_enable: boolean;
    shadow_blur: number;
    shadow_offset_x: number;
    shadow_offset_y: number;
  };
  ImageBadges: {
    enable_image_badges: boolean;
    codec_image_directory: string;
    fallback_to_text: boolean;
    image_padding: number;
    image_mapping: Record<string, string>;
  };
}

const defaultSettings: AudioSettings = {
  General: {
    general_badge_size: 100,
    general_edge_padding: 30,
    general_badge_position: 'top-right',
    general_text_padding: 12,
    use_dynamic_sizing: true
  },
  Text: {
    font: 'AvenirNextLTProBold.otf',
    fallback_font: 'DejaVuSans.ttf',
    'text-color': '#FFFFFF',
    'text-size': 90
  },
  Background: {
    'background-color': '#000000',
    background_opacity: 40
  },
  Border: {
    'border-color': '#000000',
    'border-radius': 10,
    border_width: 1
  },
  Shadow: {
    shadow_enable: false,
    shadow_blur: 8,
    shadow_offset_x: 2,
    shadow_offset_y: 2
  },
  ImageBadges: {
    enable_image_badges: true,
    codec_image_directory: 'images/codec',
    fallback_to_text: true,
    image_padding: 0,
    image_mapping: {
      'ATMOS': 'Atmos.png',
      'DOLBY DIGITAL PLUS': 'DigitalPlus.png',
      'DTS-HD MA': 'DTS-HD.png',
      'DTS-X': 'DTS-X.png',
      'TRUEHD': 'TrueHD.png',
      'TRUEHD ATMOS': 'TrueHD-Atmos.png'
    }
  }
};

export function AudioSettings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<AudioSettings>(defaultSettings);
  const [availableFonts, setAvailableFonts] = useState<string[]>([]);
  const [newMapping, setNewMapping] = useState({ codec: '', image: '' });

  // Load fonts
  const loadFonts = async () => {
    try {
      const fonts = await loadAvailableFonts();
      setAvailableFonts(fonts);
    } catch (error) {
      console.error('Error loading fonts:', error);
      setAvailableFonts([]);
    }
  };

  // Load settings from API
  const loadSettings = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_audio.yml`);
      const data = await response.json();
      
      if (data.config && Object.keys(data.config).length > 0) {
        // Merge loaded config with defaults to ensure all fields exist
        const mergedSettings = {
          ...defaultSettings,
          ...data.config,
          General: { ...defaultSettings.General, ...data.config.General },
          Text: { ...defaultSettings.Text, ...data.config.Text },
          Background: { ...defaultSettings.Background, ...data.config.Background },
          Border: { ...defaultSettings.Border, ...data.config.Border },
          Shadow: { ...defaultSettings.Shadow, ...data.config.Shadow },
          ImageBadges: { ...defaultSettings.ImageBadges, ...data.config.ImageBadges }
        };
        setSettings(mergedSettings);
      } else {
        setSettings(defaultSettings);
      }
    } catch (error) {
      console.error('Error loading audio settings:', error);
      toast.error('Failed to load audio badge settings');
      setSettings(defaultSettings);
    } finally {
      setLoading(false);
    }
  };

  // Save settings to API
  const saveSettings = async () => {
    setSaving(true);
    
    try {
      await saveSettingsWithCacheClear('badge_settings_audio.yml', settings);
      toast.success('Audio badge settings saved successfully!');
    } catch (error) {
      console.error('Error saving audio settings:', error);
      toast.error('Failed to save audio badge settings');
    } finally {
      setSaving(false);
    }
  };

  // Add new image mapping
  const addMapping = () => {
    if (newMapping.codec && newMapping.image) {
      setSettings(prev => ({
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: {
            ...prev.ImageBadges.image_mapping,
            [newMapping.codec]: newMapping.image
          }
        }
      }));
      setNewMapping({ codec: '', image: '' });
    }
  };

  // Remove image mapping
  const removeMapping = (codec: string) => {
    setSettings(prev => {
      const newImageMapping = { ...prev.ImageBadges.image_mapping };
      delete newImageMapping[codec];
      return {
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: newImageMapping
        }
      };
    });
  };

  // Update codec name in mapping
  const updateCodecName = (oldName: string, newName: string) => {
    if (oldName === newName || !newName.trim()) return;
    
    setSettings(prev => {
      const oldValue = prev.ImageBadges.image_mapping[oldName];
      const newImageMapping = { ...prev.ImageBadges.image_mapping };
      delete newImageMapping[oldName];
      newImageMapping[newName] = oldValue;
      
      return {
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: newImageMapping
        }
      };
    });
  };

  useEffect(() => {
    const loadAllData = async () => {
      await loadFonts();
      await loadSettings();
    };
    loadAllData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading audio badge settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Volume2 className="h-6 w-6" />
        <h2 className="text-2xl font-bold">Audio Badge Settings</h2>
        <Badge variant="outline">Badge Configuration</Badge>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); saveSettings(); }} className="space-y-6">
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="text">Text</TabsTrigger>
            <TabsTrigger value="background">Background</TabsTrigger>
            <TabsTrigger value="border">Border</TabsTrigger>
            <TabsTrigger value="shadow">Shadow</TabsTrigger>
            <TabsTrigger value="images">Images</TabsTrigger>
          </TabsList>

          {/* General Settings */}
          <TabsContent value="general">
            <Card>
              <CardHeader>
                <CardTitle>General Badge Settings</CardTitle>
                <CardDescription>
                  Configure basic badge positioning and sizing
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
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        General: { ...prev.General, general_badge_size: parseInt(e.target.value) || 100 }
                      }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="edge-padding">Edge Padding</Label>
                    <Input
                      id="edge-padding"
                      type="number"
                      min="0"
                      value={settings.General.general_edge_padding}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        General: { ...prev.General, general_edge_padding: parseInt(e.target.value) || 30 }
                      }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="badge-position">Badge Position</Label>
                    <Select 
                      value={settings.General.general_badge_position} 
                      onValueChange={(value) => setSettings(prev => ({
                        ...prev,
                        General: { ...prev.General, general_badge_position: value }
                      }))}
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
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        General: { ...prev.General, general_text_padding: parseInt(e.target.value) || 12 }
                      }))}
                    />
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="dynamic-sizing"
                    checked={settings.General.use_dynamic_sizing}
                    onCheckedChange={(checked) => setSettings(prev => ({
                      ...prev,
                      General: { ...prev.General, use_dynamic_sizing: checked }
                    }))}
                  />
                  <Label htmlFor="dynamic-sizing">Use Dynamic Sizing</Label>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Text Settings */}
          <TabsContent value="text">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Type className="h-5 w-5" />
                  Text Settings
                </CardTitle>
                <CardDescription>
                  Configure font, size, and text appearance for audio badges
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="font">Primary Font</Label>
                    <FontSelect
                      value={settings.Text.font}
                      onValueChange={(value) => setSettings(prev => ({
                        ...prev,
                        Text: { ...prev.Text, font: value }
                      }))}
                      availableFonts={availableFonts}
                      placeholder="Select a font..."
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="fallback-font">Fallback Font</Label>
                    <FontSelect
                      value={settings.Text.fallback_font}
                      onValueChange={(value) => setSettings(prev => ({
                        ...prev,
                        Text: { ...prev.Text, fallback_font: value }
                      }))}
                      availableFonts={availableFonts}
                      placeholder="Select a font..."
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="text-color">Text Color</Label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="color"
                        value={settings.Text['text-color']}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          Text: { ...prev.Text, 'text-color': e.target.value }
                        }))}
                        className="w-12 h-10 border rounded cursor-pointer"
                      />
                      <Input
                        type="text"
                        value={settings.Text['text-color']}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          Text: { ...prev.Text, 'text-color': e.target.value }
                        }))}
                        className="flex-1"
                        placeholder="#FFFFFF"
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
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        Text: { ...prev.Text, 'text-size': parseInt(e.target.value) || 90 }
                      }))}
                      placeholder="90"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Background Settings */}
          <TabsContent value="background">
            <Card>
              <CardHeader>
                <CardTitle>Background Settings</CardTitle>
                <CardDescription>
                  Configure badge background appearance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="background-color">Background Color</Label>
                    <div className="flex gap-2">
                      <input
                        type="color"
                        value={settings.Background['background-color']}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          Background: { ...prev.Background, 'background-color': e.target.value }
                        }))}
                        className="w-12 h-10 rounded border border-input"
                      />
                      <Input
                        value={settings.Background['background-color']}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          Background: { ...prev.Background, 'background-color': e.target.value }
                        }))}
                        placeholder="#000000"
                        className="flex-1"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="background-opacity">Background Opacity (%)</Label>
                    <Input
                      id="background-opacity"
                      type="number"
                      min="0"
                      max="100"
                      value={settings.Background.background_opacity}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        Background: { ...prev.Background, background_opacity: parseInt(e.target.value) || 40 }
                      }))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Border Settings */}
          <TabsContent value="border">
            <Card>
              <CardHeader>
                <CardTitle>Border Settings</CardTitle>
                <CardDescription>
                  Configure badge border appearance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="border-color">Border Color</Label>
                    <div className="flex gap-2">
                      <input
                        type="color"
                        value={settings.Border['border-color']}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          Border: { ...prev.Border, 'border-color': e.target.value }
                        }))}
                        className="w-12 h-10 rounded border border-input"
                      />
                      <Input
                        value={settings.Border['border-color']}
                        onChange={(e) => setSettings(prev => ({
                          ...prev,
                          Border: { ...prev.Border, 'border-color': e.target.value }
                        }))}
                        placeholder="#000000"
                        className="flex-1"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="border-radius">Border Radius</Label>
                    <Input
                      id="border-radius"
                      type="number"
                      min="0"
                      value={settings.Border['border-radius']}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        Border: { ...prev.Border, 'border-radius': parseInt(e.target.value) || 10 }
                      }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="border-width">Border Width</Label>
                    <Input
                      id="border-width"
                      type="number"
                      min="0"
                      value={settings.Border.border_width}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        Border: { ...prev.Border, border_width: parseInt(e.target.value) || 1 }
                      }))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Shadow Settings */}
          <TabsContent value="shadow">
            <Card>
              <CardHeader>
                <CardTitle>Shadow Settings</CardTitle>
                <CardDescription>
                  Configure badge drop shadow effects
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2 mb-4">
                  <Switch
                    id="shadow-enable"
                    checked={settings.Shadow.shadow_enable}
                    onCheckedChange={(checked) => setSettings(prev => ({
                      ...prev,
                      Shadow: { ...prev.Shadow, shadow_enable: checked }
                    }))}
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
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        Shadow: { ...prev.Shadow, shadow_blur: parseInt(e.target.value) || 8 }
                      }))}
                      disabled={!settings.Shadow.shadow_enable}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="shadow-offset-x">Shadow Offset X</Label>
                    <Input
                      id="shadow-offset-x"
                      type="number"
                      value={settings.Shadow.shadow_offset_x}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        Shadow: { ...prev.Shadow, shadow_offset_x: parseInt(e.target.value) || 2 }
                      }))}
                      disabled={!settings.Shadow.shadow_enable}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="shadow-offset-y">Shadow Offset Y</Label>
                    <Input
                      id="shadow-offset-y"
                      type="number"
                      value={settings.Shadow.shadow_offset_y}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        Shadow: { ...prev.Shadow, shadow_offset_y: parseInt(e.target.value) || 2 }
                      }))}
                      disabled={!settings.Shadow.shadow_enable}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Image Badge Settings */}
          <TabsContent value="images">
            <Card>
              <CardHeader>
                <CardTitle>Image Badge Settings</CardTitle>
                <CardDescription>
                  Configure image-based badges and codec mappings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="enable-image-badges"
                    checked={settings.ImageBadges.enable_image_badges}
                    onCheckedChange={(checked) => setSettings(prev => ({
                      ...prev,
                      ImageBadges: { ...prev.ImageBadges, enable_image_badges: checked }
                    }))}
                  />
                  <Label htmlFor="enable-image-badges">Enable Image Badges</Label>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="codec-directory">Codec Image Directory</Label>
                    <Input
                      id="codec-directory"
                      type="text"
                      value={settings.ImageBadges.codec_image_directory}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        ImageBadges: { ...prev.ImageBadges, codec_image_directory: e.target.value }
                      }))}
                      disabled={!settings.ImageBadges.enable_image_badges}
                      placeholder="images/codec"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="image-padding">Image Padding</Label>
                    <Input
                      id="image-padding"
                      type="number"
                      min="0"
                      value={settings.ImageBadges.image_padding}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        ImageBadges: { ...prev.ImageBadges, image_padding: parseInt(e.target.value) || 0 }
                      }))}
                      disabled={!settings.ImageBadges.enable_image_badges}
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="fallback-to-text"
                    checked={settings.ImageBadges.fallback_to_text}
                    onCheckedChange={(checked) => setSettings(prev => ({
                      ...prev,
                      ImageBadges: { ...prev.ImageBadges, fallback_to_text: checked }
                    }))}
                    disabled={!settings.ImageBadges.enable_image_badges}
                  />
                  <Label htmlFor="fallback-to-text">Fallback to Text</Label>
                </div>

                {/* Image Mappings */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <h4 className="text-lg font-semibold">Codec Image Mappings</h4>
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
                          placeholder="Codec Name"
                        />
                        <span className="text-muted-foreground">→</span>
                        <Input
                          value={image}
                          onChange={(e) => setSettings(prev => ({
                            ...prev,
                            ImageBadges: {
                              ...prev.ImageBadges,
                              image_mapping: { ...prev.ImageBadges.image_mapping, [codec]: e.target.value }
                            }
                          }))}
                          disabled={!settings.ImageBadges.enable_image_badges}
                          className="flex-1"
                          placeholder="Image Filename"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="icon"
                          onClick={() => removeMapping(codec)}
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
                        placeholder="New codec name"
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
                        onClick={addMapping}
                        disabled={!settings.ImageBadges.enable_image_badges || !newMapping.codec || !newMapping.image}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button type="submit" disabled={saving}>
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            {saving ? 'Saving...' : 'Save Audio Settings'}
          </Button>
        </div>
      </form>
    </div>
  );
}