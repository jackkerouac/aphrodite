import React from 'react';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { ArrowUp, ArrowDown } from 'lucide-react';
import { reviewSources } from '../constants';

interface SourceSelectorProps {
  displaySources: string[];
  sourceOrder: string[];
  handleArrayChange: (key: string, value: string[]) => void;
}

const SourceSelector: React.FC<SourceSelectorProps> = ({
  displaySources,
  sourceOrder,
  handleArrayChange
}) => {
  // Ensure arrays are defined
  const sources = Array.isArray(sourceOrder) ? sourceOrder : reviewSources;
  const selected = Array.isArray(displaySources) ? displaySources : [];
  
  const toggleSource = (source: string) => {
    if (selected.includes(source)) {
      handleArrayChange('display_sources', selected.filter(s => s !== source));
    } else {
      handleArrayChange('display_sources', [...selected, source]);
    }
  };

  const moveSourceUp = (source: string) => {
    const index = sources.indexOf(source);
    if (index > 0) {
      const newOrder = [...sources];
      newOrder[index] = newOrder[index - 1];
      newOrder[index - 1] = source;
      handleArrayChange('source_order', newOrder);
    }
  };

  const moveSourceDown = (source: string) => {
    const index = sources.indexOf(source);
    if (index < sources.length - 1) {
      const newOrder = [...sources];
      newOrder[index] = newOrder[index + 1];
      newOrder[index + 1] = source;
      handleArrayChange('source_order', newOrder);
    }
  };

  return (
    <div className="space-y-3">
      <div>
        <Label className="text-base">Review Sources</Label>
        <p className="text-xs text-muted-foreground mt-1">
          Select which review sources to display and their order of preference.
        </p>
      </div>
      
      <div className="space-y-2 border rounded-md p-4">
        {sources.map((source) => (
          <div key={source} className="flex items-center space-x-2 justify-between">
            <div className="flex items-center space-x-2">
              <Checkbox 
                id={`source-${source}`}
                checked={selected.includes(source)}
                onCheckedChange={() => toggleSource(source)}
              />
              <Label 
                htmlFor={`source-${source}`}
                className="cursor-pointer"
              >
                {source}
              </Label>
            </div>
            <div className="flex space-x-1">
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-7 w-7"
                onClick={() => moveSourceUp(source)}
                disabled={sources.indexOf(source) === 0}
              >
                <ArrowUp className="h-4 w-4" />
                <span className="sr-only">Move Up</span>
              </Button>
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-7 w-7"
                onClick={() => moveSourceDown(source)}
                disabled={sources.indexOf(source) === sources.length - 1}
              >
                <ArrowDown className="h-4 w-4" />
                <span className="sr-only">Move Down</span>
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SourceSelector;
