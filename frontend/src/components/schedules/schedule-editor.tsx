'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Save, X, HelpCircle, Clock } from 'lucide-react';
import { apiService } from '@/services/api';
import { toast } from 'sonner';

interface Schedule {
  id: string;
  name: string;
  timezone: string;
  cron_expression: string;
  badge_types: string[];
  reprocess_all: boolean;
  enabled: boolean;
  target_libraries: string[];
  created_at: string;
  updated_at: string;
}

interface Library {
  id: string;
  name: string;
  type: string;
}

interface ScheduleEditorProps {
  editingSchedule?: Schedule | null;
  onSave: () => void;
  onCancel: () => void;
}

const TIMEZONES = [
  'UTC',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/Toronto',
  'Europe/London',
  'Europe/Berlin',
  'Asia/Tokyo',
  'Australia/Sydney',
];

const CRON_PRESETS = {
  hourly: { label: 'Every Hour', cron: '0 * * * *' },
  daily_2am: { label: 'Daily at 2:00 AM', cron: '0 2 * * *' },
  weekly: { label: 'Weekly (Sunday 2:00 AM)', cron: '0 2 * * 0' },
  monthly: { label: 'Monthly (1st day 2:00 AM)', cron: '0 2 1 * *' },
  every_6_hours: { label: 'Every 6 Hours', cron: '0 */6 * * *' },
  weekdays_2am: { label: 'Weekdays at 2:00 AM', cron: '0 2 * * 1-5' },
  weekends_2am: { label: 'Weekends at 2:00 AM', cron: '0 2 * * 6,0' },
  twice_daily: { label: 'Twice Daily (2:00 AM & 2:00 PM)', cron: '0 2,14 * * *' },
};

