import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar,
  Clock,
  User,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2 
} from 'lucide-react';
import apiService from '@/services/api';
import { toast } from 'sonner';
import type { ActivityDetailResponse, ActivityDetail } from '../types';

interface ActivityDetailsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  activityType: string;
  activityTypeName: string;
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    case 'failed':
      return <XCircle className="h-4 w-4 text-red-600" />;
    case 'running':
    case 'processing':
      return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
    default:
      return <Clock className="h-4 w-4 text-gray-600" />;
  }
};

const getStatusBadgeVariant = (status: string) => {
  switch (status) {
    case 'completed':
      return 'default';
    case 'failed':
      return 'destructive';
    case 'running':
    case 'processing':
      return 'secondary';
    default:
      return 'outline';
  }
};

export function ActivityDetailsDialog({
  open,
  onOpenChange,
  activityType,
  activityTypeName
}: ActivityDetailsDialogProps) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ActivityDetailResponse | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [daysFilter, setDaysFilter] = useState<number>(7);

  const fetchData = async () => {
    if (!open || !activityType) return;
    
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        limit: 20,
        days: daysFilter,
        ...(statusFilter !== 'all' && { status: statusFilter })
      };
      
      const response = await apiService.getActivityTypeDetails(activityType, params);
      if (response.success !== false) {
        setData(response);
      } else {
        toast.error('Failed to load activity details');
      }
    } catch (error) {
      console.error('Failed to fetch activity details:', error);
      toast.error('Failed to load activity details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      setCurrentPage(1);
      fetchData();
    }
  }, [open, activityType, statusFilter, daysFilter]);

  useEffect(() => {
    fetchData();
  }, [currentPage]);

  const handlePreviousPage = () => {
    if (data?.pagination.has_prev) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (data?.pagination.has_next) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>{activityTypeName} Activities</DialogTitle>
          <DialogDescription>
            Detailed list of {activityTypeName.toLowerCase()} operations and their results
          </DialogDescription>
        </DialogHeader>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium">Status:</label>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
                <SelectItem value="running">Running</SelectItem>
                <SelectItem value="queued">Queued</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium">Time Period:</label>
            <Select value={daysFilter.toString()} onValueChange={(value) => setDaysFilter(parseInt(value))}>
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Last 24h</SelectItem>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {data && (
            <div className="text-sm text-muted-foreground">
              {data.total_count} total activities found
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              <span>Loading activities...</span>
            </div>
          ) : data?.activities.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No activities found for the selected filters.
            </div>
          ) : (
            <div className="space-y-3">
              {data?.activities.map((activity: ActivityDetail) => (
                <Card key={activity.id} className="p-4">
                  <CardContent className="p-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getStatusIcon(activity.status)}
                          <h4 className="font-medium">{activity.name}</h4>
                          <Badge variant={getStatusBadgeVariant(activity.status)}>
                            {activity.status}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                          <div className="flex items-center space-x-2">
                            <User className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">User:</span>
                            <span>{activity.user_id}</span>
                          </div>

                          <div className="flex items-center space-x-2">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">Created:</span>
                            <span>{formatDate(activity.created_at)}</span>
                          </div>

                          {activity.started_at && (
                            <div className="flex items-center space-x-2">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">Started:</span>
                              <span>{formatDate(activity.started_at)}</span>
                            </div>
                          )}
                        </div>

                        <div className="flex items-center space-x-4 mt-3 text-sm">
                          <span>
                            <span className="text-muted-foreground">Total:</span>{' '}
                            <span className="font-medium">{activity.total_posters}</span>
                          </span>
                          <span>
                            <span className="text-muted-foreground">Completed:</span>{' '}
                            <span className="font-medium text-green-600">{activity.completed_posters}</span>
                          </span>
                          <span>
                            <span className="text-muted-foreground">Failed:</span>{' '}
                            <span className="font-medium text-red-600">{activity.failed_posters}</span>
                          </span>
                          {activity.total_posters > 0 && (
                            <span>
                              <span className="text-muted-foreground">Progress:</span>{' '}
                              <span className="font-medium">
                                {Math.round((activity.completed_posters / activity.total_posters) * 100)}%
                              </span>
                            </span>
                          )}
                        </div>

                        {activity.badge_types && activity.badge_types.length > 0 && (
                          <div className="flex items-center space-x-2 mt-2">
                            <span className="text-sm text-muted-foreground">Badge Types:</span>
                            <div className="flex flex-wrap gap-1">
                              {activity.badge_types.map((badgeType) => (
                                <Badge key={badgeType} variant="outline" className="text-xs">
                                  {badgeType}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        {activity.error_summary && (
                          <div className="flex items-start space-x-2 mt-2 p-2 bg-red-50 rounded">
                            <AlertCircle className="h-4 w-4 text-red-600 mt-0.5" />
                            <div>
                              <span className="text-sm font-medium text-red-700">Error:</span>
                              <p className="text-sm text-red-600">{activity.error_summary}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Pagination */}
        {data && data.pagination.total_pages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-muted-foreground">
              Page {data.pagination.page} of {data.pagination.total_pages}
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePreviousPage}
                disabled={!data.pagination.has_prev}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleNextPage}
                disabled={!data.pagination.has_next}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
