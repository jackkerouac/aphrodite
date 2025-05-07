import React, { useState, useCallback } from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

// Import components
import SettingsForm from './components/SettingsForm';
import PreviewPanel from './components/PreviewPanel';

// Import hook and constants
import { useAudioBadgeSettings } from './hooks/useAudioBadgeSettings';
import { audioCodecOptions, audioCodecImages } from './constants';

const AudioBadgeSettings: React.FC = () => {
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
    handleAudioCodecChange,
    setError,
    showSuccessNotification,
    selectedAudioCodec
  } = useAudioBadgeSettings();

  const [previewImage, setPreviewImage] = useState('/src/assets/posters/dummy_poster_light.png');

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

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Audio Badge Settings</h1>
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
        <h1 className="text-3xl font-bold tracking-tight">Audio Badge Settings</h1>
        <Alert className="bg-destructive/10 border-destructive">
          <AlertCircle className="h-4 w-4 text-destructive mr-2" />
          <AlertDescription>
            {error.message || 'Error loading settings'}
          </AlertDescription>
        </Alert>
        <div className="flex justify-center">
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Audio Badge Settings</h1>
      <p className="text-muted-foreground">
        Configure the appearance of your Audio Badges.
      </p>

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
        <div className="w-full md:w-1/2">
          <SettingsForm
            settings={settings}
            handleChange={handleChange}
            handleColorChange={handleColorChange}
            handleToggleChange={handleToggleChange}
            handlePositionChange={handlePositionChange}
            handleAudioCodecChange={handleAudioCodecChange}
            selectedAudioCodec={selectedAudioCodec}
            onSubmit={onSubmit}
            saving={saving}
            isSaveDisabled={isSaveDisabled}
            audioCodecOptions={audioCodecOptions}
          />
        </div>
        <div className="w-full md:w-1/2">
          <PreviewPanel
            previewImage={previewImage}
            togglePreviewImage={togglePreviewImage}
            selectedAudioCodec={selectedAudioCodec}
            settings={settings}
            audioCodecImages={audioCodecImages}
          />
        </div>
      </div>
    </div>
  );
};

export default AudioBadgeSettings;