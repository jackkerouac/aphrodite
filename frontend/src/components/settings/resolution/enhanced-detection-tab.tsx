import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Plus, Trash2, GripVertical, Info, Zap } from 'lucide-react';
import { ResolutionSettings } from './types';

interface EnhancedDetectionTabProps {
  settings: ResolutionSettings;
  updateSetting: (section: keyof ResolutionSettings, key: string, value: any) => void;
}

export function EnhancedDetectionTab({ settings, updateSetting }: EnhancedDetectionTabProps) {
  const [newFallbackRule, setNewFallbackRule] = useState({ from: '', to: '' });
  const [newHdrPattern, setNewHdrPattern] = useState('');
  const [newDvPattern, setNewDvPattern] = useState('');

  // Helper functions for managing arrays and objects
  const addFallbackRule = () => {
    if (newFallbackRule.from && newFallbackRule.to) {
      updateSetting('enhanced_detection', 'fallback_rules', {
        ...settings.enhanced_detection.fallback_rules,
        [newFallbackRule.from]: newFallbackRule.to
      });
      setNewFallbackRule({ from: '', to: '' });
    }
  };

  const removeFallbackRule = (ruleKey: string) => {
    const newRules = { ...settings.enhanced_detection.fallback_rules };
    delete newRules[ruleKey];
    updateSetting('enhanced_detection', 'fallback_rules', newRules);
  };

  const addHdrPattern = () => {
    if (newHdrPattern && !settings.enhanced_detection.hdr_detection_patterns.includes(newHdrPattern)) {
      updateSetting('enhanced_detection', 'hdr_detection_patterns', [
        ...settings.enhanced_detection.hdr_detection_patterns,
        newHdrPattern
      ]);
      setNewHdrPattern('');
    }
  };

  const removeHdrPattern = (pattern: string) => {
    updateSetting('enhanced_detection', 'hdr_detection_patterns',
      settings.enhanced_detection.hdr_detection_patterns.filter(p => p !== pattern)
    );
  };

  const addDvPattern = () => {
    if (newDvPattern && !settings.enhanced_detection.dv_detection_patterns.includes(newDvPattern)) {
      updateSetting('enhanced_detection', 'dv_detection_patterns', [
        ...settings.enhanced_detection.dv_detection_patterns,
        newDvPattern
      ]);
      setNewDvPattern('');
    }
  };

  const removeDvPattern = (pattern: string) => {
    updateSetting('enhanced_detection', 'dv_detection_patterns',
      settings.enhanced_detection.dv_detection_patterns.filter(p => p !== pattern)
    );
  };

  const movePriorityItem = (index: number, direction: 'up' | 'down') => {
    const newOrder = [...settings.enhanced_detection.priority_order];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (newIndex >= 0 && newIndex < newOrder.length) {
      [newOrder[index], newOrder[newIndex]] = [newOrder[newIndex], newOrder[index]];
      updateSetting('enhanced_detection', 'priority_order', newOrder);
    }
  };

  return (
    <div className="space-y-6">
      {/* Master Toggle */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Enhanced Detection
          </CardTitle>
          <CardDescription>
            Advanced metadata analysis for automatic HDR, Dolby Vision, and resolution variant detection
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <Switch
              id="enable-enhanced-detection"
              checked={settings.enhanced_detection.enabled}
              onCheckedChange={(checked) => updateSetting('enhanced_detection', 'enabled', checked)}
            />
            <Label htmlFor="enable-enhanced-detection" className="font-medium">
              Enable Enhanced Detection
            </Label>
          </div>
          
          {!settings.enhanced_detection.enabled && (
            <Alert className="mt-4">
              <Info className="h-4 w-4" />
              <AlertDescription>
                Enhanced detection is disabled. The system will use legacy resolution mapping based on your manual image mappings above.
              </AlertDescription>
            </Alert>
          )}
          
          {settings.enhanced_detection.enabled && (
            <Alert className="mt-4">
              <Zap className="h-4 w-4" />
              <AlertDescription>
                Enhanced detection active! The system will automatically detect HDR, Dolby Vision, and handle resolution variants like 1440p.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Fallback Rules */}
      <Card>
        <CardHeader>
          <CardTitle>Resolution Fallback Rules</CardTitle>
          <CardDescription>
            Define fallback mappings for resolutions that don't have dedicated images
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            {Object.entries(settings.enhanced_detection.fallback_rules).map(([from, to]) => (
              <div key={from} className="flex items-center gap-2">
                <Input
                  value={from}
                  readOnly
                  disabled={!settings.enhanced_detection.enabled}
                  className="flex-1"
                  placeholder="Source resolution"
                />
                <span className="text-muted-foreground">→</span>
                <Input
                  value={to}
                  onChange={(e) => {
                    const newRules = { ...settings.enhanced_detection.fallback_rules };
                    newRules[from] = e.target.value;
                    updateSetting('enhanced_detection', 'fallback_rules', newRules);
                  }}
                  disabled={!settings.enhanced_detection.enabled}
                  className="flex-1"
                  placeholder="Target resolution"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removeFallbackRule(from)}
                  disabled={!settings.enhanced_detection.enabled}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            {/* Add new fallback rule */}
            <div className="flex items-center gap-2 pt-2 border-t">
              <Input
                value={newFallbackRule.from}
                onChange={(e) => setNewFallbackRule(prev => ({ ...prev, from: e.target.value }))}
                disabled={!settings.enhanced_detection.enabled}
                placeholder="Source resolution (e.g., 1440p)"
                className="flex-1"
              />
              <span className="text-muted-foreground">→</span>
              <Input
                value={newFallbackRule.to}
                onChange={(e) => setNewFallbackRule(prev => ({ ...prev, to: e.target.value }))}
                disabled={!settings.enhanced_detection.enabled}
                placeholder="Target resolution (e.g., 1080p)"
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={addFallbackRule}
                disabled={!settings.enhanced_detection.enabled || !newFallbackRule.from || !newFallbackRule.to}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* HDR Detection Patterns */}
      <Card>
        <CardHeader>
          <CardTitle>HDR Detection Patterns</CardTitle>
          <CardDescription>
            Metadata patterns used to identify HDR content in video streams
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {settings.enhanced_detection.hdr_detection_patterns.map((pattern) => (
              <Badge
                key={pattern}
                variant="secondary"
                className="flex items-center gap-1"
              >
                {pattern}
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-auto p-0 ml-1"
                  onClick={() => removeHdrPattern(pattern)}
                  disabled={!settings.enhanced_detection.enabled}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </Badge>
            ))}
          </div>
          
          <div className="flex gap-2">
            <Input
              value={newHdrPattern}
              onChange={(e) => setNewHdrPattern(e.target.value)}
              disabled={!settings.enhanced_detection.enabled}
              placeholder="Add HDR pattern (e.g., BT2020)"
              className="flex-1"
            />
            <Button
              type="button"
              onClick={addHdrPattern}
              disabled={!settings.enhanced_detection.enabled || !newHdrPattern}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Dolby Vision Detection Patterns */}
      <Card>
        <CardHeader>
          <CardTitle>Dolby Vision Detection Patterns</CardTitle>
          <CardDescription>
            Metadata patterns used to identify Dolby Vision content in video streams
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {settings.enhanced_detection.dv_detection_patterns.map((pattern) => (
              <Badge
                key={pattern}
                variant="secondary"
                className="flex items-center gap-1"
              >
                {pattern}
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-auto p-0 ml-1"
                  onClick={() => removeDvPattern(pattern)}
                  disabled={!settings.enhanced_detection.enabled}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </Badge>
            ))}
          </div>
          
          <div className="flex gap-2">
            <Input
              value={newDvPattern}
              onChange={(e) => setNewDvPattern(e.target.value)}
              disabled={!settings.enhanced_detection.enabled}
              placeholder="Add DV pattern (e.g., DVHE)"
              className="flex-1"
            />
            <Button
              type="button"
              onClick={addDvPattern}
              disabled={!settings.enhanced_detection.enabled || !newDvPattern}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Image Priority Order */}
      <Card>
        <CardHeader>
          <CardTitle>Image Priority Order</CardTitle>
          <CardDescription>
            Order of preference when multiple image variants are available (highest priority first)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {settings.enhanced_detection.priority_order.map((item, index) => (
              <div key={item} className="flex items-center gap-2 p-2 border rounded-md">
                <div className="flex flex-col">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => movePriorityItem(index, 'up')}
                    disabled={!settings.enhanced_detection.enabled || index === 0}
                    className="h-4 p-0"
                  >
                    ▲
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => movePriorityItem(index, 'down')}
                    disabled={!settings.enhanced_detection.enabled || index === settings.enhanced_detection.priority_order.length - 1}
                    className="h-4 p-0"
                  >
                    ▼
                  </Button>
                </div>
                <GripVertical className="h-4 w-4 text-muted-foreground" />
                <Badge variant="outline" className="flex-1">
                  {item}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  Priority {index + 1}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
