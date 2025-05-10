import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useUser } from '@/contexts/UserContext';
import { useCreateJob } from '@/hooks/useCreateJob';
import apiClient from '@/lib/api-client';

export default function TestJobs() {
  const { user } = useUser();
  const createJob = useCreateJob();
  const [testResults, setTestResults] = useState<any[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const runTests = async () => {
    if (!user) {
      setTestResults([{
        test: 'User Context',
        status: 'failed',
        message: 'No user context available'
      }]);
      return;
    }

    setIsRunning(true);
    const results = [];

    // Test 1: Create a job
    try {
      const job = await createJob.mutateAsync({
        user_id: parseInt(user.id),
        name: `Test Job - ${new Date().toISOString()}`,
        items: [
          { jellyfin_item_id: 'test-item-1', title: 'Test Item 1' },
          { jellyfin_item_id: 'test-item-2', title: 'Test Item 2' }
        ]
      });

      results.push({
        test: 'Create Job',
        status: 'passed',
        message: `Job created successfully with ID: ${job.id}`
      });

      // Test 2: Get job details
      try {
        const fetchedJob = await apiClient.jobs.getJob(job.id, user.id);
        results.push({
          test: 'Get Job Details',
          status: 'passed',
          message: `Job fetched: ${fetchedJob.name} (${fetchedJob.status})`
        });
      } catch (error) {
        results.push({
          test: 'Get Job Details',
          status: 'failed',
          message: error instanceof Error ? error.message : 'Failed to fetch job'
        });
      }

      // Test 3: Get job items
      try {
        const jobItems = await apiClient.jobs.getJobItems(job.id);
        results.push({
          test: 'Get Job Items',
          status: 'passed',
          message: `Found ${jobItems.items.length} items in job`
        });
      } catch (error) {
        results.push({
          test: 'Get Job Items',
          status: 'failed',
          message: error instanceof Error ? error.message : 'Failed to fetch job items'
        });
      }

      // Test 4: Start job processing
      try {
        const processResult = await apiClient.jobs.startProcessing(job.id);
        results.push({
          test: 'Start Job Processing',
          status: 'passed',
          message: processResult.message
        });
      } catch (error) {
        results.push({
          test: 'Start Job Processing',
          status: 'failed',
          message: error instanceof Error ? error.message : 'Failed to start processing'
        });
      }

    } catch (error) {
      results.push({
        test: 'Create Job',
        status: 'failed',
        message: error instanceof Error ? error.message : 'Failed to create job'
      });
    }

    // Test 5: Get user's jobs
    try {
      const userJobs = await apiClient.jobs.getJobs(user.id);
      results.push({
        test: 'Get User Jobs',
        status: 'passed',
        message: `Found ${userJobs.total} jobs for user`
      });
    } catch (error) {
      results.push({
        test: 'Get User Jobs',
        status: 'failed',
        message: error instanceof Error ? error.message : 'Failed to fetch user jobs'
      });
    }

    setTestResults(results);
    setIsRunning(false);
  };

  return (
    <div className="container mx-auto py-8 space-y-6">
      <h1 className="text-3xl font-bold">Job Management Tests</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Test Job Creation and Processing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded">
              <p className="text-sm">Current User ID: {user?.id || 'Not set'}</p>
            </div>
            
            <Button onClick={runTests} disabled={isRunning || !user}>
              {isRunning ? 'Running Tests...' : 'Run Tests'}
            </Button>

            {testResults.length > 0 && (
              <div className="space-y-3 mt-4">
                {testResults.map((result, index) => (
                  <div 
                    key={index} 
                    className={`p-3 border rounded ${
                      result.status === 'passed' ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
                    }`}
                  >
                    <p className="font-medium">{result.test}</p>
                    <p className="text-sm text-muted-foreground">{result.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Job API Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li>POST /api/jobs - Create a new job</li>
            <li>GET /api/jobs - Get all jobs for a user</li>
            <li>GET /api/jobs/:id - Get specific job details</li>
            <li>PUT /api/jobs/:id - Update job status</li>
            <li>GET /api/jobs/:id/items - Get job items</li>
            <li>POST /api/jobs/:id/process - Start processing a job</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
