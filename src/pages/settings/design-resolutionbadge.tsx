import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import GeneralSettingsCard from './GeneralSettingsCard';
import PreviewCard from './PreviewCard';
import ShadowSettings from './ShadowSettings';
import ColorPicker from './ColorPicker';

// Configuration
const USE_SIMULATION = false; // Set to false when backend API is implemented
const SIMULATION_DELAY = 800; // Milliseconds to simulate network delay

// ===============================
// Main Component
// ===============================

// REMOVED plus from the list.
const resolutionOptions = [
    '4k', '4kdv', '4kdvhdr', '4kdvhdrplus', '4khdr', '4kplus', '480', '480p', '480pdv',
    '480pdvhdr', '480pdvhdrplus', '480phdr', '480pplus', '576p', '576pdv', '576pdvhdr',
    '576pdvhdrplus', '576phdr', '576pplus', '720', '720p', '720pdv', '720pdvhdr',
    '720pdvhdrplus', '720phdr', '720pplus', '1080', '1080p', '1080pdv', '1080pdvhdr',
    '1080pdvhdrplus', '1080phdr', '1080pplus', '2160', 'dv', 'dvhdr', 'dvhdrplus', 'hdr'
];

// Define a mapping between resolution types and their corresponding image paths
const resolutionImages: Record<string, string> = {
    '4k': '/src/assets/resolution/4k.png',
    '4kdv': '/src/assets/resolution/4kdv.png',
    '4kdvhdr': '/src/assets/resolution/4kdvhdr.png',
    '4kdvhdrplus': '/src/assets/resolution/4kdvhdrplus.png',
    '4khdr': '/src/assets/resolution/4khdr.png',
    '4kplus': '/src/assets/resolution/4kplus.png',
    '480': '/src/assets/resolution/480.png',
    '480p': '/src/assets/resolution/480p.png',
    '480pdv': '/src/assets/resolution/480pdv.png',
    '480pdvhdr': '/src/assets/resolution/480pdvhdr.png',
    '480pdvhdrplus': '/src/assets/resolution/480pdvhdrplus.png',
    '480phdr': '/src/assets/resolution/480phdr.png',
    '480pplus': '/src/assets/resolution/480pplus.png',
    '576p': '/src/assets/resolution/576p.png',
    '576pdv': '/src/assets/resolution/576pdv.png',
    '576pdvhdr': '/src/assets/resolution/576pdvhdr.png',
    '576pdvhdrplus': '/src/assets/resolution/576pdvhdrplus.png',
    '576phdr': '/src/assets/resolution/576phdr.png',
    '576pplus': '/src/assets/resolution/576pplus.png',
    '720': '/src/assets/resolution/720.png',
    '720p': '/src/assets/resolution/720p.png',
    '720pdv': '/src/assets/resolution/720pdv.png',
    '720pdvhdr': '/src/assets/resolution/720pdvhdr.png',
    '720pdvhdrplus': '/src/assets/resolution/720pdvhdrplus.png',
    '720phdr': '/src/assets/resolution/720phdr.png',
    '720pplus': '/src/assets/resolution/720pplus.png',
    '1080': '/src/assets/resolution/1080.png',
    '1080p': '/src/assets/resolution/1080p.png',
    '1080pdv': '/src/assets/resolution/1080pdv.png',
    '1080pdvhdr': '/src/assets/resolution/1080pdvhdr.png',
    '1080pdvhdrplus': '/src/assets/resolution/1080pdvhdrplus.png',
    '1080phdr': '/src/assets/resolution/1080phdr.png',
    '1080pplus': '/src/assets/resolution/1080pplus.png',
    '2160': '/src/assets/resolution/2160.png',
    'dv': '/src/assets/resolution/dv.png',
    'dvhdr': '/src/assets/resolution/dvhdr.png',
    'dvhdrplus': '/src/assets/resolution/dvhdrplus.png',
    'hdr': '/src/assets/resolution/hdr.png',
};

// For simulation mode - store settings in memory
let savedSimulationSettings = null;

