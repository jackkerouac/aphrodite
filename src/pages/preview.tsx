import * as React from "react";
import { useEffect, useRef, useCallback } from "react";
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
  
  // Log current toggle states whenever they change, for debugging
  useEffect(() => {
    console.log('Toggle states updated in Preview component:', { 
      showAudioBadge, 
      showResolutionBadge, 
      showReviewBadge 
    });
  }, [showAudioBadge, showResolutionBadge, showReviewBadge]);
  
  // Use poster state hook to manage poster display
  const posterState = usePosterState();
  
  // Create a placeholder updateCanvasCallback to avoid hook ordering issues
  const updateCanvasCallbackRef = useRef(() => {});
  
  // Use badge state hook to manage badge settings
  const badgeState = useBadgeState("123", () => updateCanvasCallbackRef.current());
  
  // Effect to update loading state
  useEffect(() => {
    posterState.setLoading(badgeState.loading || badgeSettingsLoading);
  }, [badgeState.loading, badgeSettingsLoading]);
  
  // Completely rewritten badge rendering approach
  const renderBadges = async (ctx: CanvasRenderingContext2D, dimensions: PosterDimensions) => {
    // Import rendering utility
    const { renderBadges: applyBadgesToCanvas } = await import("./preview/utils/badgeRenderer");
    
    // Log this render request with all relevant state
    console.log('Render badges called with dimensions:', dimensions);
    console.log('Current toggle states:', { 
      showAudioBadge, 
      showResolutionBadge, 
      showReviewBadge 
    });
    
    // First clear the canvas completely
    ctx.clearRect(0, 0, dimensions.width, dimensions.height);
    
    // Then apply badges based on current toggle states
    return applyBadgesToCanvas(
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
  
  // Create a memoized render function that updates when any dependency changes
  const badgeRenderCallback = useCallback(renderBadges, [
    showAudioBadge,
    showResolutionBadge,
    showReviewBadge,
    badgeState.audioBadgeSettings,
    badgeState.resolutionBadgeSettings,
    badgeState.reviewBadgeSettings,
    badgeState.activeBadgeType,
    posterState.debugMode
  ]);
  
  // Force re-render of canvas when toggle states change
  useEffect(() => {
    if (canvasRef.current && !posterState.loading) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('Toggle state changed - forcing canvas update');
        badgeRenderCallback(ctx, posterState.posterDimensions);
      }
    }
  }, [showAudioBadge, showResolutionBadge, showReviewBadge, posterState.loading, posterState.posterDimensions, badgeRenderCallback]);
  
  // Update the canvas callback ref with latest function
  useEffect(() => {
    // Now define the real update function using all current dependencies
    updateCanvasCallbackRef.current = () => {
      if (canvasRef.current && posterState.posterDimensions.width > 50 && !posterState.loading) {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          console.log('Updating canvas via callback ref');
          badgeRenderCallback(ctx, posterState.posterDimensions);
        }
      }
    };
  }, [badgeRenderCallback, posterState.posterDimensions, posterState.loading]);
  
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
            renderBadges={badgeRenderCallback}
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
