import React from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface ResolutionSelectorProps {
  selectedResolution: string;
  handleResolutionChange: (value: string) => void;
  resolutionOptions: string[];
}

const ResolutionSelector: React.FC<ResolutionSelectorProps> = ({
  selectedResolution,
  handleResolutionChange,
  resolutionOptions
}) => {
  return (
    <div className="space-y-3">
      <Label className="text-base" htmlFor="resolution-select">Resolution Type</Label>
      <Select value={selectedResolution} onValueChange={handleResolutionChange}>
        <SelectTrigger id="resolution-select">
          <SelectValue placeholder="Select a resolution" />
        </SelectTrigger>
        <SelectContent>
          {resolutionOptions.map((resolution) => (
            <SelectItem key={resolution} value={resolution}>
              {resolution}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export default ResolutionSelector;
