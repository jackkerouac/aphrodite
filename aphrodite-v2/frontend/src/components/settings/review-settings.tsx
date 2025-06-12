'use client';

import { useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Save, Star } from 'lucide-react';
import { 
  GeneralTab, 
  SourcesTab, 
  TextTab,
  BackgroundTab,
  BorderTab,
  ShadowTab,
  ImagesTab,
  useReviewSettings 
} from './review';

export function ReviewSettings() {
  const {
    loading,
    saving,
    settings,
    reviewSources,
    reviewSourceSettings,
    availableFonts,
    loadSettings,
    loadReviewSources,
    loadFonts,
    saveSettings,
    updateSetting,
    updateReviewSource,
    updateReviewSourceSettings,
    reorderSources,
    addImageMapping,
    removeImageMapping,
    updateImageName
  } = useReviewSettings();

  useEffect(() => {
    const loadAllData = async () => {
      await loadFonts();
      await loadSettings();
      await loadReviewSources();
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
        <span className="ml-2">Loading review badge settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Star className="h-6 w-6" />
        <h2 className="text-2xl font-bold">Review Badge Settings</h2>
        <Badge variant="outline">Badge Configuration</Badge>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <Tabs defaultValue="sources" className="space-y-6">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="sources">Sources</TabsTrigger>
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="text">Text</TabsTrigger>
            <TabsTrigger value="background">Background</TabsTrigger>
            <TabsTrigger value="border">Border</TabsTrigger>
            <TabsTrigger value="shadow">Shadow</TabsTrigger>
            <TabsTrigger value="images">Images</TabsTrigger>
          </TabsList>

          <TabsContent value="sources">
            <SourcesTab 
              settings={settings} 
              reviewSources={reviewSources}
              reviewSourceSettings={reviewSourceSettings}
              updateSetting={updateSetting}
              updateReviewSource={updateReviewSource}
              updateReviewSourceSettings={updateReviewSourceSettings}
              reorderSources={reorderSources}
            />
          </TabsContent>

          <TabsContent value="general">
            <GeneralTab settings={settings} updateSetting={updateSetting} />
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
            {saving ? 'Saving...' : 'Save Review Settings'}
          </Button>
        </div>
      </form>
    </div>
  );
}
