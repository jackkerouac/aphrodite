import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  PreviewPageData, 
  defaultPreviewPageData,
  BadgeType,
  PreviewJob,
  JellyfinLibrary,
  MediaItem,
  MediaSearchParams,
  ProcessingJob
} from './types';

export function usePreviewData() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PreviewPageData>(defaultPreviewPageData);

  // Load initial preview data
  const loadPreviewData = async () => {
    setLoading(true);
    
    try {
      console.log('Loading preview page data...');
      
      // Load badge types
      const badgeTypesResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/preview/badge-types`);
      const badgeTypesData = await badgeTypesResponse.json();

      console.log('Loaded preview data:', { badgeTypesData });

      // Update state with loaded data
      setData(prev => ({
        ...prev,
        availableBadgeTypes: badgeTypesData.success ? badgeTypesData.badgeTypes : defaultPreviewPageData.availableBadgeTypes
      }));

      console.log('Preview page data loaded successfully');
    } catch (error) {
      console.error('Error loading preview page data:', error);
      toast.error('Failed to load preview information', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  // Refresh data
  const refreshData = async () => {
    await loadPreviewData();
  };

  return {
    loading,
    data,
    loadPreviewData,
    refreshData,
    setData
  };
}

// Badge selection and preview generation hook
export function usePreviewGeneration() {
  const [selectedBadgeTypes, setSelectedBadgeTypes] = useState<string[]>(['audio', 'resolution']);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentPreview, setCurrentPreview] = useState<{
    jobId?: string;
    previewUrl?: string;
    sourcePoster?: string;
    error?: string;
  }>({});

  // Generate preview
  const generatePreview = async (): Promise<boolean> => {
    if (selectedBadgeTypes.length === 0) {
      toast.error('Please select at least one badge type');
      return false;
    }

    setIsGenerating(true);
    setCurrentPreview({ error: undefined, previewUrl: undefined });

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/preview/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          badgeTypes: selectedBadgeTypes
        }),
      });

      const data = await response.json();

      if (data.success) {
        // Preview generated immediately, no job polling needed
        setCurrentPreview({
          previewUrl: data.posterUrl,
          sourcePoster: 'Random Selection',
          error: undefined
        });
        
        const badgeCount = data.appliedBadges?.length || selectedBadgeTypes.length;
        const processingTime = data.processingTime || 0;
        
        toast.success(`Preview generated with ${badgeCount} badges (${processingTime.toFixed(2)}s)`);
        return true;
      } else {
        setCurrentPreview({ error: data.message || 'Failed to generate preview' });
        toast.error(data.message || 'Failed to generate preview');
        return false;
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate preview';
      setCurrentPreview({ error: errorMessage });
      toast.error(errorMessage);
      return false;
    } finally {
      setIsGenerating(false);
    }
  };

  // Remove the job polling function since we're doing immediate processing
  // const pollJobStatus = async (jobId: string) => { ... }

  // Toggle badge type selection
  const toggleBadgeType = (badgeId: string) => {
    setSelectedBadgeTypes(prev => {
      if (prev.includes(badgeId)) {
        return prev.filter(id => id !== badgeId);
      } else {
        return [...prev, badgeId];
      }
    });
  };

  // Clear current preview
  const clearPreview = () => {
    setCurrentPreview({});
  };

  return {
    selectedBadgeTypes,
    isGenerating,
    currentPreview,
    generatePreview,
    toggleBadgeType,
    clearPreview,
    setSelectedBadgeTypes
  };
}

// Library browsing hook (for future Jellyfin integration)
export function useLibraryBrowser() {
  const [libraries, setLibraries] = useState<JellyfinLibrary[]>([]);
  const [selectedLibrary, setSelectedLibrary] = useState<string>('');
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);
  const [selectedMedia, setSelectedMedia] = useState<string>('');
  const [loading, setLoading] = useState({
    libraries: false,
    media: false
  });

  // Load Jellyfin libraries
  const loadLibraries = async () => {
    setLoading(prev => ({ ...prev, libraries: true }));
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/preview/libraries`);
      const data = await response.json();
      
      if (data.success) {
        setLibraries(data.libraries || []);
      } else {
        toast.error('Failed to load libraries');
      }
    } catch (error) {
      console.error('Error loading libraries:', error);
      toast.error('Error loading libraries');
    } finally {
      setLoading(prev => ({ ...prev, libraries: false }));
    }
  };

  // Load media items from selected library
  const loadMedia = async (params: MediaSearchParams = {}) => {
    if (!selectedLibrary && !params.library_id) return;

    setLoading(prev => ({ ...prev, media: true }));
    
    try {
      const searchParams = new URLSearchParams();
      const libraryId = params.library_id || selectedLibrary;
      
      if (libraryId) searchParams.set('library_id', libraryId);
      if (params.search) searchParams.set('search', params.search);
      if (params.page) searchParams.set('page', params.page.toString());
      if (params.limit) searchParams.set('limit', params.limit.toString());

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/preview/media?${searchParams}`
      );
      const data = await response.json();
      
      if (data.success) {
        setMediaItems(data.media || []);
      } else {
        toast.error('Failed to load media items');
      }
    } catch (error) {
      console.error('Error loading media:', error);
      toast.error('Error loading media items');
    } finally {
      setLoading(prev => ({ ...prev, media: false }));
    }
  };

  // Select library
  const selectLibrary = (libraryId: string) => {
    setSelectedLibrary(libraryId);
    setSelectedMedia('');
    setMediaItems([]);
    
    if (libraryId) {
      loadMedia({ library_id: libraryId });
    }
  };

  // Select media item
  const selectMedia = (mediaId: string) => {
    setSelectedMedia(mediaId);
  };

  return {
    libraries,
    selectedLibrary,
    mediaItems,
    selectedMedia,
    loading,
    loadLibraries,
    loadMedia,
    selectLibrary,
    selectMedia
  };
}

// Processing queue management hook (for future batch processing)
export function useProcessingQueue() {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [loading, setLoading] = useState(false);

  // Load current jobs
  const loadJobs = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs?status=pending,running`);
      const data = await response.json();
      
      if (data.success) {
        setJobs(data.jobs || []);
      }
    } catch (error) {
      console.error('Error loading jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  // Add job to queue
  const addJob = async (mediaIds: string[], badgeTypes: string[]): Promise<boolean> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          media_ids: mediaIds,
          job_type: 'badge_processing',
          parameters: {
            badge_types: badgeTypes
          }
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        toast.success('Job added to queue');
        await loadJobs(); // Refresh jobs list
        return true;
      } else {
        toast.error(data.message || 'Failed to add job');
        return false;
      }
    } catch (error) {
      console.error('Error adding job:', error);
      toast.error('Error adding job to queue');
      return false;
    }
  };

  // Cancel job
  const cancelJob = async (jobId: string): Promise<boolean> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.success) {
        toast.success('Job cancelled');
        await loadJobs(); // Refresh jobs list
        return true;
      } else {
        toast.error(data.message || 'Failed to cancel job');
        return false;
      }
    } catch (error) {
      console.error('Error cancelling job:', error);
      toast.error('Error cancelling job');
      return false;
    }
  };

  return {
    jobs,
    loading,
    loadJobs,
    addJob,
    cancelJob
  };
}
