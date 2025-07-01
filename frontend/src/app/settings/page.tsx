'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { CheckCircle, Loader2 } from 'lucide-react';
import { ApiSettings } from '@/components/settings/api-settings';
import { EnhancedAudioSettings } from '@/components/settings/enhanced-audio-settings';
import { ResolutionSettings } from '@/components/settings/resolution-settings';
import { ReviewSettings } from '@/components/settings/review-settings';
import { AwardsSettings } from '@/components/settings/awards-settings';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

interface LoadingStatus {
  api: boolean;
  audio: boolean;
  resolution: boolean;
  review: boolean;
  awards: boolean;
}

const tabs = [
  { id: 'api', name: 'API', component: ApiSettings },
  { id: 'audio', name: 'Audio', component: EnhancedAudioSettings },
  { id: 'resolution', name: 'Resolution', component: ResolutionSettings },
  { id: 'review', name: 'Review', component: ReviewSettings },
  { id: 'awards', name: 'Awards', component: AwardsSettings },
];

const configFiles = [
  { file: 'settings.yaml', key: 'api' as keyof LoadingStatus, name: 'API Settings' },
  { file: 'badge_settings_audio.yml', key: 'audio' as keyof LoadingStatus, name: 'Audio Settings' },
  { file: 'badge_settings_resolution.yml', key: 'resolution' as keyof LoadingStatus, name: 'Resolution Settings' },
  { file: 'badge_settings_review.yml', key: 'review' as keyof LoadingStatus, name: 'Review Settings' },
  { file: 'badge_settings_awards.yml', key: 'awards' as keyof LoadingStatus, name: 'Awards Settings' },
];

export default function SettingsPage() {
  return (
    <Suspense fallback={<SettingsPageFallback />}>
      <SettingsPageContent />
    </Suspense>
  );
}

function SettingsPageFallback() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure your Aphrodite system settings
        </p>
      </div>
      <div className="flex items-center justify-center min-h-96">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    </div>
  );
}

function SettingsPageContent() {
  const [isLoading, setIsLoading] = useState(true);
  const [loadingStatus, setLoadingStatus] = useState<LoadingStatus>({
    api: false,
    audio: false,
    resolution: false,
    review: false,
    awards: false,
  });
  
  const searchParams = useSearchParams();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'api');

  const checkAllConfigs = async () => {
    setIsLoading(true);
    
    try {
      // Import the apiService instead of hardcoding URL
      const { apiService } = await import('@/services/api');
      
      // Get list of available config files
      const configData = await apiService.getConfigFiles();
      const availableFiles = configData.config_files || [];
      
      console.log('Available config files:', availableFiles);
      
      // Check each configuration file
      const checkPromises = configFiles.map(async ({ file, key, name }) => {
        try {
          if (availableFiles.includes(file)) {
            console.log(`Checking ${name}...`);
            // Just verify we can access the config
            await apiService.getConfig(file);
            setLoadingStatus(prev => ({ ...prev, [key]: true }));
            console.log(`✓ ${name} accessible`);
          } else {
            console.warn(`${name} not found, but that's ok`);
            setLoadingStatus(prev => ({ ...prev, [key]: true }));
          }
        } catch (error) {
          console.error(`Error checking ${name}:`, error);
          setLoadingStatus(prev => ({ ...prev, [key]: true }));
        }
      });
      
      await Promise.all(checkPromises);
      console.log('All configuration checks completed');
      
    } catch (error) {
      console.error('Error checking configuration files:', error);
      // Set all as loaded even on error
      setLoadingStatus({
        api: true,
        audio: true,
        resolution: true,
        review: true,
        awards: true,
      });
    } finally {
      // Add a small delay to show loading completion
      setTimeout(() => {
        setIsLoading(false);
      }, 300);
    }
  };

  useEffect(() => {
    checkAllConfigs();
  }, []);

  useEffect(() => {
    // Update URL when tab changes
    const params = new URLSearchParams();
    if (activeTab !== 'api') {
      params.set('tab', activeTab);
    }
    const newUrl = params.toString() ? `?${params.toString()}` : '/settings';
    router.replace(newUrl, { scroll: false });
  }, [activeTab, router]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure your Aphrodite system settings
          </p>
        </div>

        <div className="flex items-center justify-center min-h-96">
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
              <CardTitle>Loading settings...</CardTitle>
              <CardDescription>Checking configuration files</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {configFiles.map(({ name, key }) => (
                <div key={key} className="flex items-center space-x-2">
                  {loadingStatus[key] ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                  <span className="text-sm">{name}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure your Aphrodite system settings
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          {tabs.map(tab => (
            <TabsTrigger key={tab.id} value={tab.id}>
              {tab.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {tabs.map(tab => {
          const Component = tab.component;
          return (
            <TabsContent key={tab.id} value={tab.id}>
              <Card>
                <CardContent className="p-6">
                  <Component />
                </CardContent>
              </Card>
            </TabsContent>
          );
        })}
      </Tabs>
    </div>
  );
}