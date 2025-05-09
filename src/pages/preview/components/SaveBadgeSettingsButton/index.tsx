import * as React from "react";
import { Button } from "@/components/ui/button";
import { Save } from "lucide-react";
import { toast } from "sonner";
import { AudioBadgeSettings } from "@/components/badges/types/AudioBadge";
import { ResolutionBadgeSettings } from "@/components/badges/types/ResolutionBadge";
import { ReviewBadgeSettings } from "@/components/badges/types/ReviewBadge";
import { renderBadgeToCanvas } from "@/services/badgeRenderer";
import { getSourceImageUrlForResolution } from "@/utils/resolutionUtils";
import { extractBadgeWithTransparency } from "@/services/badges/utils";

interface SaveBadgeSettingsButtonProps {
  displaySettings: {
    showAudioBadge: boolean;
    showResolutionBadge: boolean;
    showReviewBadge: boolean;
  };
  audioBadgeSettings: AudioBadgeSettings;
  resolutionBadgeSettings: ResolutionBadgeSettings;
  reviewBadgeSettings: ReviewBadgeSettings;
  userId: string;
}

const SaveBadgeSettingsButton: React.FC<SaveBadgeSettingsButtonProps> = ({
  displaySettings,
  audioBadgeSettings,
  resolutionBadgeSettings,
  reviewBadgeSettings,
  userId
}) => {
  const [loading, setLoading] = React.useState(false);

  // Function to save a badge file to the server
  const saveBadgeFileToServer = async (type: string, pngData: string) => {
    try {
      console.log(`Saving ${type} badge file to server...`);
      
      // API URL for badge files
      const url = `/api/badge-files/${userId}/${type}`;
      console.log(`Sending POST request to: ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imageData: pngData })
      });

      console.log(`Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Error response body: ${errorText}`);
        throw new Error(`Failed to save ${type} badge file: ${response.statusText}`);
      }

      const result = await response.json();
      console.log(`Saved ${type} badge file:`, result);
      return result;
    } catch (error) {
      console.error(`Error saving ${type} badge file:`, error);
      throw error;
    }
  };

  // Function to generate and save a badge file
  const generateAndSaveBadgeFile = async (type: string) => {
    try {
      console.log(`Generating ${type} badge file...`);
      let result;
      let bounds;
      
      switch (type) {
        case "audio":
          if (!displaySettings.showAudioBadge) return null;
          result = await renderBadgeToCanvas("audio", audioBadgeSettings);
          bounds = { 
            x: 0, 
            y: 0, 
            width: result.canvas.width, 
            height: result.canvas.height 
          };
          console.log(`Extracting audio badge with dimensions: ${result.canvas.width}x${result.canvas.height}`);
          break;
        case "resolution":
          if (!displaySettings.showResolutionBadge) return null;
          // Enhance resolution settings with utility functions
          const enhancedResolutionSettings = {
            ...resolutionBadgeSettings,
            directImageRender: false
          };
          
          // Get the proper image path for this resolution type
          try {
            const resolutionImageUrl = await getSourceImageUrlForResolution(resolutionBadgeSettings.resolutionType || '1080');
            console.log('Using resolution image URL for saving:', resolutionImageUrl);
            
            result = await renderBadgeToCanvas("resolution", enhancedResolutionSettings, resolutionImageUrl);
            bounds = { 
              x: 0, 
              y: 0, 
              width: result.canvas.width, 
              height: result.canvas.height 
            };
          } catch (error) {
            console.error("Error loading resolution badge image for saving:", error);
            // Fallback to text-based rendering
            result = await renderBadgeToCanvas("resolution", enhancedResolutionSettings);
            bounds = { 
              x: 0, 
              y: 0, 
              width: result.canvas.width, 
              height: result.canvas.height 
            };
          }
          break;
        case "review":
          if (!displaySettings.showReviewBadge) return null;
          result = await renderBadgeToCanvas("review", reviewBadgeSettings);
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

      // Only proceed if the badge is enabled and the result exists
      if (result) {
        const pngData = extractBadgeWithTransparency(result.canvas, bounds);
        return await saveBadgeFileToServer(type, pngData);
      }
      return null;
    } catch (error) {
      console.error(`Error generating and saving ${type} badge:`, error);
      throw error;
    }
  };

  // Function to save all badge settings to server
  const handleSaveAllBadgeSettings = async () => {
    setLoading(true);
    const toastId = toast.loading("Saving badge settings...");
    
    try {
      // 1. Save each badge to server and database
      const promises = [];
      
      // Save badge files to server
      if (displaySettings.showAudioBadge) {
        promises.push(generateAndSaveBadgeFile("audio"));
      }
      
      if (displaySettings.showResolutionBadge) {
        promises.push(generateAndSaveBadgeFile("resolution"));
      }
      
      if (displaySettings.showReviewBadge) {
        promises.push(generateAndSaveBadgeFile("review"));
      }
      
      // Wait for all badge files to be saved
      await Promise.all(promises);
      
      toast.success("Badge settings saved successfully!", { id: toastId });
    } catch (error) {
      console.error("Error saving badge settings:", error);
      toast.error("Failed to save badge settings", { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button 
      variant="default" 
      className="w-full"
      onClick={handleSaveAllBadgeSettings}
      disabled={loading || (!displaySettings.showAudioBadge && !displaySettings.showResolutionBadge && !displaySettings.showReviewBadge)}
    >
      <Save className="h-4 w-4 mr-2" />
      Save Badge Settings
    </Button>
  );
};

export default SaveBadgeSettingsButton;
