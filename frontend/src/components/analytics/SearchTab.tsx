import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Loader2, Search, CheckCircle, XCircle, Clock } from 'lucide-react';

interface ActivitySearchParams {
  activity_types?: string[];
  statuses?: string[];
  success?: boolean;
  user_id?: string;
  start_date?: string;
  end_date?: string;
  error_text?: string;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  offset?: number;
  include_details?: boolean;
}

interface SearchResult {
  activities: any[];
  pagination: {
    total_count: number;
    returned_count: number;
    limit: number;
    offset: number;
    has_next: boolean;
    has_prev: boolean;
    total_pages: number;
    current_page: number;
  };
}

interface SearchTabProps {
  searchParams: ActivitySearchParams;
  setSearchParams: React.Dispatch<React.SetStateAction<ActivitySearchParams>>;
  searchResults: SearchResult | null;
  searchLoading: boolean;
  suggestions: any;
  onSearch: () => void;
}

const formatDuration = (ms: number | null) => {
  if (!ms) return 'N/A';
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
};

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
};

export function SearchTab({ 
  searchParams, 
  setSearchParams, 
  searchResults, 
  searchLoading, 
  suggestions, 
  onSearch 
}: SearchTabProps) {
  return (
    <div className="space-y-6">
      {/* Search Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Advanced Activity Search</CardTitle>
          <CardDescription>
            Search and filter activities with advanced criteria
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            {suggestions && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Activity Types</label>
                  <Select
                    value={searchParams.activity_types?.[0] || ''}
                    onValueChange={(value) => 
                      setSearchParams(prev => ({
                        ...prev, 
                        activity_types: value ? [value] : undefined
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All types</SelectItem>
                      {suggestions.activity_types?.map((type: string) => (
                        <SelectItem key={type} value={type}>
                          {type.replace('_', ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Status</label>
                  <Select
                    value={searchParams.statuses?.[0] || ''}
                    onValueChange={(value) => 
                      setSearchParams(prev => ({
                        ...prev, 
                        statuses: value ? [value] : undefined
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All statuses" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All statuses</SelectItem>
                      {suggestions.statuses?.map((status: string) => (
                        <SelectItem key={status} value={status}>
                          {status}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Success</label>
                  <Select
                    value={searchParams.success !== undefined ? searchParams.success.toString() : ''}
                    onValueChange={(value) => 
                      setSearchParams(prev => ({
                        ...prev, 
                        success: value === '' ? undefined : value === 'true'
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All results" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All results</SelectItem>
                      <SelectItem value="true">Successful only</SelectItem>
                      <SelectItem value="false">Failed only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">User ID</label>
                  <Input
                    placeholder="Enter user ID"
                    value={searchParams.user_id || ''}
                    onChange={(e) => 
                      setSearchParams(prev => ({
                        ...prev, 
                        user_id: e.target.value || undefined
                      }))
                    }
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Error Text</label>
                  <Input
                    placeholder="Search in error messages"
                    value={searchParams.error_text || ''}
                    onChange={(e) => 
                      setSearchParams(prev => ({
                        ...prev, 
                        error_text: e.target.value || undefined
                      }))
                    }
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Sort By</label>
                  <Select
                    value={searchParams.sort_by || 'created_at'}
                    onValueChange={(value) => 
                      setSearchParams(prev => ({ ...prev, sort_by: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {suggestions.sort_options?.map((option: any) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <Button 
              onClick={onSearch}
              disabled={searchLoading}
            >
              {searchLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Search className="h-4 w-4 mr-2" />
              )}
              Search
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => {
                setSearchParams({
                  limit: 50,
                  offset: 0,
                  sort_by: 'created_at',
                  sort_order: 'desc',
                  include_details: false
                });
              }}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Search Results */}
      {searchResults && (
        <Card>
          <CardHeader>
            <CardTitle>Search Results</CardTitle>
            <CardDescription>
              Found {searchResults.pagination.total_count.toLocaleString()} activities
              (showing {searchResults.pagination.returned_count})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {searchResults.activities.map((activity) => (
                <div 
                  key={activity.id} 
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                >
                  <div className="flex flex-col">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">
                        {activity.activity_type?.replace('_', ' ')}
                      </Badge>
                      <span className="font-mono text-sm text-muted-foreground">
                        {activity.media_id}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {formatDate(activity.created_at)} • 
                      Duration: {formatDuration(activity.processing_duration_ms)}
                    </div>
                    {activity.error_message && (
                      <div className="text-sm text-red-600 mt-1 truncate max-w-md">
                        {activity.error_message}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {activity.success === true && (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    )}
                    {activity.success === false && (
                      <XCircle className="h-4 w-4 text-red-600" />
                    )}
                    {activity.success === null && (
                      <Clock className="h-4 w-4 text-yellow-600" />
                    )}
                    <Badge
                      variant={
                        activity.success === true ? 'default' :
                        activity.success === false ? 'destructive' : 'secondary'
                      }
                    >
                      {activity.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Pagination */}
            {searchResults.pagination.total_pages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-muted-foreground">
                  Page {searchResults.pagination.current_page} of {searchResults.pagination.total_pages}
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!searchResults.pagination.has_prev}
                    onClick={() => {
                      setSearchParams(prev => ({
                        ...prev,
                        offset: Math.max(0, (prev.offset || 0) - (prev.limit || 50))
                      }));
                      onSearch();
                    }}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!searchResults.pagination.has_next}
                    onClick={() => {
                      setSearchParams(prev => ({
                        ...prev,
                        offset: (prev.offset || 0) + (prev.limit || 50)
                      }));
                      onSearch();
                    }}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
