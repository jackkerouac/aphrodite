import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, Info, RefreshCw, Clock, Database, Settings, ExternalLink, Container } from 'lucide-react';
import { SystemInfo, UpdateInfo } from './types';

interface SystemDetailsCardProps {
  systemInfo: SystemInfo;
  updateInfo: UpdateInfo | null;
  checkingUpdates: boolean;
  loading: boolean;
  onCheckUpdates: () => void;
}

function VersionInfoSection({ 
  version, 
  updateInfo, 
  checkingUpdates, 
  onCheckUpdates 
}: {
  version: string;
  updateInfo: UpdateInfo | null;
  checkingUpdates: boolean;
  onCheckUpdates: () => void;
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
        <div>
          <div className="font-semibold">Current Version</div>
          <div className="text-lg">v{version}</div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={onCheckUpdates}
          disabled={checkingUpdates}
          className="gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${checkingUpdates ? 'animate-spin' : ''}`} />
          {checkingUpdates ? 'Checking...' : 'Check Updates'}
        </Button>
      </div>

      {/* Update notifications */}
      {updateInfo?.update_available && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>Update available: v{updateInfo.latest_version}</span>
            {updateInfo.release_notes_url && (
              <Button variant="default" size="sm" asChild>
                <a href={updateInfo.release_notes_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-3 w-3 mr-1" />
                  View Release Notes
                </a>
              </Button>
            )}
          </AlertDescription>
        </Alert>
      )}

      {updateInfo && !updateInfo.update_available && (
        <Alert>
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>
            {updateInfo.message || 'You are running the latest version!'}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

function ExecutionModeSection({ executionMode }: { executionMode: string }) {
  const getBadgeVariant = (mode: string) => {
    switch (mode) {
      case 'Docker':
        return 'default';
      case 'Development':
        return 'secondary';
      case 'Installed Package':
        return 'default';
      default:
        return 'outline';
    }
  };

  const getIcon = (mode: string) => {
    if (mode === 'Docker') {
      return <Container className="h-8 w-8 text-blue-500" />;
    }
    return <Settings className="h-8 w-8 text-green-500" />;
  };

  return (
    <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
      <div>
        <div className="font-semibold">Execution Mode</div>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant={getBadgeVariant(executionMode)}>
            {executionMode}
          </Badge>
        </div>
      </div>
      <div className="text-right">
        {getIcon(executionMode)}
      </div>
    </div>
  );
}

function DatabaseSchemaSection({ schemaHash }: { schemaHash: string }) {
  return (
    <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
      <div>
        <div className="font-semibold">Database Schema</div>
        <div className="font-mono text-sm">{schemaHash}</div>
      </div>
      <div className="text-right">
        <Database className="h-8 w-8 text-primary" />
      </div>
    </div>
  );
}

function UptimeSection({ uptime }: { uptime: string }) {
  return (
    <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
      <div>
        <div className="font-semibold">Uptime</div>
        <div>{uptime}</div>
      </div>
      <div className="text-right">
        <Clock className="h-8 w-8 text-green-500" />
      </div>
    </div>
  );
}

export function SystemDetailsCard({
  systemInfo,
  updateInfo,
  checkingUpdates,
  loading,
  onCheckUpdates
}: SystemDetailsCardProps) {
  if (loading) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-6 w-6" />
            System Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Loading system information...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CheckCircle2 className="h-6 w-6" />
          System Details
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <VersionInfoSection
          version={systemInfo.version}
          updateInfo={updateInfo}
          checkingUpdates={checkingUpdates}
          onCheckUpdates={onCheckUpdates}
        />
        
        <ExecutionModeSection executionMode={systemInfo.execution_mode} />
        
        <DatabaseSchemaSection schemaHash={systemInfo.database_schema_hash} />
        
        <UptimeSection uptime={systemInfo.uptime} />
      </CardContent>
    </Card>
  );
}
