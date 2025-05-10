import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

export default function TestJellyfinApi() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Get Jellyfin settings
  const { data: settings } = useQuery({
    queryKey: ['jellyfin-settings', 1],
    queryFn: () => apiClient.getJellyfinSettings(1)
  });

  const testDirectApi = async () => {
    try {
      setError(null);
      if (!settings) {
        setError('No Jellyfin settings found');
        return;
      }

      const itemId = 'e3c1a2c52b19a723fb34dd4b0fbdf89d';
      const baseUrl = settings.jellyfin_url.replace(/\/$/, '');
      
      // Test different API endpoints
      const endpoints = [
        `${baseUrl}/Items/${itemId}`,
        `${baseUrl}/Users/${settings.jellyfin_user_id}/Items/${itemId}`,
      ];

      const results: any[] = [];

      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint, {
            headers: {
              'X-Emby-Token': settings.jellyfin_api_key,
              'Accept': 'application/json'
            }
          });

          const data = await response.json();
          results.push({
            endpoint,
            status: response.status,
            statusText: response.statusText,
            ok: response.ok,
            data: response.ok ? data : null,
            error: !response.ok ? data : null
          });
        } catch (err: any) {
          results.push({
            endpoint,
            error: err.message
          });
        }
      }

      setResult(results);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Test Jellyfin API</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h3 className="font-medium">Jellyfin Settings:</h3>
            {settings && (
              <pre className="bg-muted p-2 rounded text-sm">
                {JSON.stringify({
                  url: settings.jellyfin_url,
                  token: settings.jellyfin_api_key ? '***' + settings.jellyfin_api_key.slice(-4) : 'none',
                  user_id: settings.jellyfin_user_id
                }, null, 2)}
              </pre>
            )}
          </div>

          <Button onClick={testDirectApi}>Test Direct API</Button>

          {error && (
            <div className="text-red-500 font-medium">{error}</div>
          )}

          {result && (
            <div className="space-y-4">
              <h3 className="font-medium">API Response:</h3>
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
