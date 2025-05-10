import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useJobWebSocket } from '@/hooks/useJobWebSocket';
import { useCreateJob } from '@/hooks/useCreateJob';
import { useToast } from '@/hooks/use-toast';

export function TestWebSocket() {
  const [jobId, setJobId] = useState<string>('');
  const { connected, jobStatus, jobProgress, jobError } = useJobWebSocket(jobId);
  const createJob = useCreateJob();
  const { toast } = useToast();

  const handleCreateTestJob = async () => {
    try {
      const result = await createJob.mutateAsync({
        libraryIds: ['test-library'],
        enabledBadges: ['resolution'],
        itemIds: ['test-item-1', 'test-item-2', 'test-item-3']
      });
      
      setJobId(result.jobId);
      toast({
        title: 'Test job created',
        description: `Job ID: ${result.jobId}`,
      });
    } catch (error) {
      toast({
        title: 'Error creating test job',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <h1 className="text-3xl font-bold">WebSocket Test</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>WebSocket Connection</CardTitle>
          <CardDescription>
            Status: {connected ? 'Connected' : 'Disconnected'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={handleCreateTestJob}
            disabled={createJob.isPending}
          >
            {createJob.isPending ? 'Creating...' : 'Create Test Job'}
          </Button>
        </CardContent>
      </Card>

      {jobId && (
        <Card>
          <CardHeader>
            <CardTitle>Job Status</CardTitle>
            <CardDescription>Job ID: {jobId}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {jobStatus && (
              <div>
                <h3 className="font-semibold">Status Update:</h3>
                <pre className="bg-muted p-2 rounded">
                  {JSON.stringify(jobStatus, null, 2)}
                </pre>
              </div>
            )}
            
            {jobProgress && (
              <div>
                <h3 className="font-semibold">Progress Update:</h3>
                <pre className="bg-muted p-2 rounded">
                  {JSON.stringify(jobProgress, null, 2)}
                </pre>
              </div>
            )}
            
            {jobError && (
              <div>
                <h3 className="font-semibold text-destructive">Error:</h3>
                <pre className="bg-muted p-2 rounded">
                  {JSON.stringify(jobError, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
