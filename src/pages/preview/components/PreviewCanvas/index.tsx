import * as React from "react";
import { useEffect, useRef } from "react";
import { PosterDimensions } from "@/services/posterService";
import { renderBadges as renderBadgesToCanvas } from "../../utils/badgeRenderer";
import { AudioBadgeSettings } from "@/components/badges/types/AudioBadge";
import { ResolutionBadgeSettings } from "@/components/badges/types/ResolutionBadge";
import { ReviewBadgeSettings } from "@/components/badges/types/ReviewBadge";

interface PreviewCanvasProps {
  showAudioBadge: boolean;
  showResolutionBadge: boolean;
  showReviewBadge: boolean;
  audioBadgeSettings: AudioBadgeSettings;
  resolutionBadgeSettings: ResolutionBadgeSettings;
  reviewBadgeSettings: ReviewBadgeSettings;
  posterDimensions: PosterDimensions;
  activeBadgeType: string | null;
  debugMode: boolean;
  loading: boolean;
}

const PreviewCanvas: React.FC<PreviewCanvasProps> = ({
  showAudioBadge,
  showResolutionBadge,
  showReviewBadge,
  audioBadgeSettings,
  resolutionBadgeSettings,
  reviewBadgeSettings,
  posterDimensions,
  activeBadgeType,
  debugMode,
  loading
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Function to immediately update the preview canvas
  const updatePreview = () => {
    if (canvasRef.current && posterDimensions.width > 50 && !loading) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('Forcing immediate preview update');
        // Clear the canvas and redraw all badges
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        renderBadges();
      }
    }
  };

  // Function to render badges to the canvas
  const renderBadges = async () => {
    if (canvasRef.current && posterDimensions.width > 50) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        await renderBadgesToCanvas(
          ctx,
          posterDimensions,
          showAudioBadge,
          showResolutionBadge,
          showReviewBadge,
          audioBadgeSettings,
          resolutionBadgeSettings,
          reviewBadgeSettings,
          activeBadgeType,
          debugMode
        );
      }
    }
  };

  // Force canvas redraw when settings change, with debounce
  useEffect(() => {
    if (loading) return;
    
    // Use debouncing to prevent too frequent updates
    const debounceTimeout = setTimeout(() => {
      renderBadges();
    }, 300); // 300ms debounce
    
    return () => clearTimeout(debounceTimeout);
  }, [
    audioBadgeSettings,
    resolutionBadgeSettings,
    reviewBadgeSettings,
    showAudioBadge,
    showResolutionBadge,
    showReviewBadge,
    posterDimensions,
    activeBadgeType,
    debugMode,
    loading
  ]);

  return (
    <canvas 
      ref={canvasRef}
      width={posterDimensions.width || 300}
      height={posterDimensions.height || 300}
      className="hidden" // Hidden canvas for rendering
    />
  );
};

export default PreviewCanvas;
