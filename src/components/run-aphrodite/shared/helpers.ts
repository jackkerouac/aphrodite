import { UnifiedBadgeSettings } from "@/types/unifiedBadgeSettings";

/**
 * Prepare unified badge settings for job processing
 * 
 * @param badgeSettings - Array of badge settings to prepare
 * @param enabledBadgeTypes - Optional array of badge types that are enabled
 * @returns - Processed badge settings ready for job creation
 */
export const prepareBadgeSettingsForJob = (
  badgeSettings: UnifiedBadgeSettings[] = [], 
  enabledBadgeTypes?: string[]
): any[] => {
  if (!badgeSettings || badgeSettings.length === 0) {
    console.warn('No badge settings provided for job creation');
    return [];
  }

  // Filter badge settings based on enabled badge types if provided
  const settingsToProcess = enabledBadgeTypes 
    ? badgeSettings.filter(setting => enabledBadgeTypes.includes(setting.badge_type))
    : badgeSettings;
  
  console.log(`Processing ${settingsToProcess.length} badges for job creation`);
  
  if (settingsToProcess.length === 0) {
    console.warn('No enabled badge settings found');
    return [];
  }

  // Map each badge setting to the format expected by the API
  return settingsToProcess.map(setting => {
    try {
      // Create a complete deep copy to avoid reference issues
      const settingCopy = JSON.parse(JSON.stringify(setting));
      
      // Ensure required fields are present
      if (!settingCopy.badge_type) {
        console.error('Badge setting missing badge_type:', settingCopy);
        return null;
      }
      
      // Important: Make sure to preserve all original properties exactly as they are
      // Most importantly, preserve badge_size, background_color, and display_format
      console.log(`Preparing badge of type ${settingCopy.badge_type}:`, {
        badge_size: settingCopy.badge_size,
        background_color: settingCopy.background_color,
        badge_position: settingCopy.badge_position,
        display_format: settingCopy.display_format,
        border_radius: settingCopy.border_radius,
        edge_padding: settingCopy.edge_padding,
        background_opacity: settingCopy.background_opacity
      });
      
      // Ensure all critical fields are present and properly named
      if (!settingCopy.edge_padding && settingCopy.badge_size > 120) {
        // If edge_padding is missing but badge_size is large, add a proportional padding
        settingCopy.edge_padding = Math.round(settingCopy.badge_size * 0.15); 
        console.log(`Added edge_padding ${settingCopy.edge_padding} for large badge size ${settingCopy.badge_size}`);
      }
      
      // Return the complete badge settings without any modifications
      return settingCopy;
    } catch (error) {
      console.error('Error processing badge setting:', error);
      return null;
    }
  }).filter(Boolean); // Remove any null entries
};

// Helper function to fetch details of selected items
export const fetchSelectedItemsDetails = async (itemIds: string[]) => {
  // For now, we'll use the item IDs directly
  // In a real implementation, you might want to fetch full details
  return itemIds.map(id => ({
    id: id,
    name: `Media Item`  // Safe placeholder name
  }));
};
