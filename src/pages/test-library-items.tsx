import React, { useState } from 'react';
import { Button } from '@/components/ui';
import { fetchApi } from '@/lib/api-client';
import { useUser } from '@/contexts/UserContext';

export default function TestLibraryItems() {
  const { user } = useUser();
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const testFetch = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Test hardcoded request
      const url = `/library-items/${user?.id || '1'}?libraryIds=dummy-id&page=1&limit=50`;
      console.log('Testing fetch from:', url);
      
      const data = await fetchApi(url);
      console.log('Test response:', data);
      setResponse(data);
    } catch (err) {
      console.error('Test error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Test Library Items API</h1>
      
      <div className="mb-4">
        <p>User ID: {user?.id || 'Not loaded'}</p>
      </div>
      
      <Button onClick={testFetch} disabled={loading}>
        {loading ? 'Testing...' : 'Test Fetch'}
      </Button>
      
      {error && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
          Error: {error}
        </div>
      )}
      
      {response && (
        <div className="mt-4">
          <pre className="bg-gray-100 p-4 rounded overflow-auto">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
