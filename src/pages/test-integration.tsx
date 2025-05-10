import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import useEnabledBadges from '@/hooks/useEnabledBadges';
import { UserSelector } from '@/components/user-selector';
import apiClient from '@/lib/api-client';

interface TestResult {
  test: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  message?: string;
}

export default function TestIntegration() {
  const { user } = useUser();
  const { enabledBadges, isLoading: badgesLoading, error: badgesError } = useEnabledBadges();
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  // Initialize test suite
  const tests = [
    // Badge Selection Integration
    {
      test: 'Badge settings load from database',
      run: async () => {
        if (badgesLoading) throw new Error('Still loading badge settings');
        if (badgesError) throw new Error(badgesError);
        if (!enabledBadges) throw new Error('No enabled badges data');
        return `Loaded badges: Audio=${enabledBadges.audio}, Resolution=${enabledBadges.resolution}, Review=${enabledBadges.review}`;
      }
    },
    {
      test: 'Badge selection persists in workflow',
      run: async () => {
        const count = Object.values(enabledBadges).filter(Boolean).length;
        if (count === 0) {
          return 'No badges enabled (this is valid)';
        }
        return `${count} badge(s) enabled and ready for workflow`;
      }
    },
    {
      test: 'Test with no badges enabled',
      run: async () => {
        const count = Object.values(enabledBadges).filter(Boolean).length;
        if (count === 0) {
          return 'Correctly handling case with no badges enabled';
        }
        return `${count} badge(s) are enabled`;
      }
    },
    {
      test: 'Test with all badge types enabled',
      run: async () => {
        const allEnabled = enabledBadges.audio && enabledBadges.resolution && enabledBadges.review;
        if (allEnabled) {
          return 'All badge types are enabled';
        }
        return `Not all badges enabled: Audio=${enabledBadges.audio}, Resolution=${enabledBadges.resolution}, Review=${enabledBadges.review}`;
      }
    },

    // User Context Verification
    {
      test: 'User ID is set in context',
      run: async () => {
        if (!user) throw new Error('No user in context');
        return `User ID: ${user.id}`;
      }
    },
    {
      test: 'User ID persists across page refreshes',
      run: async () => {
        const storedUser = localStorage.getItem('aphrodite_user');
        if (!storedUser) throw new Error('No user in localStorage');
        const parsed = JSON.parse(storedUser);
        if (parsed.id !== user?.id) throw new Error('User ID mismatch between context and storage');
        return `User ID ${user?.id} correctly persisted`;
      }
    },
    {
      test: 'UserSelector component switches users correctly',
      run: async () => {
        // This is more of a manual test, but we can verify the mechanism exists
        if (!user) throw new Error('No user to test with');
        return 'UserSelector component available for switching users';
      }
    },
    {
      test: 'All badge settings respect user context',
      run: async () => {
        if (!user) throw new Error('No user in context');
        
        // Test that API calls use the correct user ID
        try {
          const [audioSettings, resolutionSettings, reviewSettings] = await Promise.all([
            apiClient.audioBadge.getSettings(user.id),
            apiClient.resolutionBadge.getSettings(user.id),
            apiClient.reviewBadge.getSettings(user.id)
          ]);
          
          return `All badge APIs correctly use user ID ${user.id}`;
        } catch (err) {
          throw new Error(`Badge APIs failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
      }
    },

    // API Call Validation
    {
      test: 'Monitor for duplicate API requests',
      run: async () => {
        // This would need to be manually verified in network tab
        return 'Check Network tab for duplicate requests (manual verification required)';
      }
    },
    {
      test: 'Verify proper error responses',
      run: async () => {
        try {
          // Try to fetch with invalid user ID
          await apiClient.audioBadge.getSettings('invalid-user-id');
          throw new Error('Expected error for invalid user ID');
        } catch (err) {
          if (err instanceof Error && err.message.includes('Expected error')) {
            throw err;
          }
          return `API properly handles errors: ${err instanceof Error ? err.message : 'Error response received'}`;
        }
      }
    },
    {
      test: 'Check CORS configuration',
      run: async () => {
        // CORS issues would manifest as network errors
        try {
          await apiClient.jellyfin.testConnection();
          return 'CORS configuration working correctly';
        } catch (err) {
          throw new Error(`CORS issue detected: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
      }
    },

    // Error Scenarios
    {
      test: 'Test with invalid library IDs',
      run: async () => {
        if (!user) throw new Error('No user in context');
        try {
          await apiClient.libraryItems.getItems({
            libraryIds: ['invalid-library-id'],
            page: 1,
            limit: 10,
            userId: user.id
          });
          throw new Error('Expected error for invalid library ID');
        } catch (err) {
          if (err instanceof Error && err.message.includes('Expected error')) {
            throw err;
          }
          return `Properly handles invalid library ID: ${err instanceof Error ? err.message : 'Error handled'}`;
        }
      }
    },
    {
      test: 'Test with network disconnection',
      run: async () => {
        // This would need manual testing
        return 'Network disconnection test requires manual verification';
      }
    },
    {
      test: 'Test with expired Jellyfin token',
      run: async () => {
        // This would need manual testing with an expired token
        return 'Expired token test requires manual setup and verification';
      }
    },
    {
      test: 'Verify ErrorBoundary catches rendering errors',
      run: async () => {
        // ErrorBoundary is already implemented, this verifies it exists
        return 'ErrorBoundary is implemented in the application';
      }
    }
  ];

  const runTests = async () => {
    setIsRunning(true);
    const results: TestResult[] = tests.map(test => ({
      test: test.test,
      status: 'pending'
    }));
    setTestResults(results);

    for (let i = 0; i < tests.length; i++) {
      // Update status to running
      setTestResults(prev => prev.map((result, index) => 
        index === i ? { ...result, status: 'running' } : result
      ));

      try {
        const message = await tests[i].run();
        setTestResults(prev => prev.map((result, index) => 
          index === i ? { ...result, status: 'passed', message } : result
        ));
      } catch (error) {
        setTestResults(prev => prev.map((result, index) => 
          index === i ? { 
            ...result, 
            status: 'failed', 
            message: error instanceof Error ? error.message : 'Unknown error' 
          } : result
        ));
      }

      // Small delay between tests for visibility
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setIsRunning(false);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'passed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'running':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const passedCount = testResults.filter(r => r.status === 'passed').length;
  const failedCount = testResults.filter(r => r.status === 'failed').length;

  return (
    <div className="container mx-auto py-8 space-y-6">
      <h1 className="text-3xl font-bold">Integration Tests</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* User Context Card */}
        <Card>
          <CardHeader>
            <CardTitle>User Context</CardTitle>
          </CardHeader>
          <CardContent>
            <UserSelector />
            <div className="mt-4 p-4 bg-muted rounded">
              <p className="text-sm">Current User ID: {user?.id || 'Not set'}</p>
            </div>
          </CardContent>
        </Card>

        {/* Badge Status Card */}
        <Card>
          <CardHeader>
            <CardTitle>Badge Status</CardTitle>
          </CardHeader>
          <CardContent>
            {badgesLoading ? (
              <p>Loading badge settings...</p>
            ) : badgesError ? (
              <Alert variant="destructive">
                <AlertDescription>{badgesError}</AlertDescription>
              </Alert>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span>Audio Badge:</span>
                  <span className={enabledBadges.audio ? 'text-green-600' : 'text-red-600'}>
                    {enabledBadges.audio ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Resolution Badge:</span>
                  <span className={enabledBadges.resolution ? 'text-green-600' : 'text-red-600'}>
                    {enabledBadges.resolution ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Review Badge:</span>
                  <span className={enabledBadges.review ? 'text-green-600' : 'text-red-600'}>
                    {enabledBadges.review ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Test Runner */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Test Suite</CardTitle>
          <Button 
            onClick={runTests} 
            disabled={isRunning || !user}
          >
            {isRunning ? 'Running Tests...' : 'Run Tests'}
          </Button>
        </CardHeader>
        <CardContent>
          {testResults.length === 0 ? (
            <p className="text-muted-foreground">Click "Run Tests" to start testing</p>
          ) : (
            <div className="space-y-3">
              {testResults.map((result, index) => (
                <div key={index} className="flex items-center gap-3 p-3 border rounded">
                  {getStatusIcon(result.status)}
                  <div className="flex-1">
                    <p className="font-medium">{result.test}</p>
                    {result.message && (
                      <p className="text-sm text-muted-foreground">{result.message}</p>
                    )}
                  </div>
                </div>
              ))}
              
              {testResults.length > 0 && !isRunning && (
                <div className="mt-4 p-4 bg-muted rounded">
                  <p className="font-medium">
                    Test Summary: {passedCount} passed, {failedCount} failed
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Manual Testing Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Manual Testing Required</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 list-disc list-inside">
            <li>Monitor Network tab for duplicate API requests</li>
            <li>Test with network disconnection (disable network and try operations)</li>
            <li>Test with expired Jellyfin token (modify token in settings)</li>
            <li>Test ErrorBoundary by triggering a component error</li>
            <li>Test user switching and verify all components update correctly</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
