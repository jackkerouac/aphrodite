'use client';

import React, { useEffect } from 'react';
import { 
  usePreviewData,
  usePreviewGeneration,
  BadgeConfigurationPanel,
  PosterPreview
} from '@/components/preview';

export default function PreviewPage() {
  // Initialize hooks
  const { loading, data, loadPreviewData } = usePreviewData();
  const {
    selectedBadgeTypes,
    isGenerating,
    currentPreview,
    generatePreview,
    toggleBadgeType
  } = usePreviewGeneration();

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
      <div className="space-y-6">
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
      </div>
    </div>
  );
}
