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
      
      // Ensure user_id is set correctly
      const jobParams = {
        ...params,
        user_id: parseInt(user.id)
      };
      
      return apiClient.jobs.createJob(jobParams);
    },
    onSuccess: (job: Job) => {
      toast.success(`Job "${job.name}" created successfully`);
    },
    onError: (error) => {
      console.error('Failed to create job:', error);
      toast.error('Failed to create job');
    }
  });
}
