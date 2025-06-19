'use client';

import { useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Save, Trophy } from 'lucide-react';
import { 
  GeneralTab, 
  AwardsTab,
  TextTab,
  BackgroundTab,
  BorderTab,
  ShadowTab,
  ImagesTab,
  useAwardsSettings 
} from './awards';

export function AwardsSettings() {
  const {
    loading,
    saving,
    settings,
    availableFonts,
    loadSettings,
    loadFonts,
    saveSettings,
    updateSetting,
    addImageMapping,
    removeImageMapping,
    updateImageName,
    updateAwardSources
  } = useAwardsSettings();

  useEffect(() => {
    const loadAllData = async () => {
      await loadFonts();
      await loadSettings();
    };
    loadAllData();
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    saveSettings();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading awards badge settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Trophy className="h-6 w-6" />
        <h2 className="text-2xl font-bold">Awards Badge Settings</h2>
        <Badge variant="outline">Badge Configuration</Badge>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="awards">Awards</TabsTrigger>
            <TabsTrigger value="text">Text</TabsTrigger>
            <TabsTrigger value="background">Background</TabsTrigger>
            <TabsTrigger value="border">Border</TabsTrigger>
            <TabsTrigger value="shadow">Shadow</TabsTrigger>
            <TabsTrigger value="images">Images</TabsTrigger>
          </TabsList>

          <TabsContent value="general">
            <GeneralTab settings={settings} updateSetting={updateSetting} />
          </TabsContent>

          <TabsContent value="awards">
            <AwardsTab 
              settings={settings} 
              updateSetting={updateSetting}
              updateAwardSources={updateAwardSources}
            />
          </TabsContent>

          <TabsContent value="text">
            <TextTab 
              settings={settings} 
              updateSetting={updateSetting}
              availableFonts={availableFonts}
            />
          </TabsContent>

          <TabsContent value="background">
            <BackgroundTab settings={settings} updateSetting={updateSetting} />
          </TabsContent>

          <TabsContent value="border">
            <BorderTab settings={settings} updateSetting={updateSetting} />
          </TabsContent>

          <TabsContent value="shadow">
            <ShadowTab settings={settings} updateSetting={updateSetting} />
          </TabsContent>

          <TabsContent value="images">
            <ImagesTab 
              settings={settings} 
              updateSetting={updateSetting}
              addImageMapping={addImageMapping}
              removeImageMapping={removeImageMapping}
              updateImageName={updateImageName}
            />
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
            {saving ? 'Saving...' : 'Save Awards Settings'}
          </Button>
        </div>
      </form>
    </div>
  );
}
