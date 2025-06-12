'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Wrench } from 'lucide-react';
import { 
  ConnectionCheck, 
  DatabaseOperations, 
  LogsViewer,
  useMaintenanceData 
} from '@/components/maintenance';

export default function MaintenancePage() {
  const [activeTab, setActiveTab] = useState('connection');
  const { loading, loadMaintenanceData } = useMaintenanceData();

  // Load initial data
  useEffect(() => {
    loadMaintenanceData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading maintenance tools...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Wrench className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Maintenance</h1>
        </div>
        <p className="text-muted-foreground text-lg">
          System management tools and diagnostics for Aphrodite v2
        </p>
      </div>

      {/* Maintenance Tools Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="connection" className="flex items-center gap-2">
            <span className="hidden sm:inline">Connection Check</span>
            <span className="sm:hidden">Connection</span>
          </TabsTrigger>
          <TabsTrigger value="database" className="flex items-center gap-2">
            <span className="hidden sm:inline">Database Operations</span>
            <span className="sm:hidden">Database</span>
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center gap-2">
            <span className="hidden sm:inline">Logs</span>
            <span className="sm:hidden">Logs</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="connection" className="space-y-6">
          <ConnectionCheck />
        </TabsContent>

        <TabsContent value="database" className="space-y-6">
          <DatabaseOperations />
        </TabsContent>

        <TabsContent value="logs" className="space-y-6">
          <LogsViewer />
        </TabsContent>
      </Tabs>
    </div>
  );
}
