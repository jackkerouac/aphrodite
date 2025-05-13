import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { CreateJobParams, Job } from '@/lib/api/jobs';
import { useUser } from '@/contexts/UserContext';
import { toast } from 'sonner';

export function useCreateJob() {
  const { user } = useUser();

  return useMutation({
    mutationFn: async (params: CreateJobParams) => {
      if (!user) {
        throw new Error('No user context available');
      }
      
      // Validate job payload
      if (!params.items || params.items.length === 0) {
        throw new Error('No items selected for processing');
      }
      
      if (!params.badgeSettings || params.badgeSettings.length === 0) {
        throw new Error('No badge settings provided for job creation');
      }
      
      // Ensure user_id is set correctly
      const jobParams = {
        ...params,
        user_id: parseInt(user.id)
      };
      
      // Validate each badge setting has required properties
      jobParams.badgeSettings = jobParams.badgeSettings.map(badge => {
        // Ensure badge_type is set
        if (!badge.badge_type) {
          console.error('Badge missing required badge_type property:', badge);
          return null;
        }
        
        // Return cleaned badge
        return {
          ...badge,
          badge_type: String(badge.badge_type)
        };
      }).filter(Boolean); // Remove any invalid badges
      
      // Final check to ensure we still have badge settings
      if (jobParams.badgeSettings.length === 0) {
        throw new Error('All badge settings were invalid. Job creation aborted.');
      }
      
      return apiClient.jobs.createJob(jobParams);
    },
    onSuccess: (job: Job) => {
      toast.success(`Job "${job.name}" created successfully`);
    },
    onError: (error: Error) => {
      console.error('Failed to create job:', error);
      
      // Provide more specific error message to the user
      const errorMessage = error.message || 'Failed to create job';
      toast.error(errorMessage);
    }
  });
}
