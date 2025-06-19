'use client';

import React, { useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  usePreviewData,
  usePreviewGeneration,
  useLibraryBrowser,
  useProcessingQueue,
  BadgeConfigurationPanel,
  PosterPreview,
  LibraryBrowser,
  ProcessingControls
} from '@/components/preview';
import { Eye, Zap } from 'lucide-react';

export default function PreviewPage() {
  // Initialize all hooks
  const { loading, data, loadPreviewData } = usePreviewData();
  const {
    selectedBadgeTypes,
    isGenerating,
    currentPreview,
    generatePreview,
    toggleBadgeType
  } = usePreviewGeneration();
  
  const {
    libraries,
    selectedLibrary,
    mediaItems,
    selectedMedia,
    loading: libraryLoading,
    loadLibraries,
    loadMedia,
    selectLibrary,
    selectMedia
  } = useLibraryBrowser();
  
  const {
    jobs,
    loading: queueLoading,
    loadJobs,
    addJob,
    cancelJob
  } = useProcessingQueue();

  // Load initial data
  useEffect(() => {
    loadPreviewData();
  }, []);

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Preview</h1>
        <p className="text-muted-foreground">
          Generate poster previews with badges to see how they'll look before applying changes
        </p>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="simple" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="simple" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Simple Preview
          </TabsTrigger>
          <TabsTrigger value="advanced" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Advanced Mode
          </TabsTrigger>
        </TabsList>

        {/* Simple Preview Mode */}
        <TabsContent value="simple" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Configuration */}
            <div className="space-y-6">
              <BadgeConfigurationPanel
                availableBadgeTypes={data.availableBadgeTypes}
                selectedBadgeTypes={selectedBadgeTypes}
                onToggleBadgeType={toggleBadgeType}
                onGeneratePreview={generatePreview}
                isGenerating={isGenerating}
              />
            </div>

            {/* Right Column - Preview */}
            <div className="space-y-6">
              <PosterPreview
                isGenerating={isGenerating}
                previewUrl={currentPreview.previewUrl}
                sourcePoster={currentPreview.sourcePoster}
                selectedBadgeTypes={selectedBadgeTypes}
                error={currentPreview.error}
              />
            </div>
          </div>
        </TabsContent>

        {/* Advanced Mode */}
        <TabsContent value="advanced" className="space-y-6">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* Left Column - Library & Configuration */}
            <div className="space-y-6">
              <LibraryBrowser
                libraries={libraries}
                selectedLibrary={selectedLibrary}
                mediaItems={mediaItems}
                selectedMedia={selectedMedia}
                loading={libraryLoading}
                onSelectLibrary={selectLibrary}
                onSelectMedia={selectMedia}
                onLoadLibraries={loadLibraries}
                onLoadMedia={loadMedia}
              />
              
              <BadgeConfigurationPanel
                availableBadgeTypes={data.availableBadgeTypes}
                selectedBadgeTypes={selectedBadgeTypes}
                onToggleBadgeType={toggleBadgeType}
                onGeneratePreview={generatePreview}
                isGenerating={isGenerating}
              />
            </div>

            {/* Right Column - Preview & Processing */}
            <div className="space-y-6">
              <PosterPreview
                isGenerating={isGenerating}
                previewUrl={currentPreview.previewUrl}
                sourcePoster={currentPreview.sourcePoster}
                selectedBadgeTypes={selectedBadgeTypes}
                error={currentPreview.error}
              />
              
              <ProcessingControls
                jobs={jobs}
                loading={queueLoading}
                onAddJob={addJob}
                onCancelJob={cancelJob}
                onLoadJobs={loadJobs}
                selectedMedia={selectedMedia}
                selectedBadgeTypes={selectedBadgeTypes}
              />
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
