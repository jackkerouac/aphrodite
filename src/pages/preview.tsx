import * as React from "react";
import { useState, useEffect, useRef } from "react";
// Remove ResolutionBadgeToggle and AudioBadgeToggle imports
import BadgeToggles from "./preview/components/BadgeToggles";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileSliders, ScanEye, Download } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { renderBadgeToCanvas, extractBadgeWithTransparency } from "@/services/badgeRenderer";
import { getResolutionImagePath, getResolutionDisplayName } from "@/utils/resolutionUtils";
import { useBadgeSettings } from "@/hooks/useBadgeSettings";
import BadgeControls from "@/components/badges/BadgeControls";
import FixedPosterPreview from "@/components/badges/FixedPosterPreview";
import { AudioBadgeSettings } from "@/components/badges/types/AudioBadge";
import { ResolutionBadgeSettings } from "@/components/badges/types/ResolutionBadge";
import { ReviewBadgeSettings } from "@/components/badges/types/ReviewBadge";
import { PosterDimensions } from "@/services/posterService";

// Import dummy poster images
import lightPoster from "../assets/example_poster_light.png";
import darkPoster from "../assets/example_poster_dark.png";

// Default settings for each badge type if hook fails to load
const defaultAudioBadgeSettings = {
  type: 'audio',
  size: 80,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  textColor: '#FFFFFF',
  codecType: 'Dolby Atmos',
  position: {
    percentX: 5,
    percentY: 5,
  },
};

const defaultResolutionBadgeSettings = {
  type: 'resolution',
  size: 100,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  textColor: '#FFFFFF',
  resolutionType: '1080p',
  // Use utility functions for resolution image path and display name
  getResolutionImagePath: getResolutionImagePath,
  getResolutionDisplayName: getResolutionDisplayName,
  position: {
    percentX: 5,
    percentY: 15,
  },
};

const defaultReviewBadgeSettings = {
  type: 'review',
  size: 100,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  textColor: '#FFFFFF',
  displayFormat: 'horizontal',
  maxSourcesToShow: 2,
  showDividers: true,
  sources: [
    { name: 'IMDB', rating: 8.5, outOf: 10 },
    { name: 'RT', rating: 90, outOf: 100 }
  ],
  position: {
    percentX: 5,
    percentY: 25,
  },
};

