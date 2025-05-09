import * as React from "react";
import { useEffect, useRef } from "react";
import { useBadgePreviewSettings } from "./preview/hooks/useBadgePreviewSettings";
import { usePosterState } from "./preview/hooks/usePosterState";
import { useBadgeState } from "./preview/hooks/useBadgeState";
import { saveBadgeAsPng } from "./preview/utils/badgeRenderer";
import BadgeSettingsArea from "./preview/components/BadgeSettingsArea";
import BadgePreviewArea from "./preview/components/BadgePreviewArea";

export default function Preview() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Use the badge preview settings hook to manage badge visibility
  const { 
    displaySettings: { showAudioBadge, showResolutionBadge, showReviewBadge },
    toggleBadge,
    loading: badgeSettingsLoading
  } = useBadgePreviewSettings();
  
  // Use poster state hook to manage poster display
  const posterState = usePosterState();
  
  // Function to update preview immediately
  const updateCanvasCallback = () => {
    // Logic to force canvas redraw
    if (canvasRef.current && posterState.posterDimensions.width > 50 && !posterState.loading) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('Forcing immediate preview update from main component');
        badgeRenderCallbackRef.current(ctx, posterState.posterDimensions);
      }
    }
  };
  
  // Use badge state hook to manage badge settings
  const badgeState = useBadgeState("123", updateCanvasCallback);
  
  // Effect to update loading state
  useEffect(() => {
    posterState.setLoading(badgeState.loading || badgeSettingsLoading);
  }, [badgeState.loading, badgeSettingsLoading]);
  
  // Function to render badges to canvas (will be passed to child components)
  const badgeRenderCallback = async (ctx: CanvasRenderingContext2D, dimensions: PosterDimensions) => {
    // Import here to prevent circular dependency
    const { renderBadges } = await import("./preview/utils/badgeRenderer");
    
    return renderBadges(
      ctx,
      dimensions,
      showAudioBadge,
      showResolutionBadge,
      showReviewBadge,
      badgeState.audioBadgeSettings,
      badgeState.resolutionBadgeSettings,
      badgeState.reviewBadgeSettings,
      badgeState.activeBadgeType,
      posterState.debugMode
    );
  };
  
  // Use a ref to keep the render callback function stable
  const badgeRenderCallbackRef = useRef(badgeRenderCallback);
  
  // Update the ref when dependencies change
  useEffect(() => {
    badgeRenderCallbackRef.current = badgeRenderCallback;
  }, [
    showAudioBadge,
    showResolutionBadge,
    showReviewBadge,
    badgeState.audioBadgeSettings,
    badgeState.resolutionBadgeSettings,
    badgeState.reviewBadgeSettings,
    badgeState.activeBadgeType,
    posterState.debugMode
  ]);
  
  // Function to save badge as PNG
  const handleSaveBadgeAsPng = (type: string) => {
    saveBadgeAsPng(
      type,
      badgeState.audioBadgeSettings,
      badgeState.resolutionBadgeSettings,
      badgeState.reviewBadgeSettings
    );
  };

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-3xl font-bold tracking-tight">Preview</h1>
      <p className="text-muted-foreground">Customize and preview your badges on a poster</p>
      
      <div className="flex flex-col md:flex-row gap-8">
        {/* Badge Settings Area (Left - 50%) */}
        <div className="w-full md:w-1/2">
          <BadgeSettingsArea
            displaySettings={{
              showAudioBadge,
              showResolutionBadge,
              showReviewBadge
            }}
            toggleBadge={toggleBadge}
            loading={posterState.loading}
            badgeSettingsLoading={badgeSettingsLoading}
            onBadgeTypeChange={badgeState.setActiveBadgeType}
            saveHandlers={{
              audio: badgeState.saveAudioBadgeSettings,
              resolution: badgeState.saveResolutionBadgeSettings,
              review: badgeState.saveReviewBadgeSettings
            }}
            saveBadgeAsPng={handleSaveBadgeAsPng}
          />
        </div>

        {/* Preview Area (Right - 50%) */}
        <div className="w-full md:w-1/2">
          <BadgePreviewArea
            activeBadgeType={badgeState.activeBadgeType}
            debugMode={posterState.debugMode}
            loading={posterState.loading}
            posterDimensions={posterState.posterDimensions}
            togglePoster={posterState.togglePoster}
            toggleDebugMode={posterState.toggleDebugMode}
            activePoster={posterState.activePoster}
            renderBadges={badgeRenderCallbackRef.current}
            onBadgePositionChange={badgeState.handleBadgePositionChange}
            onPosterLoad={posterState.handlePosterLoad}
          />
        </div>
      </div>
      
      {/* Hidden canvas reference */}
      <canvas 
        ref={canvasRef}
        width={posterState.posterDimensions.width || 300}
        height={posterState.posterDimensions.height || 300}
        className="hidden" // Hidden canvas for rendering
      />
    </div>
  );
}

// Import PosterDimensions type at end to avoid circular dependency
import { PosterDimensions } from "@/services/posterService";
