import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import apiClient from '@/lib/api-client';

export default function TestJobProcessing() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const processJob = async (jobId: number) => {
    try {
      setError(null);
      setLoading(true);
      
      // Trigger job processing
      const response = await fetch(`/api/jobs/${jobId}/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createTestJob = async () => {
    try {
      setError(null);
      setLoading(true);
      
      // Create a test job
      const response = await apiClient.jobs.create({
        user_id: 1,
        name: 'Test Job Manual Processing',
        items: [{
          jellyfin_item_id: 'e3c1a2c52b19a723fb34dd4b0fbdf89d',
          title: 'Test Item'
        }]
      });
      
      setResult({ jobCreated: response });
      
      // Process the job manually
      await processJob(response.id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Test Job Processing</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Button onClick={createTestJob} disabled={loading}>
              Create & Process Test Job
            </Button>
          </div>

          {loading && <div>Processing...</div>}

          {error && (
            <div className="text-red-500 font-medium">{error}</div>
          )}

          {result && (
            <div className="space-y-4">
              <h3 className="font-medium">Result:</h3>
              <Textarea
                value={JSON.stringify(result, null, 2)}
                readOnly
                className="min-h-[400px] font-mono text-sm"
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
