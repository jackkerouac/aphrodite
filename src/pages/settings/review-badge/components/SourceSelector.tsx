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
  const toggleSource = (source: string) => {
    if (displaySources.includes(source)) {
      handleArrayChange('display_sources', displaySources.filter(s => s !== source));
    } else {
      handleArrayChange('display_sources', [...displaySources, source]);
    }
  };

  const moveSourceUp = (source: string) => {
    const index = sourceOrder.indexOf(source);
    if (index > 0) {
      const newOrder = [...sourceOrder];
      newOrder[index] = newOrder[index - 1];
      newOrder[index - 1] = source;
      handleArrayChange('source_order', newOrder);
    }
  };

  const moveSourceDown = (source: string) => {
    const index = sourceOrder.indexOf(source);
    if (index < sourceOrder.length - 1) {
      const newOrder = [...sourceOrder];
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
        {sourceOrder.map((source) => (
          <div key={source} className="flex items-center space-x-2 justify-between">
            <div className="flex items-center space-x-2">
              <Checkbox 
                id={`source-${source}`}
                checked={displaySources.includes(source)}
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
                disabled={sourceOrder.indexOf(source) === 0}
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
                disabled={sourceOrder.indexOf(source) === sourceOrder.length - 1}
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