export default function Preview() {
  // State for poster and badge display
  const [activePoster, setActivePoster] = useState("light");
  const [posterImage, setPosterImage] = useState(lightPoster);
  const [posterDimensions, setPosterDimensions] = useState<PosterDimensions>({
    width: 0,
    height: 0,
    aspectRatio: 1,
  });
  
  // Display toggles for each badge type
  const [showAudioBadge, setShowAudioBadge] = useState(true);
  const [showResolutionBadge, setShowResolutionBadge] = useState(true);
  const [showReviewBadge, setShowReviewBadge] = useState(true);
  
  // Active badge type for editing
  const [activeBadgeType, setActiveBadgeType] = useState<string | null>("audio");
  
  // Debug mode toggle
  const [debugMode, setDebugMode] = useState(false);
  
  // Loading state
  const [loading, setLoading] = useState(true);
  
  // References
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Render badges on canvas
  const renderBadges = async (ctx: CanvasRenderingContext2D, dimensions: PosterDimensions) => {
    // Return early if dimensions are invalid
    if (!dimensions || dimensions.width < 50 || dimensions.height < 50) {
      console.log('Invalid dimensions, skipping badge rendering');
      return;
    }

    // Use defaults if settings are not available
    const actualAudioSettings = audioBadgeSettings || defaultAudioBadgeSettings;
    const actualResolutionSettings = resolutionBadgeSettings || defaultResolutionBadgeSettings;
    const actualReviewSettings = reviewBadgeSettings || defaultReviewBadgeSettings;
    
    // Add a console log to debug
    console.log('Rendering badges with dimensions:', dimensions);
    console.log('Active badge type:', activeBadgeType);
    
    // Clear canvas
    ctx.clearRect(0, 0, dimensions.width, dimensions.height);

    // Create promises array to handle all badge rendering
    const renderPromises = [];

    // Add render tasks to the array
    if (showAudioBadge) {
      renderPromises.push((async () => {
        try {
          // Log the EXACT settings being used
          console.log('Rendering audio badge with settings:', actualAudioSettings);
          console.log('Audio badge size about to be used:', actualAudioSettings.size);
          
          // Render the audio badge - this now returns a dynamically sized canvas based on the image
          const result = await renderBadgeToCanvas("audio", actualAudioSettings);
          if (!result || !result.canvas) {
            console.error("Failed to get canvas for audio badge");
            return;
          }
          
          console.log('Result canvas dimensions:', result.canvas.width, 'x', result.canvas.height);
          
          // Calculate position based on center point - adjust for badge dimensions
          const percentX = actualAudioSettings.position?.percentX || 5;
          const percentY = actualAudioSettings.position?.percentY || 5;
          
          // Convert from percentage to absolute position
          const centerX = (percentX / 100) * dimensions.width;
          const centerY = (percentY / 100) * dimensions.height;
          
          // Calculate the top-left position by accounting for badge dimensions
          const posX = centerX - (result.canvas.width / 2);
          const posY = centerY - (result.canvas.height / 2);
          
          console.log(`Drawing audio badge at position: ${posX.toFixed(2)}, ${posY.toFixed(2)} with dimensions ${result.canvas.width}x${result.canvas.height}`);
          ctx.drawImage(result.canvas, posX, posY);
          
          // Highlight active badge with a non-visible indicator if it's currently selected
          if (activeBadgeType === "audio" && debugMode) {
            ctx.strokeStyle = '#4f46e5'; // Indigo color for highlight
            ctx.lineWidth = 2;
            ctx.strokeRect(posX - 2, posY - 2, result.canvas.width + 4, result.canvas.height + 4);
            
            // Draw center point marker for debugging
            if (debugMode) {
              ctx.fillStyle = '#ff0000';
              ctx.beginPath();
              ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
              ctx.fill();
            }
          }
        } catch (error) {
          console.error("Error rendering audio badge:", error);
        }
      })());
    }

    if (showResolutionBadge) {
      renderPromises.push((async () => {
        try {
          // Enhance resolution badge settings with utility functions if not already present
          const enhancedResolutionSettings = {
            ...actualResolutionSettings,
            getResolutionImagePath: actualResolutionSettings.getResolutionImagePath || getResolutionImagePath,
            getResolutionDisplayName: actualResolutionSettings.getResolutionDisplayName || getResolutionDisplayName
          };
          
          const result = await renderBadgeToCanvas("resolution", enhancedResolutionSettings);
          if (!result || !result.canvas) {
            console.error("Failed to get canvas for resolution badge");
            return;
          }
          
          // Calculate position based on center point - adjust for badge dimensions
          const percentX = actualResolutionSettings.position?.percentX || 5;
          const percentY = actualResolutionSettings.position?.percentY || 15;
          
          // Convert from percentage to absolute position
          const centerX = (percentX / 100) * dimensions.width;
          const centerY = (percentY / 100) * dimensions.height;
          
          // Calculate the top-left position by accounting for badge dimensions
          const posX = centerX - (result.canvas.width / 2);
          const posY = centerY - (result.canvas.height / 2);
          
          console.log(`Drawing resolution badge at position: ${posX.toFixed(2)}, ${posY.toFixed(2)} with dimensions ${result.canvas.width}x${result.canvas.height}`);
          ctx.drawImage(result.canvas, posX, posY);
          
          // Highlight active badge with a non-visible indicator if it's currently selected
          if (activeBadgeType === "resolution" && debugMode) {
            ctx.strokeStyle = '#4f46e5'; // Indigo color for highlight
            ctx.lineWidth = 2;
            ctx.strokeRect(posX - 2, posY - 2, result.canvas.width + 4, result.canvas.height + 4);
            
            // Draw center point marker for debugging
            if (debugMode) {
              ctx.fillStyle = '#ff0000';
              ctx.beginPath();
              ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
              ctx.fill();
            }
          }
        } catch (error) {
          console.error("Error rendering resolution badge:", error);
        }
      })());
    }

    if (showReviewBadge) {
      renderPromises.push((async () => {
        try {
          const result = await renderBadgeToCanvas("review", actualReviewSettings);
          if (!result || !result.canvas) {
            console.error("Failed to get canvas for review badge");
            return;
          }
          
          // Calculate position based on center point - adjust for badge dimensions
          const percentX = actualReviewSettings.position?.percentX || 5;
          const percentY = actualReviewSettings.position?.percentY || 25;
          
          // Convert from percentage to absolute position
          const centerX = (percentX / 100) * dimensions.width;
          const centerY = (percentY / 100) * dimensions.height;
          
          // Calculate the top-left position by accounting for badge dimensions
          const posX = centerX - (result.canvas.width / 2);
          const posY = centerY - (result.canvas.height / 2);
          
          console.log(`Drawing review badge at position: ${posX.toFixed(2)}, ${posY.toFixed(2)} with dimensions ${result.canvas.width}x${result.canvas.height}`);
          ctx.drawImage(result.canvas, posX, posY);
          
          // Highlight active badge with a non-visible indicator if it's currently selected
          if (activeBadgeType === "review" && debugMode) {
            ctx.strokeStyle = '#4f46e5'; // Indigo color for highlight
            ctx.lineWidth = 2;
            ctx.strokeRect(posX - 2, posY - 2, result.canvas.width + 4, result.canvas.height + 4);
            
            // Draw center point marker for debugging
            if (debugMode) {
              ctx.fillStyle = '#ff0000';
              ctx.beginPath();
              ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
              ctx.fill();
            }
          }
        } catch (error) {
          console.error("Error rendering review badge:", error);
        }
      })());
    }

    // Wait for all rendering to complete
    await Promise.all(renderPromises);
  };
  
  // Get badge settings for each type using our hook
  const { 
    badgeSettings: audioBadgeSettings, 
    saveBadgeSettings: saveAudioBadgeSettings,
    isLoading: isLoadingAudio
  } = useBadgeSettings<AudioBadgeSettings>("123", "audio");
  
  // Debug: Watch for changes to audioBadgeSettings
  useEffect(() => {
    console.log('Preview: audioBadgeSettings changed:', audioBadgeSettings);
  }, [audioBadgeSettings]);
  
  const { 
    badgeSettings: resolutionBadgeSettings, 
    saveBadgeSettings: saveResolutionBadgeSettings,
    isLoading: isLoadingResolution
  } = useBadgeSettings<ResolutionBadgeSettings>("123", "resolution");
  
  const { 
    badgeSettings: reviewBadgeSettings, 
    saveBadgeSettings: saveReviewBadgeSettings,
    isLoading: isLoadingReview
  } = useBadgeSettings<ReviewBadgeSettings>("123", "review");

  // Update loading state when all settings are loaded
  useEffect(() => {
    setLoading(isLoadingAudio || isLoadingResolution || isLoadingReview);
  }, [isLoadingAudio, isLoadingResolution, isLoadingReview]);
  
  // Debug output when settings change
  useEffect(() => {
    if (!loading) {
      console.log('Audio badge settings loaded:', audioBadgeSettings);
      console.log('Resolution badge settings loaded:', resolutionBadgeSettings);
      console.log('Review badge settings loaded:', reviewBadgeSettings);
    }
  }, [loading, audioBadgeSettings, resolutionBadgeSettings, reviewBadgeSettings]);
  
  // Function to immediately update the preview canvas
  const updatePreview = () => {
    if (canvasRef.current && posterDimensions.width > 50 && !loading) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('Forcing immediate preview update');
        // Clear the canvas and redraw all badges
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        renderBadges(ctx, posterDimensions);
      }
    }
  };

  // Call updatePreview whenever badge settings change
  useEffect(() => {
    updatePreview();
  }, [audioBadgeSettings, resolutionBadgeSettings, reviewBadgeSettings]);
  
  // Create wrapped save functions that force immediate updates
  const saveAudioBadgeSettingsWithUpdate = (settings: AudioBadgeSettings) => {
    saveAudioBadgeSettings(settings);
    // Force immediate update instead of waiting for effect
    setTimeout(updatePreview, 0);
  };
  
  const saveResolutionBadgeSettingsWithUpdate = (settings: ResolutionBadgeSettings) => {
    saveResolutionBadgeSettings(settings);
    // Force immediate update instead of waiting for effect
    setTimeout(updatePreview, 0);
  };
  
  const saveReviewBadgeSettingsWithUpdate = (settings: ReviewBadgeSettings) => {
    saveReviewBadgeSettings(settings);
    // Force immediate update instead of waiting for effect
    setTimeout(updatePreview, 0);
  };
  
  // Force canvas redraw when settings change, with debounce
  useEffect(() => {
    if (loading) return;
    
    // Use debouncing to prevent too frequent updates
    const debounceTimeout = setTimeout(() => {
      if (canvasRef.current && posterDimensions.width > 50) {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          renderBadges(ctx, posterDimensions);
        }
      }
    }, 300); // 300ms debounce
    
    return () => clearTimeout(debounceTimeout);
  }, [
    audioBadgeSettings, resolutionBadgeSettings, reviewBadgeSettings,
    showAudioBadge, showResolutionBadge, showReviewBadge,
    posterDimensions, loading
  ]);

  // Handle poster image loading and set dimensions
  const handlePosterLoad = (dimensions: PosterDimensions) => {
    console.log('Poster dimensions received from PosterPreview:', dimensions);
    setPosterDimensions(dimensions);
  };

  // Handle badge position changes
  const handleBadgePositionChange = (type: string, position: { percentX: number, percentY: number }) => {
    // Update the position for the appropriate badge type
    switch (type) {
      case "audio":
        saveAudioBadgeSettings({
          ...audioBadgeSettings,
          position
        });
        break;
      case "resolution":
        saveResolutionBadgeSettings({
          ...resolutionBadgeSettings,
          position
        });
        break;
      case "review":
        saveReviewBadgeSettings({
          ...reviewBadgeSettings,
          position
        });
        break;
    }

    // Force canvas redraw after position changes
    if (canvasRef.current && posterDimensions.width > 50) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('Redrawing badges after position change');
        renderBadges(ctx, posterDimensions);
      }
    }
  };

  // Handle badge type selection in controls
  const handleBadgeTypeChange = (type: string) => {
    setActiveBadgeType(type);
    
    // Force canvas redraw when active badge type changes
    if (canvasRef.current && posterDimensions.width > 50) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        console.log('Redrawing badges after badge type change');
        renderBadges(ctx, posterDimensions);
      }
    }
  };

  // Toggle between light and dark poster
  const togglePoster = () => {
    if (activePoster === "light") {
      setActivePoster("dark");
      setPosterImage(darkPoster);
    } else {
      setActivePoster("light");
      setPosterImage(lightPoster);
    }
  };

  // Save a badge as PNG with transparency
  const saveBadgeAsPng = async (type: string) => {
    try {
      let result;
      let bounds;
      
      // Use defaults if settings are not available
      const actualAudioSettings = audioBadgeSettings || defaultAudioBadgeSettings;
      const actualResolutionSettings = resolutionBadgeSettings || defaultResolutionBadgeSettings;
      const actualReviewSettings = reviewBadgeSettings || defaultReviewBadgeSettings;
      
      switch (type) {
        case "audio":
          result = await renderBadgeToCanvas("audio", actualAudioSettings);
          // Use the entire canvas as the bounds since we're now sizing it exactly to the image
          bounds = { 
            x: 0, 
            y: 0, 
            width: result.canvas.width, 
            height: result.canvas.height 
          };
          console.log(`Extracting audio badge with dimensions: ${result.canvas.width}x${result.canvas.height}`);
          break;
        case "resolution":
          // Enhance resolution settings with utility functions
          const enhancedResolutionSettings = {
            ...actualResolutionSettings,
            getResolutionImagePath: actualResolutionSettings.getResolutionImagePath || getResolutionImagePath,
            getResolutionDisplayName: actualResolutionSettings.getResolutionDisplayName || getResolutionDisplayName
          };
          result = await renderBadgeToCanvas("resolution", enhancedResolutionSettings);
          bounds = { 
            x: 0, 
            y: 0, 
            width: result.canvas.width, 
            height: result.canvas.height 
          };
          break;
        case "review":
          result = await renderBadgeToCanvas("review", actualReviewSettings);
          bounds = { 
            x: 0, 
            y: 0, 
            width: result.canvas.width, 
            height: result.canvas.height 
          };
          break;
        default:
          throw new Error(`Unknown badge type: ${type}`);
      }
      
      const pngData = extractBadgeWithTransparency(result.canvas, bounds);
      
      // Create a download link
      const link = document.createElement("a");
      link.href = pngData;
      link.download = `${type}-badge.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error(`Error saving ${type} badge:`, error);
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-3xl font-bold tracking-tight">Preview</h1>
      <p className="text-muted-foreground">Customize and preview your badges on a poster</p>
      
      <div className="flex flex-col md:flex-row gap-8">
        {/* Badge Settings Card (Left - 50%) */}
        <div className="w-full md:w-1/2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSliders className="w-5 h-5" />
                Badge Settings
              </CardTitle>
              <CardDescription>Customize badge appearance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Badge Type Toggles */}
                <div className="space-y-3">
                  <h3 className="text-lg font-medium">Display Badges</h3>
                  <div className="flex flex-col gap-3">
                    <BadgeToggles
                      displaySettings={{
                        showAudioBadge,
                        showResolutionBadge,
                        showReviewBadge,
                      }}
                      toggleBadge={(badge) => {
                        if (badge === 'showAudioBadge') setShowAudioBadge(!showAudioBadge);
                        if (badge === 'showResolutionBadge') setShowResolutionBadge(!showResolutionBadge);
                        if (badge === 'showReviewBadge') setShowReviewBadge(!showReviewBadge);
                      }}
                      loading={loading}
                    />
                  </div>
                </div>

                {/* Badge Controls */}
                <div className="space-y-3">
                  <h3 className="text-lg font-medium">Badge Settings</h3>
                  <BadgeControls 
                    userId="123" 
                    onBadgeTypeChange={handleBadgeTypeChange}
                    initialBadgeType="audio"
                    saveHandlers={{
                      audio: saveAudioBadgeSettingsWithUpdate,
                      resolution: saveResolutionBadgeSettingsWithUpdate,
                      review: saveReviewBadgeSettingsWithUpdate
                    }}
                  />
                </div>

                {/* Save Buttons */}
                <div className="space-y-3 pt-4">
                  <h3 className="text-lg font-medium">Export Badges</h3>
                  <div className="grid grid-cols-3 gap-2">
                    <Button 
                      variant="outline" 
                      className="w-full"
                      onClick={() => saveBadgeAsPng("audio")}
                      disabled={!showAudioBadge}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Audio Badge
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full"
                      onClick={() => saveBadgeAsPng("resolution")}
                      disabled={!showResolutionBadge}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Resolution Badge
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full"
                      onClick={() => saveBadgeAsPng("review")}
                      disabled={!showReviewBadge}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Review Badge
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Preview Card (Right - 50%) */}
        <div className="w-full md:w-1/2">
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ScanEye className="w-5 h-5" />
                Preview
              </CardTitle>
              <CardDescription>
                Poster Preview - Drag badges to position them
              </CardDescription>
              {/* Poster Switcher and Debug Mode Toggle */}
              <div className="mt-4 flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={togglePoster}
                >
                  Switch to {activePoster === "light" ? "Dark" : "Light"} Poster
                </Button>
                <Button 
                  variant={debugMode ? "secondary" : "outline"} 
                  size="sm" 
                  onClick={() => setDebugMode(!debugMode)}
                >
                  {debugMode ? "Disable" : "Enable"} Debug Mode
                </Button>
              </div>
            </CardHeader>
            <CardContent className="flex flex-col justify-center flex-grow items-center p-0 relative">
              <div ref={containerRef} className="relative w-full flex justify-center">
                {loading ? (
                  <div className="flex flex-col items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    <p className="mt-4 text-sm text-muted-foreground">Loading badge settings...</p>
                  </div>
                ) : (
                  <>
                    <FixedPosterPreview 
                      onPosterLoad={handlePosterLoad}
                      onBadgePositionChange={handleBadgePositionChange}
                      activeBadgeType={activeBadgeType}
                      renderBadges={renderBadges}
                      debugMode={debugMode}
                    />
                    <canvas 
                      ref={canvasRef} 
                      className="hidden" // Hidden canvas for debugging
                      width={posterDimensions.width || 300} 
                      height={posterDimensions.height || 300} 
                    />
                  </>
                )}
              </div>
              <p className="text-sm text-muted-foreground mt-2 absolute bottom-0">
                {activeBadgeType ? `Click and drag to position the ${activeBadgeType} badge` : "Select a badge type to position it"}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}