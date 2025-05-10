import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

export default function TestJellyfinEndpoints() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Get Jellyfin settings
  const { data: settings } = useQuery({
    queryKey: ['jellyfin-settings', 1],
    queryFn: () => apiClient.getJellyfinSettings(1)
  });

  const testEndpoints = async () => {
    try {
      setError(null);
      if (!settings) {
        setError('No Jellyfin settings found');
        return;
      }

      const itemId = 'e3c1a2c52b19a723fb34dd4b0fbdf89d';
      const baseUrl = settings.jellyfin_url.replace(/\/$/, '');
      
      // Test different endpoints with X-Emby-Token
      const endpoints = [
        {
          name: 'System Info',
          url: `${baseUrl}/System/Info`
        },
        {
          name: 'Users',
          url: `${baseUrl}/Users`
        },
        {
          name: 'Current User',
          url: `${baseUrl}/Users/${settings.jellyfin_user_id}`
        },
        {
          name: 'Item Direct',
          url: `${baseUrl}/Items/${itemId}`
        },
        {
          name: 'User Item',
          url: `${baseUrl}/Users/${settings.jellyfin_user_id}/Items/${itemId}`
        },
        {
          name: 'User Items List',
          url: `${baseUrl}/Users/${settings.jellyfin_user_id}/Items?Limit=1`
        },
        {
          name: 'Item Image',
          url: `${baseUrl}/Items/${itemId}/Images/Primary`
        }
      ];

      const results: any[] = [];

      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint.url, {
            headers: {
              'X-Emby-Token': settings.jellyfin_api_key,
              'Accept': 'application/json'
            }
          });

          const responseText = await response.text();
          let data;
          try {
            data = JSON.parse(responseText);
          } catch {
            data = responseText.length > 500 ? responseText.substring(0, 500) + '...' : responseText;
          }

          results.push({
            name: endpoint.name,
            url: endpoint.url,
            status: response.status,
            statusText: response.statusText,
            contentType: response.headers.get('content-type'),
            data: data
          });
        } catch (err: any) {
          results.push({
            name: endpoint.name,
            url: endpoint.url,
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
          <CardTitle>Test Jellyfin Endpoints</CardTitle>
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

          <Button onClick={testEndpoints}>Test Endpoints</Button>

          {error && (
            <div className="text-red-500 font-medium">{error}</div>
          )}

          {result && (
            <div className="space-y-4">
              <h3 className="font-medium">Endpoint Test Results:</h3>
              <Textarea
                value={JSON.stringify(result, null, 2)}
                readOnly
                className="min-h-[600px] font-mono text-sm"
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
