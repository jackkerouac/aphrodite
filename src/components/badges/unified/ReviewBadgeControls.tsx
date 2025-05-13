import React from 'react';
import { ReviewBadgeSettings, DisplayFormat } from '@/types/unifiedBadgeSettings';
import BaseBadgeControls from './BaseBadgeControls';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Plus, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { availableReviewSources } from '@/utils/reviewSourceUtils';

interface ReviewBadgeControlsProps {
  settings: ReviewBadgeSettings;
  onChange: (settings: ReviewBadgeSettings) => void;
}

/**
 * Controls specific to Review badges
 */
const ReviewBadgeControls: React.FC<ReviewBadgeControlsProps> = ({ settings, onChange }) => {
  // Handle change in review-specific properties
  const handlePropertyChange = (key: keyof ReviewBadgeSettings['properties'], value: any) => {
    onChange({
      ...settings,
      properties: {
        ...settings.properties,
        [key]: value
      }
    });
  };

  // Handle change in display format
  const handleDisplayFormatChange = (format: DisplayFormat) => {
    onChange({
      ...settings,
      display_format: format
    });
  };

  // Add a review source
  const addReviewSource = (source: string) => {
    const currentSources = settings.properties.review_sources || [];
    
    // Only add if not already in the list
    if (!currentSources.includes(source)) {
      handlePropertyChange('review_sources', [...currentSources, source]);
    }
  };

  // Remove a review source
  const removeReviewSource = (sourceToRemove: string) => {
    const currentSources = settings.properties.review_sources || [];
    handlePropertyChange(
      'review_sources',
      currentSources.filter(source => source !== sourceToRemove)
    );
  };

  return (
    <BaseBadgeControls
      settings={settings}
      onChange={onChange}
      badgeType="review"
    >
      {/* Review-specific controls */}
      <div className="space-y-4 border-t border-gray-200 pt-4 mt-4">
        {/* Display Format */}
        <div className="space-y-2 mb-4">
          <Label htmlFor="display_format">Display Format</Label>
          <Select
            value={settings.display_format}
            onValueChange={(value) => handleDisplayFormatChange(value as DisplayFormat)}
          >
            <SelectTrigger id="display_format">
              <SelectValue placeholder="Select format" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={DisplayFormat.Horizontal}>Horizontal</SelectItem>
              <SelectItem value={DisplayFormat.Vertical}>Vertical</SelectItem>
            </SelectContent>
          </Select>
          <div className="text-xs text-gray-500 mt-1">
            How multiple review scores should be arranged
          </div>
        </div>

        {/* Review Sources */}
        <div className="space-y-2">
          <Label>Review Sources</Label>
          
          <div className="flex flex-wrap gap-2 mt-2 mb-4">
            {(settings.properties.review_sources || []).map((source) => (
              <div key={source} className="flex items-center bg-gray-100 rounded-md px-2 py-1">
                <span className="text-sm">{source}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 ml-1"
                  onClick={() => removeReviewSource(source)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
          
          <div className="flex items-center gap-2">
            <Select
              onValueChange={(value) => {
                addReviewSource(value);
              }}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Add source" />
              </SelectTrigger>
              <SelectContent>
                {availableReviewSources.map((source) => (
                  <SelectItem key={source.value} value={source.value}>
                    {source.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                // Get current selected value and add it
                const select = document.querySelector('select[name="add-source"]');
                if (select && select.value) {
                  addReviewSource(select.value);
                }
              }}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="text-xs text-gray-500 mt-1">
            Sources for review scores to display in the badge
          </div>
        </div>

        {/* Score Type display information */}
        <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded-md">
          <p className="text-sm">All review scores will be displayed as percentages (e.g., 75%)</p>
        </div>
      </div>
    </BaseBadgeControls>
  );
};

export default ReviewBadgeControls;
