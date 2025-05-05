import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { ApiError } from '@/lib/api-client';

// API service type
export interface ApiService {
  id: string;
  name: string;
  fetchSettings: () => Promise<Record<string, string>>;
  saveSettings: (values: Record<string, string>) => Promise<void>;
  testConnection: (values: Record<string, string>) => Promise<void>;
}

export interface ApiSettingField {
  id: string;
  label: string;
  placeholder: string;
  type?: string;
  description?: string;
  secure?: boolean;
  required?: boolean;
}

export interface UseApiSettingsProps {
  service: ApiService;
  fields: ApiSettingField[];
}

export interface UseApiSettingsReturn {
  values: Record<string, string>;
  loading: boolean;
  error: Error | null;
  saving: boolean;
  testing: boolean;
  connectionStatus: 'idle' | 'success' | 'error';
  fetchSettings: () => Promise<void>;
  handleValuesChange: (newValues: Record<string, string>) => void;
  handleSave: () => Promise<void>;
  handleTest: () => Promise<void>;
  isSaveDisabled: boolean;
  isTestDisabled: boolean;
}

export function useApiSettings({ service, fields }: UseApiSettingsProps): UseApiSettingsReturn {
  // State
  const [values, setValues] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Fetch settings
  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const serviceSettings = await service.fetchSettings();
      
      setValues(serviceSettings);
    } catch (error) {
      console.error(`Error fetching ${service.id} settings:`, error);
      setError(error as Error);
      
      // Only show a toast if it's not a 404 (not found) error
      // This is expected for new users who haven't set up their settings yet
      if (!(error instanceof ApiError && error.status === 404)) {
        toast.error(`Failed to load ${service.name} settings`);
      }
    } finally {
      setLoading(false);
    }
  }, [service]);

  // Handle input changes
  const handleValuesChange = useCallback((newValues: Record<string, string>) => {
    setValues(newValues);
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    try {
      setSaving(true);
      
      await service.saveSettings(values);
      toast.success(`${service.name} settings saved successfully`);
      
      return Promise.resolve();
    } catch (error) {
      console.error(`Error saving ${service.id} settings:`, error);
      toast.error(`Failed to save ${service.name} settings: ${(error as Error).message}`);
      return Promise.reject(error);
    } finally {
      setSaving(false);
    }
  }, [service, values]);

  // Handle test connection
  const handleTest = useCallback(async () => {
    try {
      setTesting(true);
      setConnectionStatus('idle');
      
      await service.testConnection(values);
      setConnectionStatus('success');
      toast.success(`${service.name} connection successful`);
      
      // Reset status after a delay
      setTimeout(() => setConnectionStatus('idle'), 5000);
      
      return Promise.resolve();
    } catch (error) {
      setConnectionStatus('error');
      toast.error(`${service.name} connection failed: ${(error as Error).message}`);
      
      // Reset status after a delay
      setTimeout(() => setConnectionStatus('idle'), 5000);
      
      return Promise.reject(error);
    } finally {
      setTesting(false);
    }
  }, [service, values]);

  // Required field validation
  const requiredFields = fields
    .filter(field => field.required !== false)
    .map(field => field.id);
  
  // Check if there are any empty required fields
  const hasEmptyRequiredFields = requiredFields.some(field => !values[field] || values[field].trim() === '');
  
  // We disable the save and test buttons if required fields are empty
  // This is a simple UI constraint, not a replacement for full validation
  const isSaveDisabled = hasEmptyRequiredFields;
  const isTestDisabled = hasEmptyRequiredFields;

  // Initial data fetch
  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  return {
    values,
    loading,
    error,
    saving,
    testing,
    connectionStatus,
    fetchSettings,
    handleValuesChange,
    handleSave,
    handleTest,
    isSaveDisabled,
    isTestDisabled,
  };
}
