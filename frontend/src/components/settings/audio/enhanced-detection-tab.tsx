import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Plus, Trash2, Zap, AudioWaveform } from 'lucide-react';
import { useState } from 'react';
import { AudioSettings } from './types';

interface EnhancedDetectionTabProps {
  settings: AudioSettings;
  updateSetting: (path: string, value: any) => void;
}

export function EnhancedDetectionTab({ settings, updateSetting }: EnhancedDetectionTabProps) {
  const [newAtmosPattern, setNewAtmosPattern] = useState('');
  const [newDtsXPattern, setNewDtsXPattern] = useState('');
  const [newFallbackRule, setNewFallbackRule] = useState({ from: '', to: '' });
  const [newPriorityItem, setNewPriorityItem] = useState('');

  const addAtmosPattern = () => {
    if (newAtmosPattern.trim()) {
      const currentPatterns = settings.EnhancedDetection.atmos_detection_patterns;
      updateSetting('EnhancedDetection.atmos_detection_patterns', [...currentPatterns, newAtmosPattern.trim()]);
      setNewAtmosPattern('');
    }
  };

  const removeAtmosPattern = (index: number) => {
    const currentPatterns = settings.EnhancedDetection.atmos_detection_patterns;
    updateSetting('EnhancedDetection.atmos_detection_patterns', currentPatterns.filter((_, i) => i !== index));
  };

  const addDtsXPattern = () => {
    if (newDtsXPattern.trim()) {
      const currentPatterns = settings.EnhancedDetection.dts_x_detection_patterns;
      updateSetting('EnhancedDetection.dts_x_detection_patterns', [...currentPatterns, newDtsXPattern.trim()]);
      setNewDtsXPattern('');
    }
  };

  const removeDtsXPattern = (index: number) => {
    const currentPatterns = settings.EnhancedDetection.dts_x_detection_patterns;
    updateSetting('EnhancedDetection.dts_x_detection_patterns', currentPatterns.filter((_, i) => i !== index));
  };

  const addFallbackRule = () => {
    if (newFallbackRule.from.trim() && newFallbackRule.to.trim()) {
      const currentRules = settings.EnhancedDetection.fallback_rules;
      updateSetting('EnhancedDetection.fallback_rules', {
        ...currentRules,
        [newFallbackRule.from.trim()]: newFallbackRule.to.trim()
      });
      setNewFallbackRule({ from: '', to: '' });
    }
  };

  const removeFallbackRule = (key: string) => {
    const currentRules = { ...settings.EnhancedDetection.fallback_rules };
    delete currentRules[key];
    updateSetting('EnhancedDetection.fallback_rules', currentRules);
  };

  const addPriorityItem = () => {
    if (newPriorityItem.trim()) {
      const currentPriority = settings.EnhancedDetection.priority_order;
      updateSetting('EnhancedDetection.priority_order', [...currentPriority, newPriorityItem.trim()]);
      setNewPriorityItem('');
    }
  };

  const removePriorityItem = (index: number) => {
    const currentPriority = settings.EnhancedDetection.priority_order;
    updateSetting('EnhancedDetection.priority_order', currentPriority.filter((_, i) => i !== index));
  };

  const movePriorityItem = (index: number, direction: 'up' | 'down') => {
    const currentPriority = [...settings.EnhancedDetection.priority_order];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (newIndex >= 0 && newIndex < currentPriority.length) {
      [currentPriority[index], currentPriority[newIndex]] = [currentPriority[newIndex], currentPriority[index]];
      updateSetting('EnhancedDetection.priority_order', currentPriority);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Enhanced Audio Detection
        </CardTitle>
        <CardDescription>
          Configure advanced audio detection features including Dolby Atmos and DTS-X detection
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center space-x-2">
          <Switch
            id="enhanced-detection-enable"
            checked={settings.EnhancedDetection.enabled}
            onCheckedChange={(checked) => updateSetting('EnhancedDetection.enabled', checked)}
          />
          <Label htmlFor="enhanced-detection-enable">Enable Enhanced Detection</Label>
          <Badge variant={settings.EnhancedDetection.enabled ? "default" : "secondary"}>
            {settings.EnhancedDetection.enabled ? "Active" : "Disabled"}
          </Badge>
        </div>

        {/* Dolby Atmos Detection Patterns */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <AudioWaveform className="h-4 w-4" />
            <h4 className="text-lg font-semibold">Dolby Atmos Detection Patterns</h4>
            <Badge variant="outline">{settings.EnhancedDetection.atmos_detection_patterns.length} patterns</Badge>
          </div>
          
          <div className="space-y-2 border rounded-md p-4 max-h-40 overflow-y-auto">
            {settings.EnhancedDetection.atmos_detection_patterns.map((pattern, index) => (
              <div key={index} className="flex items-center gap-2">
                <Input
                  value={pattern}
                  onChange={(e) => {
                    const newPatterns = [...settings.EnhancedDetection.atmos_detection_patterns];
                    newPatterns[index] = e.target.value;
                    updateSetting('EnhancedDetection.atmos_detection_patterns', newPatterns);
                  }}
                  disabled={!settings.EnhancedDetection.enabled}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removeAtmosPattern(index)}
                  disabled={!settings.EnhancedDetection.enabled}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            <div className="flex items-center gap-2 pt-2 border-t">
              <Input
                value={newAtmosPattern}
                onChange={(e) => setNewAtmosPattern(e.target.value)}
                disabled={!settings.EnhancedDetection.enabled}
                placeholder="New Atmos pattern (e.g., 'truehd atmos')"
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={addAtmosPattern}
                disabled={!settings.EnhancedDetection.enabled || !newAtmosPattern.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* DTS-X Detection Patterns */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <AudioWaveform className="h-4 w-4" />
            <h4 className="text-lg font-semibold">DTS-X Detection Patterns</h4>
            <Badge variant="outline">{settings.EnhancedDetection.dts_x_detection_patterns.length} patterns</Badge>
          </div>
          
          <div className="space-y-2 border rounded-md p-4 max-h-40 overflow-y-auto">
            {settings.EnhancedDetection.dts_x_detection_patterns.map((pattern, index) => (
              <div key={index} className="flex items-center gap-2">
                <Input
                  value={pattern}
                  onChange={(e) => {
                    const newPatterns = [...settings.EnhancedDetection.dts_x_detection_patterns];
                    newPatterns[index] = e.target.value;
                    updateSetting('EnhancedDetection.dts_x_detection_patterns', newPatterns);
                  }}
                  disabled={!settings.EnhancedDetection.enabled}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removeDtsXPattern(index)}
                  disabled={!settings.EnhancedDetection.enabled}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            <div className="flex items-center gap-2 pt-2 border-t">
              <Input
                value={newDtsXPattern}
                onChange={(e) => setNewDtsXPattern(e.target.value)}
                disabled={!settings.EnhancedDetection.enabled}
                placeholder="New DTS-X pattern (e.g., 'dts:x')"
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={addDtsXPattern}
                disabled={!settings.EnhancedDetection.enabled || !newDtsXPattern.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Fallback Rules */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h4 className="text-lg font-semibold">Fallback Rules</h4>
            <Badge variant="outline">{Object.keys(settings.EnhancedDetection.fallback_rules).length} rules</Badge>
          </div>
          
          <div className="space-y-2 border rounded-md p-4 max-h-40 overflow-y-auto">
            {Object.entries(settings.EnhancedDetection.fallback_rules).map(([from, to]) => (
              <div key={from} className="flex items-center gap-2">
                <Input
                  value={from}
                  disabled
                  className="flex-1"
                />
                <span className="text-muted-foreground">→</span>
                <Input
                  value={to}
                  onChange={(e) => {
                    const newRules = { ...settings.EnhancedDetection.fallback_rules };
                    newRules[from] = e.target.value;
                    updateSetting('EnhancedDetection.fallback_rules', newRules);
                  }}
                  disabled={!settings.EnhancedDetection.enabled}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removeFallbackRule(from)}
                  disabled={!settings.EnhancedDetection.enabled}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            <div className="flex items-center gap-2 pt-2 border-t">
              <Input
                value={newFallbackRule.from}
                onChange={(e) => setNewFallbackRule(prev => ({ ...prev, from: e.target.value }))}
                disabled={!settings.EnhancedDetection.enabled}
                placeholder="From codec"
                className="flex-1"
              />
              <span className="text-muted-foreground">→</span>
              <Input
                value={newFallbackRule.to}
                onChange={(e) => setNewFallbackRule(prev => ({ ...prev, to: e.target.value }))}
                disabled={!settings.EnhancedDetection.enabled}
                placeholder="To codec"
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={addFallbackRule}
                disabled={!settings.EnhancedDetection.enabled || !newFallbackRule.from.trim() || !newFallbackRule.to.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Priority Order */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h4 className="text-lg font-semibold">Audio Priority Order</h4>
            <Badge variant="outline">{settings.EnhancedDetection.priority_order.length} items</Badge>
          </div>
          
          <div className="space-y-2 border rounded-md p-4 max-h-40 overflow-y-auto">
            {settings.EnhancedDetection.priority_order.map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground w-8">{index + 1}.</span>
                <Input
                  value={item}
                  onChange={(e) => {
                    const newPriority = [...settings.EnhancedDetection.priority_order];
                    newPriority[index] = e.target.value;
                    updateSetting('EnhancedDetection.priority_order', newPriority);
                  }}
                  disabled={!settings.EnhancedDetection.enabled}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => movePriorityItem(index, 'up')}
                  disabled={!settings.EnhancedDetection.enabled || index === 0}
                >
                  ↑
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => movePriorityItem(index, 'down')}
                  disabled={!settings.EnhancedDetection.enabled || index === settings.EnhancedDetection.priority_order.length - 1}
                >
                  ↓
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removePriorityItem(index)}
                  disabled={!settings.EnhancedDetection.enabled}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            
            <div className="flex items-center gap-2 pt-2 border-t">
              <span className="text-sm text-muted-foreground w-8">{settings.EnhancedDetection.priority_order.length + 1}.</span>
              <Input
                value={newPriorityItem}
                onChange={(e) => setNewPriorityItem(e.target.value)}
                disabled={!settings.EnhancedDetection.enabled}
                placeholder="New priority item"
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={addPriorityItem}
                disabled={!settings.EnhancedDetection.enabled || !newPriorityItem.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
