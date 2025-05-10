import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

export default function TestJellyfinAuth() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Get Jellyfin settings
  const { data: settings } = useQuery({
    queryKey: ['jellyfin-settings', 1],
    queryFn: () => apiClient.getJellyfinSettings(1)
  });

  const testVariousAuthFormats = async () => {
    try {
      setError(null);
      if (!settings) {
        setError('No Jellyfin settings found');
        return;
      }

      const itemId = 'e3c1a2c52b19a723fb34dd4b0fbdf89d';
      const baseUrl = settings.jellyfin_url.replace(/\/$/, '');
      
      // Test different authentication formats
      const authFormats = [
        { name: 'X-Emby-Token', headers: { 'X-Emby-Token': settings.jellyfin_api_key } },
        { name: 'X-MediaBrowser-Token', headers: { 'X-MediaBrowser-Token': settings.jellyfin_api_key } },
        { name: 'Authorization (MediaBrowser)', headers: { 'Authorization': `MediaBrowser Token="${settings.jellyfin_api_key}"` } },
        { name: 'Authorization (Bearer)', headers: { 'Authorization': `Bearer ${settings.jellyfin_api_key}` } },
        { name: 'api_key parameter', url: `${baseUrl}/Items/${itemId}?api_key=${settings.jellyfin_api_key}`, headers: {} },
      ];

      const results: any[] = [];

      for (const format of authFormats) {
        try {
          const url = format.url || `${baseUrl}/Items/${itemId}`;
          const response = await fetch(url, {
            headers: {
              'Accept': 'application/json',
              ...format.headers
            }
          });

          const responseText = await response.text();
          let data;
          try {
            data = JSON.parse(responseText);
          } catch {
            data = responseText;
          }

          results.push({
            format: format.name,
            url,
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            data: data
          });
        } catch (err: any) {
          results.push({
            format: format.name,
            error: err.message
          });
        }
      }

      // Also test the Users endpoint
      const userEndpoints = [
        `${baseUrl}/Users/${settings.jellyfin_user_id}/Items/${itemId}`,
        `${baseUrl}/Users/${settings.jellyfin_user_id}`,
        `${baseUrl}/Users`
      ];

      for (const endpoint of userEndpoints) {
        try {
          const response = await fetch(endpoint, {
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
            data = responseText;
          }

          results.push({
            format: 'User endpoint with X-Emby-Token',
            url: endpoint,
            status: response.status,
            statusText: response.statusText,
            data: data
          });
        } catch (err: any) {
          results.push({
            url: endpoint,
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
          <CardTitle>Test Jellyfin Authentication</CardTitle>
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

          <Button onClick={testVariousAuthFormats}>Test All Auth Formats</Button>

          {error && (
            <div className="text-red-500 font-medium">{error}</div>
          )}

          {result && (
            <div className="space-y-4">
              <h3 className="font-medium">Authentication Test Results:</h3>
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
