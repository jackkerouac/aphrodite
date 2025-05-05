import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Label } from '@/components/ui/label.jsx';
import { Eye, EyeOff, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface ApiSettingField {
  id: string;
  label: string;
  placeholder: string;
  type?: string;
  description?: string;
  secure?: boolean;
  required?: boolean;
}

interface ApiSettingsCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  fields: ApiSettingField[];
  values: Record<string, string>;
  onValuesChange: (values: Record<string, string>) => void;
  onSave: () => Promise<void>;
  onTest: () => Promise<void>;
  saveDisabled?: boolean;
  testDisabled?: boolean;
  fieldErrors?: Record<string, string>;
}

export default function ApiSettingsCard({
  title,
  description,
  icon,
  fields,
  values,
  onValuesChange,
  onSave,
  onTest,
  saveDisabled = false,
  testDisabled = false,
  fieldErrors = {}
}: ApiSettingsCardProps) {
  // Debug log the props
  console.log(`[ApiSettingsCard] ${title} render:`, { fields, values });
  // State for UI interaction
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [visibleFields, setVisibleFields] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>(fieldErrors);

  // Update local errors when fieldErrors prop changes
  useEffect(() => {
    console.log(`🚨 [ApiSettingsCard] ${title}: Received fieldErrors:`, fieldErrors);
    console.log(`🚨 [ApiSettingsCard] ${title}: fieldErrors keys length:`, Object.keys(fieldErrors).length);
    
    if (fieldErrors && Object.keys(fieldErrors).length > 0) {
      console.log(`🚨 [ApiSettingsCard] ${title}: Setting errors from fieldErrors props`);
      setErrors(fieldErrors);
    }
  }, [fieldErrors]);

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    onValuesChange({
      ...values,
      [name]: value
    });
  };

  // Toggle field visibility (for secure fields)
  const toggleFieldVisibility = (fieldId: string) => {
    setVisibleFields(prev => ({
      ...prev,
      [fieldId]: !prev[fieldId]
    }));
  };

  // Rely on the errors passed in through props or set locally
  const hasValidationErrors = (): boolean => {
    // Log the current errors
    console.log(`🚨 [ApiSettingsCard] ${title}: Checking validation errors. Current errors:`, errors);
    console.log(`🚨 [ApiSettingsCard] ${title}: Errors keys length:`, Object.keys(errors).length);
    
    // Check if there are any validation errors
    const hasErrors = Object.keys(errors).length > 0 && Object.values(errors).some(error => error !== '');
    console.log(`🚨 [ApiSettingsCard] ${title}: Has validation errors:`, hasErrors);
    
    return hasErrors;
  };

  // Handle save operation
  const handleSave = async () => {
    // Temporarily bypass validation since we have empty or invalid error objects
    // Check for validation errors
    if (hasValidationErrors()) {
      console.log(`⚠️ [ApiSettingsCard] ${title}: Validation errors present:`, errors);
      toast.error(`Please fix the errors before saving`);
      return;
    }
    
    try {
      console.log(`💾 [ApiSettingsCard] ${title}: Saving settings with values:`, JSON.stringify(values, null, 2));
      setLoading(true);
      setSaveSuccess(false);
      
      // Call the save function
      await onSave();
      
      // Set success state
      setSaveSuccess(true);
      // Reset after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000);
      
      console.log(`✅ [ApiSettingsCard] ${title}: Settings saved successfully`);
      // Toast is now handled by the useApiSettings hook, no need to duplicate it here
    } catch (error) {
      console.error(`❌ [ApiSettingsCard] Error saving ${title} settings:`, error);
      let errorMessage = `Failed to save ${title} settings`;
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Handle test connection
  const handleTest = async () => {
    // Temporarily bypass validation since we have empty or invalid error objects
    // Check for validation errors
    if (hasValidationErrors()) {
      console.log(`⚠️ [ApiSettingsCard] ${title}: Validation errors present:`, errors);
      toast.error(`Please fix the errors before testing connection`);
      return;
    }
    
    try {
      console.log(`🔍 [ApiSettingsCard] ${title}: Testing connection with values:`, JSON.stringify(values, null, 2));
      setTestingConnection(true);
      setConnectionStatus('idle');
      
      // Call the test function
      await onTest();
      
      // Set success state
      setConnectionStatus('success');
      console.log(`✅ [ApiSettingsCard] ${title}: Connection test successful`);
      // Reset after 5 seconds
      setTimeout(() => setConnectionStatus('idle'), 5000);
    } catch (error) {
      console.error(`❌ [ApiSettingsCard] Error testing ${title} connection:`, error);
      let errorMessage = `Failed to test ${title} connection`;
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
      
      // Set error state
      setConnectionStatus('error');
      // Reset after 5 seconds
      setTimeout(() => setConnectionStatus('idle'), 5000);
    } finally {
      setTestingConnection(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {icon}
          {title}
        </CardTitle>
        <CardDescription>
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {fields.map(field => (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id} className="flex items-center gap-1">
              {field.label}
              {field.required && <span className="text-destructive">*</span>}
            </Label>
            <div className="relative">
              <Input
                id={field.id}
                name={field.id}
                type={field.secure && !visibleFields[field.id] ? "password" : field.type || "text"}
                placeholder={field.placeholder}
                value={values[field.id] || ''}
                onChange={handleInputChange}
                className={cn(
                  errors[field.id] && "border-destructive focus-visible:ring-destructive"
                )}
                aria-invalid={errors[field.id] ? "true" : "false"}
              />
              {field.secure && (
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility(field.id)}
                  className="absolute right-2 top-2 text-gray-500 hover:text-gray-700"
                  aria-label={visibleFields[field.id] ? `Hide ${field.label}` : `Show ${field.label}`}
                >
                  {visibleFields[field.id] ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              )}
            </div>
            {errors[field.id] ? (
              <p className="text-sm text-destructive">
                {errors[field.id]}
              </p>
            ) : field.description ? (
              <p className="text-sm text-muted-foreground">
                {field.description}
              </p>
            ) : null}
          </div>
        ))}
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button
          variant="outline"
          onClick={handleTest}
          disabled={loading || testingConnection || testDisabled}
          className="flex items-center gap-2"
        >
          {testingConnection ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Testing...
            </>
          ) : connectionStatus === 'success' ? (
            <>
              <CheckCircle className="h-4 w-4 text-green-500" />
              Connected
            </>
          ) : connectionStatus === 'error' ? (
            <>
              <AlertCircle className="h-4 w-4 text-red-500" />
              Connection Failed
            </>
          ) : (
            'Test Connection'
          )}
        </Button>
        <Button
          onClick={handleSave}
          disabled={loading || testingConnection || saveDisabled}
          className="flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : saveSuccess ? (
            <>
              <CheckCircle className="h-4 w-4" />
              Saved!
            </>
          ) : (
            'Save Settings'
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
