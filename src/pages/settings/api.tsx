import { useState, useEffect } from 'react';
import { Loader2, Server, Film, Database } from 'lucide-react';
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
    case 'database':
      return <Database className="h-5 w-5" />;
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
    anidb: {},
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
  
  const anidbSettings = useApiSettings({
    service: apiServices.anidb,
    fields: serviceFields.anidb,
  });
  
  // Map service IDs to their respective hooks
  const settingsHooks = {
    jellyfin: jellyfinSettings,
    omdb: omdbSettings,
    tmdb: tmdbSettings,
    anidb: anidbSettings,
  };
  
  // Load all available settings from the DB when the API page first renders
  useEffect(() => {
    console.log('[ApiSettings] Component mounted, fetching all active service settings');
    // Fetch settings for all active services
    activeServices.forEach(serviceId => {
      if (serviceId in settingsHooks) {
        console.log(`[ApiSettings] Fetching ${serviceId} settings on mount`);
        settingsHooks[serviceId as keyof typeof settingsHooks].fetchSettings();
      } else {
        console.error(`[ApiSettings] Service not found in settingsHooks: ${serviceId}`);
      }
    });
  }, []);  // empty deps → run once on mount

  // Validation function for all services
  const validateServiceSettings = (serviceId: string, values: Record<string, string>) => {
    console.log(`🚨 [ApiSettings] validateServiceSettings for ${serviceId}:`, values);
    
    // Only validate if the service exists in our hooks and is loaded and active
    if (!settingsHooks[serviceId as keyof typeof settingsHooks]) {
      console.log(`🚨 [ApiSettings] Service not found in settingsHooks: ${serviceId}`);
      return { isValid: true, errors: {} };
    }
    
    const settings = settingsHooks[serviceId as keyof typeof settingsHooks];
    if (activeServices.includes(serviceId) && !settings.loading) {
      // Get the validation function for this service
      const validationFunction = validationFunctions[serviceId];
      if (validationFunction) {
        console.log(`🚨 [ApiSettings] Using validation function for ${serviceId}`);
        const { isValid, errors } = validationFunction(values);
        console.log(`🚨 [ApiSettings] Validation result for ${serviceId}:`, { isValid, errors });
        
        setFieldErrors(prev => {
          const newErrors = {
            ...prev,
            [serviceId]: errors,
          };
          console.log(`🚨 [ApiSettings] Updated fieldErrors:`, newErrors);
          return newErrors;
        });
        return { isValid, errors };
      } else {
        console.log(`🚨 [ApiSettings] No validation function found for ${serviceId}`);
      }
    } else {
      console.log(`🚨 [ApiSettings] Skipping validation - service not active or still loading`);
    }
    return { isValid: true, errors: {} };
  };

  // Validate Jellyfin settings
  useEffect(() => {
    console.log(`🚨 [ApiSettings] Validating Jellyfin settings:`, jellyfinSettings.values);
    const result = validateServiceSettings('jellyfin', jellyfinSettings.values);
    console.log(`🚨 [ApiSettings] Jellyfin validation result:`, result);
  }, [jellyfinSettings.values, jellyfinSettings.loading]);

  // Validate OMDB settings
  useEffect(() => {
    validateServiceSettings('omdb', omdbSettings.values);
  }, [omdbSettings.values, omdbSettings.loading]);

  // Validate TMDB settings
  useEffect(() => {
    validateServiceSettings('tmdb', tmdbSettings.values);
  }, [tmdbSettings.values, tmdbSettings.loading]);
  
  // Validate AniDB settings
  useEffect(() => {
    validateServiceSettings('anidb', anidbSettings.values);
  }, [anidbSettings.values, anidbSettings.loading]);
  
  // Function to activate a service
  const activateService = (serviceId: string) => {
    if (!activeServices.includes(serviceId)) {
      setActiveServices([...activeServices, serviceId]);
      // Enforce loading the service settings
      if (serviceId in settingsHooks) {
        settingsHooks[serviceId as keyof typeof settingsHooks].fetchSettings();
      } else {
        console.error(`[ApiSettings] Cannot activate service - not found in settingsHooks: ${serviceId}`);
      }
    }
  };
  
  // Available services that can be added
  const availableServices = Object.keys(apiServices)
    .filter(serviceId => serviceId in settingsHooks) // Make sure the service exists in hooks
    .filter(serviceId => !activeServices.includes(serviceId));

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">API Settings</h1>
      <p className="text-muted-foreground">
        Configure connections to external services used by Aphrodite.
      </p>
      
      {/* Active service cards */}
      <div className="space-y-6">
        {activeServices.map(serviceId => {
          // Skip services that don't exist in our hooks
          if (!(serviceId in settingsHooks)) {
            console.error(`[ApiSettings] Cannot render card - service not found in settingsHooks: ${serviceId}`);
            return null;
          }
          
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
          
          // Debug log the values before rendering
          console.log(`📣 [ApiSettings] Rendering ${service.name} card with values:`, settings.values);
          console.log(`📣 [ApiSettings] ${service.name} fields:`, serviceFields[serviceId]);
          console.log(`📣 [ApiSettings] ${service.name} fieldErrors:`, fieldErrors[serviceId]);
          
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