const useResolutionBadgeSettings = () => {
    const [settings, setSettings] = useState({
        resolution_type: '1080',
        margin: 10,
        position: 'top-left',
        size: 100, // Size as percentage (100% = original size)
        background_color: '#000000',
        background_transparency: 0.8,
        border_radius: 4,
        border_width: 1,
        border_color: '#ffffff',
        border_transparency: 0.8,
        shadow_toggle: false,
        shadow_color: '#000000',
        shadow_blur_radius: 5,
        shadow_offset_x: 2,
        shadow_offset_y: 2,
        z_index: 1
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [saving, setSaving] = useState(false);
    const [isSaveDisabled, setIsSaveDisabled] = useState(false);
    const [showSuccessNotification, setShowSuccessNotification] = useState(false);
    const [selectedResolution, setSelectedResolution] = useState(settings.resolution_type || '1080');

    // Load settings from the API when component mounts
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                setLoading(true);
                setError(null);
                
                // Check if using simulation mode
                if (USE_SIMULATION) {
                    // Simulate network delay
                    await new Promise(resolve => setTimeout(resolve, SIMULATION_DELAY));
                    
                    // If we have saved settings, use them
                    if (savedSimulationSettings) {
                        console.log('Using simulated saved settings:', savedSimulationSettings);
                        
                        setSettings(prevSettings => ({
                            ...prevSettings,
                            ...savedSimulationSettings,
                        }));
                        
                        if (savedSimulationSettings.resolution_type) {
                            setSelectedResolution(savedSimulationSettings.resolution_type);
                        }
                    } else {
                        console.log('No saved settings found in simulation mode, using defaults');
                    }
                    
                    setLoading(false);
                    return;
                }
                
                // Real API implementation
                const userId = 1; // In a real app, you'd get this from authentication
                const endpoint = `/api/resolution-badge-settings/${userId}`;
                
                const response = await fetch(endpoint);
                
                // Get response text first (don't try to parse JSON yet)
                const responseText = await response.text();
                console.log('API Response text:', responseText);
                
                if (!response.ok) {
                    // If settings don't exist yet, we'll just use defaults
                    if (response.status === 404) {
                        console.log('No settings found, using defaults');
                        return;
                    }
                    
                    // Try to parse as JSON if possible
                    let errorMessage = 'Failed to load settings';
                    try {
                        const errorData = JSON.parse(responseText);
                        errorMessage = errorData.message || errorMessage;
                    } catch (parseError) {
                        // If JSON parsing fails, use response text or status
                        errorMessage = responseText || `Server returned ${response.status}: ${response.statusText}`;
                    }
                    throw new Error(errorMessage);
                }
                
                // Try to parse the successful response
                let data;
                try {
                    data = JSON.parse(responseText);
                    console.log('Settings loaded:', data);

                    // Update settings with loaded data
                    // Note: We're keeping default values for any missing fields
                    setSettings(prevSettings => ({
                        ...prevSettings,
                        ...data,
                    }));
                    
                    // Update selected resolution if it exists in the loaded data
                    if (data.resolution_type) {
                        setSelectedResolution(data.resolution_type);
                    }
                } catch (parseError) {
                    console.error('Failed to parse response as JSON:', parseError);
                    const errorMessage = responseText || 'Unknown Response';
                    throw new Error(`Received invalid data from server: ${errorMessage}`);
                }
            } catch (err: any) {
                console.error('Error loading settings:', err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };
        
        fetchSettings();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setSettings(prevSettings => ({
            ...prevSettings,
            [name]: name.includes('transparency') || name.includes('size') ? parseFloat(value) : value,
        }));
    };
    
    const handleColorChange = (key: string, value: string) => {
        setSettings(prevSettings => ({
            ...prevSettings,
            [key]: value,
        }));
    };
    
    const handleToggleChange = (key: string, value: boolean) => {
        setSettings(prevSettings => ({
            ...prevSettings,
            [key]: value,
        }));
    };


    const handleSave = async () => {
        try {
            setSaving(true);
            setIsSaveDisabled(true);
            setError(null);
            
            // Check if using simulation mode
            if (USE_SIMULATION) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, SIMULATION_DELAY));
                
                // Store settings in the simulation variable
                savedSimulationSettings = { ...settings };
                console.log('Saved settings in simulation mode:', savedSimulationSettings);
                
                // Set success state
                setShowSuccessNotification(true);
                
                // Hide success notification after a delay
                setTimeout(() => {
                    setShowSuccessNotification(false);
                }, 3000);
                
                setSaving(false);
                setIsSaveDisabled(false);
                return;
            }
            
            // Real API implementation
            const userId = 1; // In a real app, you'd get this from authentication
            const endpoint = `/api/resolution-badge-settings/${userId}`;
            
            // Note: Database needs to be updated to include 'resolution_type' and 'position' fields
            // Current implementation will only save fields that exist in the database
            
            // Prepare the settings object to be sent to the API
            const settingsToSave = {
                size: settings.size,
                margin: settings.margin,
                background_color: settings.background_color,
                background_transparency: settings.background_transparency,
                border_radius: settings.border_radius,
                border_width: settings.border_width,
                border_color: settings.border_color,
                border_transparency: settings.border_transparency,
                shadow_toggle: settings.shadow_toggle,
                shadow_color: settings.shadow_color,
                shadow_blur_radius: settings.shadow_blur_radius,
                shadow_offset_x: settings.shadow_offset_x,
                shadow_offset_y: settings.shadow_offset_y,
                z_index: settings.z_index,
                // These fields might not exist in the database yet
                resolution_type: settings.resolution_type,
                position: settings.position
            };
            
            // Make the API call
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsToSave),
            });
            
            // Get response text first (don't try to parse JSON yet)
            const responseText = await response.text();
            console.log('API Response text:', responseText);
            
            // Check if response is successful
            if (!response.ok) {
                // Try to parse as JSON if possible
                let errorMessage = 'Failed to save settings';
                try {
                    const errorData = JSON.parse(responseText);
                    errorMessage = errorData.message || errorMessage;
                } catch (parseError) {
                    // If JSON parsing fails, use response text or status
                    errorMessage = responseText || `Server returned ${response.status}: ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }
            
            // Try to parse the successful response
            let data;
            try {
                data = JSON.parse(responseText);
                console.log('Settings saved successfully:', data);
            } catch (parseError) {
                console.warn('Could not parse response as JSON, but request succeeded:', responseText);
                // Continue anyway since the save was successful
            }
            
            // Set success state (we'll add a notification for this)
            setShowSuccessNotification(true);
            
            // Hide success notification after a delay
            setTimeout(() => {
                setShowSuccessNotification(false);
            }, 3000);
        } catch (err: any) {
            console.error('Error saving settings:', err);
            setError(err);
        } finally {
            setSaving(false);
            setIsSaveDisabled(false);
        }
    };

    const handlePositionChange = (value: string) => {
        setSettings(prevSettings => ({
            ...prevSettings,
            position: value,
        }));
    };
    const handleResolutionChange = (value: string) => {
        setSettings(prevSettings => ({
            ...prevSettings,
            resolution_type: value,
        }));
        setSelectedResolution(value);
    };

    return {
        settings,
        loading,
        error,
        saving,
        handleChange,
        handleColorChange,
        handleToggleChange,
        handleSave,
        isSaveDisabled,
        handlePositionChange,
        handleResolutionChange,
        setError,
        showSuccessNotification,
        setShowSuccessNotification,
        selectedResolution
    };
};

const DesignResolutionBadge = () => {
    const {
        settings,
        loading,
        error,
        saving,
        handleChange,
        handleColorChange,
        handleToggleChange,
        handleSave,
        isSaveDisabled,
        handlePositionChange,
        handleResolutionChange,
        setError,
        showSuccessNotification,
        selectedResolution
    } = useResolutionBadgeSettings();

    const [previewImage, setPreviewImage] = useState('/src/assets/posters/dummy_poster_light.png');
    const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });

    const onSubmit = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await handleSave();
        } catch (err: any) {
            console.error('Error saving settings:', err);
        }
    }, [handleSave]);

    const togglePreviewImage = () => {
        setPreviewImage(prevImage =>
            prevImage === '/src/assets/posters/dummy_poster_light.png'
                ? '/src/assets/posters/dummy_poster_dark.png'
                : '/src/assets/posters/dummy_poster_light.png'
        );
    };

    useEffect(() => {
        const imagePath = resolutionImages[selectedResolution] || resolutionImages['1080'];
        const img = new Image();
        img.src = imagePath;
        img.crossOrigin = 'anonymous';
        
        const handleLoad = () => {
            // Store the natural dimensions of the image
            const width = img.naturalWidth;
            const height = img.naturalHeight;
            setImageDimensions({ width, height });
            console.log(`Image loaded: ${selectedResolution}, Size: ${width}x${height}`);
        };

        const handleError = (e: any) => {
            console.error(`Error loading image ${imagePath}:`, e);
            setImageDimensions({ width: 0, height: 0 });
        };

        img.onload = handleLoad;
        img.onerror = handleError;

        // Cleanup function
        return () => {
            img.onload = null;
            img.onerror = null;
        };
    }, [selectedResolution]);


    if (loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-3xl font-bold tracking-tight">Resolution Badge Settings</h1>
                <div className="flex items-center justify-center p-12">
                    <Loader2 className="h-8 w-8 animate-spin mr-2" />
                    <span>Loading settings...</span>
                </div>
            </div>
        );
    }

    if (error && loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-3xl font-bold tracking-tight">Resolution Badge Settings</h1>
                <Card className="bg-destructive/10 border-destructive">
                    <CardHeader>
                        <CardTitle>Error Loading Settings</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="mb-4">{error.message}</p>
                        <Button onClick={() => window.location.reload()}>Retry</Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold tracking-tight">Resolution Badge Settings</h1>
            <p className="text-muted-foreground">
                Configure the appearance of your Resolution Badges.
            </p>

            {USE_SIMULATION && (
                <Alert className="bg-yellow-50 border-yellow-200 text-yellow-800">
                    <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
                    <AlertDescription>
                        Running in simulation mode. Settings are not being saved to the database.
                    </AlertDescription>
                </Alert>
            )}

            {/* Success notification */}
            {showSuccessNotification && (
                <Alert className="bg-green-50 border-green-200 text-green-800">
                    <CheckCircle2 className="h-4 w-4 text-green-600 mr-2" />
                    <AlertDescription>
                        Settings saved successfully!
                    </AlertDescription>
                </Alert>
            )}

            {/* Error notification */}
            {error && !loading && (
                <Alert className="bg-red-50 border-red-200 text-red-800">
                    <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
                    <AlertDescription>
                        {error.message || 'An error occurred while saving settings.'}
                    </AlertDescription>
                </Alert>
            )}

            <div className="flex flex-col md:flex-row gap-6">
                <div className="w-1/2">
                    <GeneralSettingsCard
                        settings={settings}
                        handleChange={handleChange}
                        handleColorChange={handleColorChange}
                        handleToggleChange={handleToggleChange}
                        handlePositionChange={handlePositionChange}
                        handleResolutionChange={handleResolutionChange}
                        selectedResolution={selectedResolution}
                        onSubmit={onSubmit}
                        saving={saving}
                        isSaveDisabled={isSaveDisabled}
                        resolutionOptions={resolutionOptions}
                    />
                </div>
                {/* Preview Card */}
                <div className="w-1/2">
                    <PreviewCard
                        previewImage={previewImage}
                        togglePreviewImage={togglePreviewImage}
                        selectedResolution={selectedResolution}
                        settings={settings}
                        resolutionImages={resolutionImages}
                        imageDimensions={imageDimensions}
                    />
                </div>
            </div>
        </div>
    );
};

export default DesignResolutionBadge;