export function ScheduleEditor({ editingSchedule, onSave, onCancel }: ScheduleEditorProps) {
  const [formData, setFormData] = useState({
    name: '',
    timezone: 'UTC',
    cron_expression: '0 2 * * *',
    badge_types: [] as string[],
    reprocess_all: false,
    enabled: true,
    target_libraries: [] as string[],
  });

  const [availableBadgeTypes, setAvailableBadgeTypes] = useState<string[]>([]);
  const [availableLibraries, setAvailableLibraries] = useState<Library[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('custom');
  const [loading, setLoading] = useState(false);
  const [showCronHelp, setShowCronHelp] = useState(false);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        console.log('🔍 Loading schedule editor data...');
        
        // Load badge types
        const badgeTypesResponse = await apiService.getScheduleBadgeTypes();
        console.log('📊 Badge types response:', badgeTypesResponse);
        const badgeTypes = badgeTypesResponse?.badge_types || [];
        setAvailableBadgeTypes(badgeTypes);
        console.log('✅ Badge types loaded:', badgeTypes);
        
        // Load libraries (handle errors gracefully)
        try {
          const librariesResponse = await apiService.getScheduleLibraries();
          console.log('📊 Libraries response:', librariesResponse);
          const libraries = librariesResponse?.libraries || [];
          setAvailableLibraries(libraries);
          console.log('✅ Libraries loaded:', libraries);
        } catch (libraryError) {
          console.warn('⚠️ Failed to load libraries:', libraryError);
          // Don't show error toast for libraries - they might fail if Jellyfin isn't configured
          setAvailableLibraries([]);
        }
        
      } catch (error) {
        console.error('❌ Failed to load editor data:', error);
        toast.error('Failed to load configuration data');
      }
    };
    
    loadData();
  }, []);

  // Set form data when editing
  useEffect(() => {
    if (editingSchedule) {
      setFormData({
        name: editingSchedule.name,
        timezone: editingSchedule.timezone,
        cron_expression: editingSchedule.cron_expression,
        badge_types: editingSchedule.badge_types,
        reprocess_all: editingSchedule.reprocess_all,
        enabled: editingSchedule.enabled,
        target_libraries: editingSchedule.target_libraries,
      });
      
      // Try to match preset
      const matchingPreset = Object.entries(CRON_PRESETS).find(
        ([_, preset]) => preset.cron === editingSchedule.cron_expression
      );
      setSelectedPreset(matchingPreset ? matchingPreset[0] : 'custom');
    }
  }, [editingSchedule]);

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
    if (preset !== 'custom' && CRON_PRESETS[preset as keyof typeof CRON_PRESETS]) {
      setFormData(prev => ({
        ...prev,
        cron_expression: CRON_PRESETS[preset as keyof typeof CRON_PRESETS].cron
      }));
    }
  };

  const handleBadgeTypeToggle = (badgeType: string) => {
    setFormData(prev => ({
      ...prev,
      badge_types: prev.badge_types.includes(badgeType)
        ? prev.badge_types.filter(type => type !== badgeType)
        : [...prev.badge_types, badgeType]
    }));
  };

  const handleLibraryToggle = (libraryId: string) => {
    setFormData(prev => ({
      ...prev,
      target_libraries: prev.target_libraries.includes(libraryId)
        ? prev.target_libraries.filter(id => id !== libraryId)
        : [...prev.target_libraries, libraryId]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error('Schedule name is required');
      return;
    }
    
    if (!formData.cron_expression.trim()) {
      toast.error('Cron expression is required');
      return;
    }

    try {
      setLoading(true);
      
      if (editingSchedule) {
        await apiService.updateSchedule(editingSchedule.id, formData);
        toast.success('Schedule updated successfully');
      } else {
        await apiService.createSchedule(formData);
        toast.success('Schedule created successfully');
      }
      
      onSave();
    } catch (error) {
      console.error('Failed to save schedule:', error);
      toast.error('Failed to save schedule');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">
          {editingSchedule ? 'Edit Schedule' : 'Create New Schedule'}
        </h2>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={onCancel}>
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>
              Configure the schedule name and timing
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Schedule Name</Label>
              <Input
                id="name"
                placeholder="Enter schedule name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select value={formData.timezone} onValueChange={(value) => setFormData(prev => ({ ...prev, timezone: value }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIMEZONES.map((tz) => (
                    <SelectItem key={tz} value={tz}>{tz}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Quick Presets</Label>
              <Select value={selectedPreset} onValueChange={handlePresetChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="custom">Custom Expression</SelectItem>
                  {Object.entries(CRON_PRESETS).map(([key, preset]) => (
                    <SelectItem key={key} value={key}>{preset.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label htmlFor="cron">Cron Expression</Label>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowCronHelp(!showCronHelp)}
                >
                  <HelpCircle className="h-4 w-4" />
                </Button>
              </div>
              <Input
                id="cron"
                placeholder="0 2 * * *"
                value={formData.cron_expression}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, cron_expression: e.target.value }));
                  setSelectedPreset('custom');
                }}
                required
              />
              {showCronHelp && (
                <div className="p-3 bg-muted rounded text-sm">
                  <p className="font-medium mb-2">Cron Expression Format:</p>
                  <p className="font-mono">minute hour day month weekday</p>
                  <div className="mt-2 space-y-1">
                    <p>• <code>0 2 * * *</code> - Daily at 2:00 AM</p>
                    <p>• <code>0 */6 * * *</code> - Every 6 hours</p>
                    <p>• <code>0 2 * * 1-5</code> - Weekdays at 2:00 AM</p>
                    <p>• <code>0 2 1 * *</code> - Monthly on 1st day at 2:00 AM</p>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="enabled"
                checked={formData.enabled}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, enabled: checked }))}
              />
              <Label htmlFor="enabled">Enable Schedule</Label>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Processing Options</CardTitle>
            <CardDescription>
              Configure what will be processed when the schedule runs
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <Label>Badge Types to Apply</Label>
              {availableBadgeTypes.length === 0 ? (
                <div className="text-center py-4">
                  <Clock className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Loading badge types...</p>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-2">
                    {availableBadgeTypes.map((badgeType) => (
                      <div key={badgeType} className="flex items-center space-x-2">
                        <Checkbox
                          id={`badge-${badgeType}`}
                          checked={formData.badge_types.includes(badgeType)}
                          onCheckedChange={() => handleBadgeTypeToggle(badgeType)}
                        />
                        <Label htmlFor={`badge-${badgeType}`} className="capitalize">
                          {badgeType}
                        </Label>
                      </div>
                    ))}
                  </div>
                  {formData.badge_types.length === 0 && (
                    <p className="text-sm text-muted-foreground">
                      No badge types selected. Schedule will not process any items.
                    </p>
                  )}
                </>
              )}
            </div>

            <Separator />

            <div className="flex items-center space-x-2">
              <Switch
                id="reprocess_all"
                checked={formData.reprocess_all}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, reprocess_all: checked }))}
              />
              <div className="space-y-1">
                <Label htmlFor="reprocess_all">Reprocess All Items</Label>
                <p className="text-sm text-muted-foreground">
                  When enabled, processes all items regardless of existing 'aphrodite-overlay' metadata
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Target Libraries</CardTitle>
            <CardDescription>
              Select which Jellyfin libraries to process (leave all unchecked to process all libraries)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {availableLibraries.length === 0 ? (
                <div className="text-center py-4">
                  <Clock className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Loading libraries...</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    If this persists, check that Jellyfin is configured and running
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {availableLibraries.map((library) => (
                    <div key={library.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`library-${library.id}`}
                        checked={formData.target_libraries.includes(library.id)}
                        onCheckedChange={() => handleLibraryToggle(library.id)}
                      />
                      <Label htmlFor={`library-${library.id}`} className="flex items-center gap-2">
                        {library.name}
                        <Badge variant="outline" className="text-xs">
                          {library.type}
                        </Badge>
                      </Label>
                    </div>
                  ))}
                </div>
              )}
              {formData.target_libraries.length === 0 && availableLibraries.length > 0 && (
                <p className="text-sm text-muted-foreground mt-2">
                  No libraries selected. Schedule will process all movie and TV show libraries.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? (
              <>
                <Clock className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {editingSchedule ? 'Update Schedule' : 'Create Schedule'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
