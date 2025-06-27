'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle, XCircle, Save } from 'lucide-react';
import { toast } from 'sonner';

// Dynamic API URL helper for production/remote deployments
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // In browser, always use current origin
    return window.location.origin;
  }
  // Server-side: only use environment variable, no hardcoded fallback
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (apiUrl === undefined || apiUrl === '') {
    // Empty means use relative URLs in production
    return '';
  }
  return apiUrl;
};

interface JellyfinConfig {
  url: string;
  api_key: string;
  user_id: string;
}

interface OmdbConfig {
  api_key: string;
  cache_expiration: number;
}

interface TmdbConfig {
  api_key: string;
  cache_expiration: number;
  language: string;
  region: string;
}

interface AnidbConfig {
  username: string;
  password: string;
  version: number;
  client_name: string;
  language: string;
  cache_expiration: number;
}

interface MdblistConfig {
  api_key: string;
  cache_expiration: number;
}

interface ConnectionStatus {
  success: boolean;
  message: string;
}

export function ApiSettings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // Connection testing states
  const [jellyfinTesting, setJellyfinTesting] = useState(false);
  const [jellyfinStatus, setJellyfinStatus] = useState<ConnectionStatus | null>(null);
  const [omdbTesting, setOmdbTesting] = useState(false);
  const [omdbStatus, setOmdbStatus] = useState<ConnectionStatus | null>(null);
  const [tmdbTesting, setTmdbTesting] = useState(false);
  const [tmdbStatus, setTmdbStatus] = useState<ConnectionStatus | null>(null);
  const [mdblistTesting, setMdblistTesting] = useState(false);
  const [mdblistStatus, setMdblistStatus] = useState<ConnectionStatus | null>(null);
  const [anidbTesting, setAnidbTesting] = useState(false);
  const [anidbStatus, setAnidbStatus] = useState<ConnectionStatus | null>(null);

  // Form data
  const [jellyfin, setJellyfin] = useState<JellyfinConfig>({
    url: 'https://jellyfin.example.com',
    api_key: '',
    user_id: ''
  });

  const [omdb, setOmdb] = useState<OmdbConfig>({
    api_key: '',
    cache_expiration: 60
  });

  const [tmdb, setTmdb] = useState<TmdbConfig>({
    api_key: '',
    cache_expiration: 60,
    language: 'en',
    region: ''
  });

  const [anidb, setAnidb] = useState<AnidbConfig>({
    username: '',
    password: '',
    version: 1,
    client_name: '',
    language: 'en',
    cache_expiration: 60
  });

  const [mdblist, setMdblist] = useState<MdblistConfig>({
    api_key: '',
    cache_expiration: 60
  });

  // Load settings
  const loadSettings = async () => {
    setLoading(true);
    
    try {
      console.log('Loading API settings from settings.yaml...');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/config/settings.yaml`);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log('No settings.yaml found yet, using defaults');
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('API settings loaded from settings.yaml:', data);
      
      if (data.config && data.config.api_keys) {
        const config = data.config;
        
        // Load Jellyfin settings
        if (config.api_keys.Jellyfin && config.api_keys.Jellyfin.length > 0) {
          const jellyfinConfig = config.api_keys.Jellyfin[0];
          setJellyfin({
            url: jellyfinConfig.url || '',
            api_key: jellyfinConfig.api_key || '',
            user_id: jellyfinConfig.user_id || ''
          });
        }

        // Load OMDB settings
        if (config.api_keys.OMDB && config.api_keys.OMDB.length > 0) {
          const omdbConfig = config.api_keys.OMDB[0];
          setOmdb({
            api_key: omdbConfig.api_key || '',
            cache_expiration: omdbConfig.cache_expiration || 60
          });
        }

        // Load TMDB settings
        if (config.api_keys.TMDB && config.api_keys.TMDB.length > 0) {
          const tmdbConfig = config.api_keys.TMDB[0];
          setTmdb({
            api_key: tmdbConfig.api_key || '',
            cache_expiration: tmdbConfig.cache_expiration || 60,
            language: tmdbConfig.language || 'en',
            region: tmdbConfig.region || ''
          });
        }

        // Load AniDB settings
        if (config.api_keys.aniDB) {
          const anidbConfig = config.api_keys.aniDB;
          if (Array.isArray(anidbConfig)) {
            const username = anidbConfig[0]?.username || '';
            const details = anidbConfig[1] || {};
            setAnidb({
              username,
              password: details.password || '',
              version: details.version || 1,
              client_name: details.client_name || '',
              language: details.language || 'en',
              cache_expiration: details.cache_expiration || 60
            });
          }
        }

        // Load MDBList settings
        if (config.api_keys.MDBList && config.api_keys.MDBList.length > 0) {
          const mdblistConfig = config.api_keys.MDBList[0];
          setMdblist({
            api_key: mdblistConfig.api_key || '',
            cache_expiration: mdblistConfig.cache_expiration || 60
          });
        }
        
        toast.success('API settings loaded successfully');
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      toast.error('Failed to load API settings');
    } finally {
      setLoading(false);
    }
  };

  // Save settings
  const saveSettings = async () => {
    setSaving(true);
    
    try {
      // Save all API settings to settings.yaml (single source of truth)
      const settingsObj = {
        api_keys: {
          Jellyfin: [{
            url: jellyfin.url,
            api_key: jellyfin.api_key,
            user_id: jellyfin.user_id
          }],
          OMDB: [{
            api_key: omdb.api_key,
            cache_expiration: omdb.cache_expiration
          }],
          TMDB: [{
            api_key: tmdb.api_key,
            cache_expiration: tmdb.cache_expiration,
            language: tmdb.language,
            region: tmdb.region || null
          }],
          aniDB: [
            { username: anidb.username },
            {
              password: anidb.password,
              version: anidb.version,
              client_name: anidb.client_name,
              language: anidb.language,
              cache_expiration: anidb.cache_expiration
            }
          ],
          MDBList: [{
            api_key: mdblist.api_key,
            cache_expiration: mdblist.cache_expiration
          }]
        }
      };

      const response = await fetch(`${getApiBaseUrl()}/api/v1/config/settings.yaml`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settingsObj),
      });

      if (!response.ok) {
        throw new Error('Failed to save API settings');
      }

      toast.success('API settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save API settings');
    } finally {
      setSaving(false);
    }
  };

  // Test Jellyfin connection
  const testJellyfinConnection = async () => {
    if (!jellyfin.url || !jellyfin.api_key || !jellyfin.user_id) {
      setJellyfinStatus({
        success: false,
        message: 'Please fill in all Jellyfin fields'
      });
      return;
    }

    setJellyfinTesting(true);
    setJellyfinStatus(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/config/test-jellyfin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: jellyfin.url,
          api_key: jellyfin.api_key,
          user_id: jellyfin.user_id
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setJellyfinStatus({
          success: true,
          message: data.message || 'Connection successful!'
        });
        
        // Auto-save on successful connection
        try {
          await saveSettings();
          setJellyfinStatus({
            success: true,
            message: (data.message || 'Connection successful!') + ' - Settings saved automatically!'
          });
        } catch (saveError) {
          setJellyfinStatus({
            success: true,
            message: (data.message || 'Connection successful!') + ' - Warning: Auto-save failed, please save manually.'
          });
        }
      } else {
        setJellyfinStatus({
          success: false,
          message: data.error || 'Connection failed'
        });
      }
    } catch (error) {
      setJellyfinStatus({
        success: false,
        message: 'Connection failed'
      });
    } finally {
      setJellyfinTesting(false);
    }
  };

  // Test MDBList connection
  const testMdblistConnection = async () => {
    if (!mdblist.api_key) {
      setMdblistStatus({
        success: false,
        message: 'Please enter an MDBList API key'
      });
      return;
    }

    setMdblistTesting(true);
    setMdblistStatus(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/config/test-mdblist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: mdblist.api_key
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMdblistStatus({
          success: true,
          message: data.message || 'Connection successful!'
        });
      } else {
        setMdblistStatus({
          success: false,
          message: data.error || 'Connection failed'
        });
      }
    } catch (error) {
      setMdblistStatus({
        success: false,
        message: 'Connection failed'
      });
    } finally {
      setMdblistTesting(false);
    }
  };

  // Test AniDB connection
  const testAnidbConnection = async () => {
    if (!anidb.username || !anidb.password) {
      setAnidbStatus({
        success: false,
        message: 'Please enter AniDB username and password'
      });
      return;
    }

    setAnidbTesting(true);
    setAnidbStatus(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/config/test-anidb`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: anidb.username,
          password: anidb.password,
          version: anidb.version,
          client_name: anidb.client_name,
          language: anidb.language
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setAnidbStatus({
          success: true,
          message: data.message || 'Connection successful!'
        });
      } else {
        setAnidbStatus({
          success: false,
          message: data.error || 'Connection failed'
        });
      }
    } catch (error) {
      setAnidbStatus({
        success: false,
        message: 'Connection failed'
      });
    } finally {
      setAnidbTesting(false);
    }
  };

  // Test OMDB connection
  const testOmdbConnection = async () => {
    if (!omdb.api_key) {
      setOmdbStatus({
        success: false,
        message: 'Please enter an OMDB API key'
      });
      return;
    }

    setOmdbTesting(true);
    setOmdbStatus(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/config/test-omdb`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: omdb.api_key
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setOmdbStatus({
          success: true,
          message: data.message || 'Connection successful!'
        });
      } else {
        setOmdbStatus({
          success: false,
          message: data.error || 'Connection failed'
        });
      }
    } catch (error) {
      setOmdbStatus({
        success: false,
        message: 'Connection failed'
      });
    } finally {
      setOmdbTesting(false);
    }
  };

  // Test TMDB connection
  const testTmdbConnection = async () => {
    if (!tmdb.api_key) {
      setTmdbStatus({
        success: false,
        message: 'Please enter a TMDB API key'
      });
      return;
    }

    setTmdbTesting(true);
    setTmdbStatus(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/config/test-tmdb`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: tmdb.api_key
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setTmdbStatus({
          success: true,
          message: data.message || 'Connection successful!'
        });
      } else {
        setTmdbStatus({
          success: false,
          message: data.error || 'Connection failed'
        });
      }
    } catch (error) {
      setTmdbStatus({
        success: false,
        message: 'Connection failed'
      });
    } finally {
      setTmdbTesting(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading API settings...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">API Settings</h2>
        <p className="text-muted-foreground">
          Configure connections to external services
        </p>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); saveSettings(); }} className="space-y-6">
        {/* Jellyfin Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Jellyfin Connection
              {jellyfinStatus && (
                <Badge variant={jellyfinStatus.success ? "default" : "destructive"}>
                  {jellyfinStatus.success ? "Connected" : "Error"}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              Configure your Jellyfin media server connection
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="jellyfin-url">Server URL</Label>
              <Input
                id="jellyfin-url"
                type="text"
                placeholder="https://jellyfin.example.com"
                value={jellyfin.url}
                onChange={(e) => setJellyfin(prev => ({ ...prev, url: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="jellyfin-api-key">API Key</Label>
              <Input
                id="jellyfin-api-key"
                type="text"
                placeholder="Your Jellyfin API key"
                value={jellyfin.api_key}
                onChange={(e) => setJellyfin(prev => ({ ...prev, api_key: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="jellyfin-user-id">User ID</Label>
              <Input
                id="jellyfin-user-id"
                type="text"
                placeholder="Your Jellyfin user ID"
                value={jellyfin.user_id}
                onChange={(e) => setJellyfin(prev => ({ ...prev, user_id: e.target.value }))}
              />
            </div>

            <div className="flex items-center gap-2">
              <Button 
                type="button"
                variant="outline"
                onClick={testJellyfinConnection}
                disabled={jellyfinTesting}
              >
                {jellyfinTesting ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : jellyfinStatus?.success ? (
                  <CheckCircle className="h-4 w-4 mr-2" />
                ) : jellyfinStatus?.success === false ? (
                  <XCircle className="h-4 w-4 mr-2" />
                ) : null}
                {jellyfinTesting ? 'Testing...' : 'Test Connection'}
              </Button>
              
              {jellyfinStatus && (
                <span className={`text-sm ${jellyfinStatus.success ? 'text-green-600' : 'text-red-600'}`}>
                  {jellyfinStatus.message}
                </span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* OMDB Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              OMDB API
              {omdbStatus && (
                <Badge variant={omdbStatus.success ? "default" : "destructive"}>
                  {omdbStatus.success ? "Connected" : "Error"}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              Open Movie Database for additional metadata
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="omdb-api-key">API Key</Label>
              <Input
                id="omdb-api-key"
                type="text"
                placeholder="Your OMDB API key"
                value={omdb.api_key}
                onChange={(e) => setOmdb(prev => ({ ...prev, api_key: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="omdb-cache">Cache Expiration (minutes)</Label>
              <Input
                id="omdb-cache"
                type="number"
                value={omdb.cache_expiration}
                onChange={(e) => setOmdb(prev => ({ ...prev, cache_expiration: parseInt(e.target.value) || 60 }))}
              />
            </div>

            <div className="flex items-center gap-2">
              <Button 
                type="button"
                variant="outline"
                onClick={testOmdbConnection}
                disabled={omdbTesting}
              >
                {omdbTesting ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : omdbStatus?.success ? (
                  <CheckCircle className="h-4 w-4 mr-2" />
                ) : omdbStatus?.success === false ? (
                  <XCircle className="h-4 w-4 mr-2" />
                ) : null}
                {omdbTesting ? 'Testing...' : 'Test Connection'}
              </Button>
              
              {omdbStatus && (
                <span className={`text-sm ${omdbStatus.success ? 'text-green-600' : 'text-red-600'}`}>
                  {omdbStatus.message}
                </span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* TMDB Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              TMDB API
              {tmdbStatus && (
                <Badge variant={tmdbStatus.success ? "default" : "destructive"}>
                  {tmdbStatus.success ? "Connected" : "Error"}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              The Movie Database for comprehensive movie and TV data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="tmdb-api-key">API Read Access Token</Label>
              <Input
                id="tmdb-api-key"
                type="text"
                placeholder="Your TMDB API Read Access Token"
                value={tmdb.api_key}
                onChange={(e) => setTmdb(prev => ({ ...prev, api_key: e.target.value }))}
              />
              <p className="text-xs text-muted-foreground">
                Use your TMDB API Read Access Token (Bearer token), not the API Key
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tmdb-language">Language</Label>
                <Input
                  id="tmdb-language"
                  type="text"
                  placeholder="en"
                  value={tmdb.language}
                  onChange={(e) => setTmdb(prev => ({ ...prev, language: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="tmdb-region">Region</Label>
                <Input
                  id="tmdb-region"
                  type="text"
                  placeholder="US"
                  value={tmdb.region}
                  onChange={(e) => setTmdb(prev => ({ ...prev, region: e.target.value }))}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="tmdb-cache">Cache Expiration (minutes)</Label>
              <Input
                id="tmdb-cache"
                type="number"
                value={tmdb.cache_expiration}
                onChange={(e) => setTmdb(prev => ({ ...prev, cache_expiration: parseInt(e.target.value) || 60 }))}
              />
            </div>

            <div className="flex items-center gap-2">
              <Button 
                type="button"
                variant="outline"
                onClick={testTmdbConnection}
                disabled={tmdbTesting}
              >
                {tmdbTesting ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : tmdbStatus?.success ? (
                  <CheckCircle className="h-4 w-4 mr-2" />
                ) : tmdbStatus?.success === false ? (
                  <XCircle className="h-4 w-4 mr-2" />
                ) : null}
                {tmdbTesting ? 'Testing...' : 'Test Connection'}
              </Button>
              
              {tmdbStatus && (
                <span className={`text-sm ${tmdbStatus.success ? 'text-green-600' : 'text-red-600'}`}>
                  {tmdbStatus.message}
                </span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* MDBList Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              MDBList API
              {mdblistStatus && (
                <Badge variant={mdblistStatus.success ? "default" : "destructive"}>
                  {mdblistStatus.success ? "Connected" : "Error"}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              MDBList for movie and TV show ratings and data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="mdblist-api-key">API Key</Label>
              <Input
                id="mdblist-api-key"
                type="text"
                placeholder="Your MDBList API key"
                value={mdblist.api_key}
                onChange={(e) => setMdblist(prev => ({ ...prev, api_key: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="mdblist-cache">Cache Expiration (minutes)</Label>
              <Input
                id="mdblist-cache"
                type="number"
                value={mdblist.cache_expiration}
                onChange={(e) => setMdblist(prev => ({ ...prev, cache_expiration: parseInt(e.target.value) || 60 }))}
              />
            </div>

            <div className="flex items-center gap-2">
              <Button 
                type="button"
                variant="outline"
                onClick={testMdblistConnection}
                disabled={mdblistTesting}
              >
                {mdblistTesting ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : mdblistStatus?.success ? (
                  <CheckCircle className="h-4 w-4 mr-2" />
                ) : mdblistStatus?.success === false ? (
                  <XCircle className="h-4 w-4 mr-2" />
                ) : null}
                {mdblistTesting ? 'Testing...' : 'Test Connection'}
              </Button>
              
              {mdblistStatus && (
                <span className={`text-sm ${mdblistStatus.success ? 'text-green-600' : 'text-red-600'}`}>
                  {mdblistStatus.message}
                </span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* AniDB Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              AniDB API
              {anidbStatus && (
                <Badge variant={anidbStatus.success ? "default" : "destructive"}>
                  {anidbStatus.success ? "Connected" : "Error"}
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              AniDB for anime database information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="anidb-username">Username</Label>
                <Input
                  id="anidb-username"
                  type="text"
                  placeholder="Your AniDB username"
                  value={anidb.username}
                  onChange={(e) => setAnidb(prev => ({ ...prev, username: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="anidb-password">Password</Label>
                <Input
                  id="anidb-password"
                  type="password"
                  placeholder="Your AniDB password"
                  value={anidb.password}
                  onChange={(e) => setAnidb(prev => ({ ...prev, password: e.target.value }))}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="anidb-client">Client Name</Label>
                <Input
                  id="anidb-client"
                  type="text"
                  placeholder="aphrodite"
                  value={anidb.client_name}
                  onChange={(e) => setAnidb(prev => ({ ...prev, client_name: e.target.value }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="anidb-language">Language</Label>
                <Input
                  id="anidb-language"
                  type="text"
                  placeholder="en"
                  value={anidb.language}
                  onChange={(e) => setAnidb(prev => ({ ...prev, language: e.target.value }))}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="anidb-version">Version</Label>
                <Input
                  id="anidb-version"
                  type="number"
                  value={anidb.version}
                  onChange={(e) => setAnidb(prev => ({ ...prev, version: parseInt(e.target.value) || 1 }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="anidb-cache">Cache Expiration (minutes)</Label>
                <Input
                  id="anidb-cache"
                  type="number"
                  value={anidb.cache_expiration}
                  onChange={(e) => setAnidb(prev => ({ ...prev, cache_expiration: parseInt(e.target.value) || 60 }))}
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button 
                type="button"
                variant="outline"
                onClick={testAnidbConnection}
                disabled={anidbTesting}
              >
                {anidbTesting ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : anidbStatus?.success ? (
                  <CheckCircle className="h-4 w-4 mr-2" />
                ) : anidbStatus?.success === false ? (
                  <XCircle className="h-4 w-4 mr-2" />
                ) : null}
                {anidbTesting ? 'Testing...' : 'Test Connection'}
              </Button>
              
              {anidbStatus && (
                <span className={`text-sm ${anidbStatus.success ? 'text-green-600' : 'text-red-600'}`}>
                  {anidbStatus.message}
                </span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button type="submit" disabled={saving}>
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </div>
  );
}