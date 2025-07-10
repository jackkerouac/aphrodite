import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function PerformanceTab() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Performance Analytics</CardTitle>
          <CardDescription>
            System performance metrics and bottleneck analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            Performance analytics dashboard will be displayed here.
            This will include CPU usage, memory consumption, processing times,
            and bottleneck identification across different operation types.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
