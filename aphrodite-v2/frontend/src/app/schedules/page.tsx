'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SchedulesList } from '@/components/schedules/schedules-list';
import { ScheduleHistory } from '@/components/schedules/schedule-history';
import { ScheduleEditor } from '@/components/schedules/schedule-editor';

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

export default function SchedulesPage() {
  const [activeTab, setActiveTab] = useState('schedules');
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);

  const handleCreateSchedule = () => {
    setEditingSchedule(null);
    setActiveTab('editor');
  };

  const handleEditSchedule = (schedule: Schedule) => {
    setEditingSchedule(schedule);
    setActiveTab('editor');
  };

  const handleScheduleSave = () => {
    setEditingSchedule(null);
    setActiveTab('schedules');
  };

  const handleCancelEdit = () => {
    setEditingSchedule(null);
    setActiveTab('schedules');
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Schedules</h1>
        <p className="text-muted-foreground mt-2">
          Manage automated poster processing schedules
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="schedules">Schedules</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="editor">
            {editingSchedule ? 'Edit Schedule' : 'Create Schedule'}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="schedules">
          <SchedulesList
            onCreateSchedule={handleCreateSchedule}
            onEditSchedule={handleEditSchedule}
          />
        </TabsContent>

        <TabsContent value="history">
          <ScheduleHistory />
        </TabsContent>

        <TabsContent value="editor">
          <ScheduleEditor
            editingSchedule={editingSchedule}
            onSave={handleScheduleSave}
            onCancel={handleCancelEdit}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
