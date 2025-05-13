import React from "react";
import { useRunAphrodite } from "./RunAphroditeContext";

export const SummaryStep: React.FC = () => {
  const { stepData, jobStatus } = useRunAphrodite();

  return (
    <div className="space-y-4">
      <p className="text-muted-foreground">Review the results of the badge application process.</p>
      <div className="border rounded-lg p-4">
        <h3 className="font-medium mb-2">Job Summary</h3>
        
        {jobStatus && (
          <div className="space-y-2">
            <p className="text-sm">
              Status: <span className="font-medium">{jobStatus.status}</span>
            </p>
            <p className="text-sm">
              Total items: {jobStatus.totalItems || 0}
            </p>
            <p className="text-sm">
              Successfully processed: {(jobStatus.totalItems || 0) - (jobStatus.failedCount || 0)}
            </p>
            {jobStatus.failedCount !== undefined && jobStatus.failedCount > 0 && (
              <p className="text-sm text-destructive">
                Failed items: {jobStatus.failedCount}
              </p>
            )}
          </div>
        )}
        
        <div className="mt-4">
          <h4 className="text-sm font-medium mb-2">Applied badges:</h4>
          <div className="flex flex-wrap gap-2">
            {stepData.enabledBadges?.map(badgeType => (
              <div key={badgeType} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/20 text-primary">
                {badgeType.charAt(0).toUpperCase() + badgeType.slice(1)} Badge
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
