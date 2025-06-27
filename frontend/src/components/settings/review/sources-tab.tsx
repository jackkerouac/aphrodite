import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowUp, ArrowDown, GripVertical, CheckCircle, Info } from 'lucide-react';
import { ReviewSettings, ReviewSource, ReviewSourceSettings } from './types';
import { useState } from 'react';

interface SourcesTabProps {
  settings: ReviewSettings;
  reviewSources: ReviewSource[];
  reviewSourceSettings: ReviewSourceSettings;
  updateSetting: (section: keyof ReviewSettings, key: string, value: any) => void;
  updateReviewSource: (source: ReviewSource) => void;
  updateReviewSourceSettings: (key: keyof ReviewSourceSettings, value: any) => void;
  reorderSources: (newOrder: ReviewSource[]) => void;
}

export function SourcesTab({ 
  settings, 
  reviewSources, 
  reviewSourceSettings,
  updateSetting, 
  updateReviewSource,
  updateReviewSourceSettings,
  reorderSources
}: SourcesTabProps) {
  
  // Drag and drop state
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  
  const getConditionLabel = (conditions: string | null) => {
    if (!conditions) return '';
    try {
      const parsed = JSON.parse(conditions);
      return parsed.content_type || 'conditional';
    } catch (e) {
      return 'conditional';
    }
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
    console.log('📋 Drag started for index:', index);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (draggedIndex !== null && draggedIndex !== index) {
      setDragOverIndex(index);
    }
  };

  const handleDragLeave = () => {
    setDragOverIndex(null);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>, dropIndex: number) => {
    e.preventDefault();
    
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDraggedIndex(null);
      setDragOverIndex(null);
      return;
    }
    
    console.log('📋 Dropping item from index', draggedIndex, 'to index', dropIndex);
    
    const sortedSources = [...reviewSources].sort((a, b) => a.priority - b.priority);
    const draggedItem = sortedSources[draggedIndex];
    
    // Remove the dragged item and insert it at the new position
    const newOrder = [...sortedSources];
    newOrder.splice(draggedIndex, 1);
    newOrder.splice(dropIndex, 0, draggedItem);
    
    // Update priorities based on new order
    const updatedOrder = newOrder.map((source, index) => ({
      ...source,
      priority: index + 1,
      display_order: index + 1
    }));
    
    console.log('📋 New order after drop:', updatedOrder.map(s => ({name: s.source_name, priority: s.priority})));
    
    reorderSources(updatedOrder);
    
    // Reset drag state
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const movePriorityUp = (index: number) => {
    if (index > 0) {
      const newSources = [...reviewSources];
      [newSources[index], newSources[index - 1]] = [newSources[index - 1], newSources[index]];
      
      // Update priorities
      newSources.forEach((source, idx) => {
        source.priority = idx + 1;
        source.display_order = idx + 1;
      });
      
      reorderSources(newSources);
    }
  };

  const movePriorityDown = (index: number) => {
    if (index < reviewSources.length - 1) {
      const newSources = [...reviewSources];
      [newSources[index], newSources[index + 1]] = [newSources[index + 1], newSources[index]];
      
      // Update priorities
      newSources.forEach((source, idx) => {
        source.priority = idx + 1;
        source.display_order = idx + 1;
      });
      
      reorderSources(newSources);
    }
  };

  return (
    <div className="space-y-6">
      {/* Review Sources Status Notice */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-500" />
            Review Source Availability
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-2 text-sm">Not all review sources are currently functional. Here are the sources that are currently working:</p>
          <div className="flex flex-wrap gap-2 mb-2">
            <Badge variant="default" className="bg-green-500">IMDb</Badge>
            <Badge variant="default" className="bg-green-500">Metacritic</Badge>
            <Badge variant="default" className="bg-green-500">MyAnimeList</Badge>
            <Badge variant="default" className="bg-green-500">TMDb</Badge>
          </div>
          <p className="text-xs text-muted-foreground">Other sources are included for future functionality and testing purposes. I will get to them, I promise!</p>
        </CardContent>
      </Card>

      {/* Review Sources Control */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Review Sources Control
          </CardTitle>
          <CardDescription>
            Configure which review sources to display and their priority order
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Source Selection Settings */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="max-badges-display">Max Badges to Display</Label>
              <Input
                id="max-badges-display"
                type="number"
                min="1"
                max="10"
                value={reviewSourceSettings.max_badges_display}
                onChange={(e) => updateReviewSourceSettings('max_badges_display', parseInt(e.target.value) || 4)}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="selection-mode">Selection Mode</Label>
              <Select
                value={reviewSourceSettings.source_selection_mode}
                onValueChange={(value) => updateReviewSourceSettings('source_selection_mode', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="priority">Priority Order</SelectItem>
                  <SelectItem value="enabled_only">Enabled Only</SelectItem>
                  <SelectItem value="custom">Custom Logic</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center space-x-2 pt-6">
              <Switch
                id="show-percentage-only"
                checked={reviewSourceSettings.show_percentage_only}
                onCheckedChange={(checked) => updateReviewSourceSettings('show_percentage_only', checked)}
              />
              <Label htmlFor="show-percentage-only">Convert all to percentage format</Label>
            </div>
          </div>

          {/* Draggable Sources List */}
          <div className="bg-muted/30 rounded-lg p-4">
            <h4 className="text-lg font-semibold mb-3 flex items-center">
              <GripVertical className="w-4 h-4 mr-2 text-muted-foreground" />
              Review Sources (Drag to reorder)
            </h4>
            
            <div className="space-y-2">
              {reviewSources
                .sort((a, b) => a.priority - b.priority)
                .map((source, index) => {
                  const isDragging = draggedIndex === index;
                  const isDraggedOver = dragOverIndex === index;
                  
                  return (
                <Card 
                  key={source.id} 
                  className={`shadow-sm hover:shadow-md transition-shadow cursor-move ${
                    !source.enabled ? 'opacity-50' : ''
                  } ${
                    isDragging ? 'opacity-30 transform rotate-2' : ''
                  } ${
                    isDraggedOver ? 'border-blue-500 border-2 bg-blue-50' : ''
                  }`}
                  draggable
                  onDragStart={(e) => handleDragStart(e, index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, index)}
                  onDragEnd={handleDragEnd}
                >
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {/* Drag Handle */}
                        <GripVertical className="w-5 h-5 text-muted-foreground cursor-move" />
                        
                        {/* Priority Order */}
                        <Badge variant="default" className="w-8 text-center">
                          {source.priority}
                        </Badge>
                        
                        {/* Source Info */}
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{source.source_name}</span>
                            {source.conditions && (
                              <Badge variant="secondary" className="text-xs">
                                {getConditionLabel(source.conditions)}
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Max variants: {source.max_variants} • 
                            <span className={source.enabled ? 'text-green-600' : 'text-red-600'}>
                              {source.enabled ? 'Enabled' : 'Disabled'}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Controls */}
                      <div className="flex items-center space-x-2">
                        {/* Max Variants */}
                        <div className="space-y-1">
                          <Label className="text-xs">Max:</Label>
                          <Select
                            value={source.max_variants.toString()}
                            onValueChange={(value) => {
                              const updatedSource = { ...source, max_variants: parseInt(value) };
                              updateReviewSource(updatedSource);
                            }}
                          >
                            <SelectTrigger className="w-16">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="1">1</SelectItem>
                              <SelectItem value="2">2</SelectItem>
                              <SelectItem value="3">3</SelectItem>
                              <SelectItem value="4">4</SelectItem>
                              <SelectItem value="5">5</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        
                        {/* Move Controls */}
                        <div className="flex flex-col space-y-1">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => movePriorityUp(index)}
                            disabled={index === 0}
                            className="h-6 w-8 p-0"
                          >
                            <ArrowUp className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => movePriorityDown(index)}
                            disabled={index === reviewSources.length - 1}
                            className="h-6 w-8 p-0"
                          >
                            <ArrowDown className="h-3 w-3" />
                          </Button>
                        </div>
                        
                        {/* Enable/Disable Toggle */}
                        <Switch
                          checked={source.enabled}
                          onCheckedChange={(checked) => {
                            const updatedSource = { ...source, enabled: checked };
                            updateReviewSource(updatedSource);
                          }}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
                })}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
