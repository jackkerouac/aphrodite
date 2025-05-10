import React, { useState, useEffect } from "react";
import { Card, CardContent, Progress, Button, Alert, AlertDescription } from "@/components/ui";
import { Play, Pause, X, CheckCircle2, AlertCircle, Clock, RefreshCw } from "lucide-react";

interface JobItem {
  id: string;
  jellyfinItemId: string;
  title: string;
  status: "pending" | "processing" | "completed" | "failed";
  errorMessage?: string;
}

interface JobStatusProps {
  jobId?: string;
  totalItems: number;
  processedItems: number;
  failedItems: number;
  status: "pending" | "running" | "paused" | "completed" | "failed";
  items?: JobItem[];
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
  onRetry?: (itemId: string) => void;
}

export const JobStatus: React.FC<JobStatusProps> = ({
  jobId,
  totalItems,
  processedItems,
  failedItems,
  status,
  items = [],
  onPause,
  onResume,
  onCancel,
  onRetry
}) => {
  const [expandedErrors, setExpandedErrors] = useState<string[]>([]);
  
  // Calculate progress percentage
  const progressPercentage = totalItems > 0 ? (processedItems / totalItems) * 100 : 0;
  const successItems = processedItems - failedItems;
  
  // Get status icon and color
  const getStatusIcon = () => {
    switch (status) {
      case "running":
        return <RefreshCw className="h-5 w-5 animate-spin text-primary" />;
      case "paused":
        return <Pause className="h-5 w-5 text-yellow-500" />;
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "failed":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />;
    }
  };
  
  const getStatusText = () => {
    switch (status) {
      case "running":
        return "Processing...";
      case "paused":
        return "Paused";
      case "completed":
        return failedItems > 0 ? "Completed with errors" : "Completed successfully";
      case "failed":
        return "Failed";
      default:
        return "Pending";
    }
  };
  
  const toggleErrorExpansion = (itemId: string) => {
    setExpandedErrors(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };
  
  // Simulated WebSocket connection preparation
  useEffect(() => {
    // This is where WebSocket connection would be established
    // For now, this is just a placeholder
    console.log(`Ready to connect to WebSocket for job ${jobId}`);
    
    return () => {
      // Cleanup WebSocket connection
      console.log(`WebSocket cleanup for job ${jobId}`);
    };
  }, [jobId]);
  
  return (
    <div className="space-y-4">
      {/* Overall Progress Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              {getStatusIcon()}
              <div>
                <h3 className="text-lg font-semibold">{getStatusText()}</h3>
                <p className="text-sm text-muted-foreground">
                  {processedItems} of {totalItems} items processed
                </p>
              </div>
            </div>
            
            {/* Control buttons */}
            <div className="flex gap-2">
              {status === "running" && onPause && (
                <Button variant="secondary" size="sm" onClick={onPause}>
                  <Pause className="h-4 w-4 mr-2" />
                  Pause
                </Button>
              )}
              {status === "paused" && onResume && (
                <Button variant="secondary" size="sm" onClick={onResume}>
                  <Play className="h-4 w-4 mr-2" />
                  Resume
                </Button>
              )}
              {(status === "running" || status === "paused") && onCancel && (
                <Button variant="destructive" size="sm" onClick={onCancel}>
                  <X className="h-4 w-4 mr-2" />
                  Cancel
                </Button>
              )}
            </div>
          </div>
          
          {/* Progress bar */}
          <Progress value={progressPercentage} className="h-3 mb-4" />
          
          {/* Statistics */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-green-600">{successItems}</p>
              <p className="text-sm text-muted-foreground">Successful</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{failedItems}</p>
              <p className="text-sm text-muted-foreground">Failed</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">{totalItems - processedItems}</p>
              <p className="text-sm text-muted-foreground">Remaining</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Failed items details */}
      {failedItems > 0 && items.some(item => item.status === "failed") && (
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Failed Items</h3>
            <div className="space-y-3">
              {items
                .filter(item => item.status === "failed")
                .map(item => (
                  <Alert key={item.id} variant="destructive">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <AlertDescription className="font-medium">
                          {item.title}
                        </AlertDescription>
                        {item.errorMessage && (
                          <div className="mt-2">
                            <button
                              className="text-sm text-destructive/70 hover:text-destructive underline"
                              onClick={() => toggleErrorExpansion(item.id)}
                            >
                              {expandedErrors.includes(item.id) ? "Hide error" : "Show error"}
                            </button>
                            {expandedErrors.includes(item.id) && (
                              <p className="mt-1 text-sm text-destructive/70">
                                {item.errorMessage}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                      {onRetry && (
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => onRetry(item.id)}
                        >
                          <RefreshCw className="h-3 w-3 mr-1" />
                          Retry
                        </Button>
                      )}
                    </div>
                  </Alert>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Recent activity (optional, can show last few processed items) */}
      {status === "running" && items.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="space-y-2">
              {items
                .filter(item => item.status === "processing" || item.status === "completed")
                .slice(-5)
                .reverse()
                .map(item => (
                  <div key={item.id} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{item.title}</span>
                    <span className={
                      item.status === "completed" 
                        ? "text-green-600" 
                        : "text-blue-600"
                    }>
                      {item.status === "completed" ? "Completed" : "Processing..."}
                    </span>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Note: This component is prepared for WebSocket integration
// To add real-time updates:
// 1. Create a WebSocket connection in the useEffect hook
// 2. Listen for job update events
// 3. Update the component props through a parent component that manages the WebSocket connection
// 4. Handle connection errors and reconnection logic
// 5. Clean up the connection when component unmounts
