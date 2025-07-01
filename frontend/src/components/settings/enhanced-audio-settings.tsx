'use client';

import { useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Save, Volume2 } from 'lucide-react';
import { 
  GeneralTab, 
  TextTab, 
  BackgroundTab, 
  BorderTab, 
  ShadowTab, 
  ImagesTab,
  EnhancedDetectionTab,
  PerformanceTab,
  DiagnosticsTab,
  useAudioSettings 
} from './audio';

export function EnhancedAudioSettings() {
  const {
    loading,
    saving,
    settings,
    availableFonts,
    loadSettings,
    loadFonts,
    saveSettings,
    updateSetting,
    addAudioMapping,
    removeAudioMapping,
    updateCodecName,
    // Diagnostic functions
    runAudioCoverageAnalysis,
    getCacheStats,
    clearAudioCache,
    testEnhancedDetection
  } = useAudioSettings();

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
        <span className="ml-2">Loading audio badge settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Volume2 className="h-6 w-6" />
        <h2 className="text-2xl font-bold">Enhanced Audio Badge Settings</h2>
        <Badge variant="outline">Advanced Configuration</Badge>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-9">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="text">Text</TabsTrigger>
            <TabsTrigger value="background">Background</TabsTrigger>
            <TabsTrigger value="border">Border</TabsTrigger>
            <TabsTrigger value="shadow">Shadow</TabsTrigger>
            <TabsTrigger value="images">Images</TabsTrigger>
            <TabsTrigger value="enhanced">Enhanced</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="diagnostics">Diagnostics</TabsTrigger>
          </TabsList>

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
              addAudioMapping={addAudioMapping}
              removeAudioMapping={removeAudioMapping}
              updateCodecName={updateCodecName}
            />
          </TabsContent>

          <TabsContent value="enhanced">
            <EnhancedDetectionTab 
              settings={settings} 
              updateSetting={updateSetting}
            />
          </TabsContent>

          <TabsContent value="performance">
            <PerformanceTab 
              settings={settings} 
              updateSetting={updateSetting}
            />
          </TabsContent>

          <TabsContent value="diagnostics">
            <DiagnosticsTab 
              settings={settings}
              runAudioCoverageAnalysis={runAudioCoverageAnalysis}
              getCacheStats={getCacheStats}
              clearAudioCache={clearAudioCache}
              testEnhancedDetection={testEnhancedDetection}
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
            {saving ? 'Saving...' : 'Save Audio Settings'}
          </Button>
        </div>
      </form>
    </div>
  );
}
