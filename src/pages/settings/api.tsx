import React, { useState, useEffect } from 'react';
import { Loader2, Server, Film, Tv } from 'lucide-react';
import { toast } from 'sonner';
import ApiSettingsCard from '@/components/settings/api-settings-card';
import { useApiSettings } from '@/hooks/useApiSettings';
import { 
  apiServices, 
  serviceFields, 
  serviceIconNames, 
  serviceDescriptions 
} from '@/lib/api-services';
import { Button } from '@/components/ui/button.jsx';
import { 
  validationFunctions 
} from '@/lib/validation';

// Map icon names to actual icon components
const getIconComponent = (iconName: string) => {
  switch (iconName) {
    case 'server':
      return <Server className="h-5 w-5" />;
    case 'film':
      return <Film className="h-5 w-5" />;
    case 'tv':
      return <Tv className="h-5 w-5" />;
    default:
      return <Server className="h-5 w-5" />;
  }
};

export default function ApiSettings() {
  // Track which services are being displayed
  const [activeServices, setActiveServices] = useState<string[]>(['jellyfin']);
  const [fieldErrors, setFieldErrors] = useState<Record<string, Record<string, string>>>({
    jellyfin: {},
    omdb: {},
    tmdb: {},
    tvdb: {},
  });
  
  // Set up hooks for each active service
  const jellyfinSettings = useApiSettings({
    service: apiServices.jellyfin,
    fields: serviceFields.jellyfin,
  });
  
  const omdbSettings = useApiSettings({
    service: apiServices.omdb,
    fields: serviceFields.omdb,
  });
  
  const tmdbSettings = useApiSettings({
    service: apiServices.tmdb,
    fields: serviceFields.tmdb,
  });
  
  const tvdbSettings = useApiSettings({
    service: apiServices.tvdb,
    fields: serviceFields.tvdb,
  });
  
  // Map service IDs to their respective hooks
  const settingsHooks = {
    jellyfin: jellyfinSettings,
    omdb: omdbSettings,
    tmdb: tmdbSettings,
    tvdb: tvdbSettings,
  };

  // Validation function for all services
  const validateServiceSettings = (serviceId: string, values: Record<string, string>) => {
    // Only validate if the service is loaded and active
    const settings = settingsHooks[serviceId as keyof typeof settingsHooks];
    if (activeServices.includes(serviceId) && !settings.loading) {
      // Get the validation function for this service
      const validationFunction = validationFunctions[serviceId];
      if (validationFunction) {
        const { isValid, errors } = validationFunction(values);
        setFieldErrors(prev => ({
          ...prev,
          [serviceId]: errors,
        }));
        return { isValid, errors };
      }
    }
    return { isValid: true, errors: {} };
  };

  // Validate Jellyfin settings
  useEffect(() => {
    validateServiceSettings('jellyfin', jellyfinSettings.values);
  }, [jellyfinSettings.values, jellyfinSettings.loading]);

  // Validate OMDB settings
  useEffect(() => {
    validateServiceSettings('omdb', omdbSettings.values);
  }, [omdbSettings.values, omdbSettings.loading]);

  // Validate TMDB settings
  useEffect(() => {
    validateServiceSettings('tmdb', tmdbSettings.values);
  }, [tmdbSettings.values, tmdbSettings.loading]);

  // Validate TVDB settings
  useEffect(() => {
    validateServiceSettings('tvdb', tvdbSettings.values);
  }, [tvdbSettings.values, tvdbSettings.loading]);
  
  // Function to activate a service
  const activateService = (serviceId: string) => {
    if (!activeServices.includes(serviceId)) {
      setActiveServices([...activeServices, serviceId]);
      // Enforce loading the service settings
      settingsHooks[serviceId as keyof typeof settingsHooks].fetchSettings();
    }
  };
  
  // Available services that can be added
  const availableServices = Object.keys(apiServices).filter(
    serviceId => !activeServices.includes(serviceId)
  );

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">API Settings</h1>
      <p className="text-muted-foreground">
        Configure connections to external services used by Aphrodite.
      </p>
      
      {/* Active service cards */}
      <div className="space-y-6">
        {activeServices.map(serviceId => {
          const settings = settingsHooks[serviceId as keyof typeof settingsHooks];
          const service = apiServices[serviceId];
          
          if (settings.loading) {
            return (
              <div 
                key={serviceId}
                className="flex items-center justify-center p-6 bg-card rounded-lg border"
              >
                <Loader2 className="h-6 w-6 animate-spin mr-2" />
                <span>Loading {service.name} settings...</span>
              </div>
            );
          }
          
          if (settings.error) {
            return (
              <div 
                key={serviceId}
                className="p-6 bg-destructive/10 rounded-lg border border-destructive"
              >
                <h2 className="text-xl font-semibold mb-2">Error Loading {service.name} Settings</h2>
                <p className="text-muted-foreground">{settings.error.message}</p>
                <Button 
                  className="mt-4"
                  onClick={() => settings.fetchSettings()}
                >
                  Retry
                </Button>
              </div>
            );
          }
          
          return (
            <ApiSettingsCard
              key={serviceId}
              title={service.name}
              description={serviceDescriptions[serviceId]}
              icon={getIconComponent(serviceIconNames[serviceId])}
              fields={serviceFields[serviceId]}
              values={settings.values}
              onValuesChange={settings.handleValuesChange}
              onSave={settings.handleSave}
              onTest={settings.handleTest}
              saveDisabled={settings.isSaveDisabled}
              testDisabled={settings.isTestDisabled}
              fieldErrors={fieldErrors[serviceId]}
            />
          );
        })}
        
        {/* Add new API service section */}
        {availableServices.length > 0 && (
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t"></div>
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Add API Service
                </span>
              </div>
            </div>
            
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableServices.map(serviceId => (
                <Button
                  key={serviceId}
                  variant="outline"
                  className="h-auto py-4 flex flex-col items-center gap-2"
                  onClick={() => activateService(serviceId)}
                >
                  <div className="flex items-center gap-2">
                    {getIconComponent(serviceIconNames[serviceId])}
                    <span>{apiServices[serviceId].name}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {serviceDescriptions[serviceId]}
                  </p>
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
