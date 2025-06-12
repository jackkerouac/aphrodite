import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Activity, Image, Clock, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to Aphrodite v2 - Your media poster enhancement system
        </p>
      </div>

      {/* System Status Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Status</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-green-600 border-green-600">
                Online
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Backend services running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Media Items</CardTitle>
            <Image className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2,456</div>
            <p className="text-xs text-muted-foreground">
              Total items in library
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">
              Currently processing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">
              Posters enhanced
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Current Jobs */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest job processing activity
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Processing Movie Collection</span>
                <Badge variant="secondary">Running</Badge>
              </div>
              <Progress value={75} className="h-2" />
              <p className="text-xs text-muted-foreground">75% complete - 180/240 items</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">TV Shows Badge Update</span>
                <Badge variant="outline">Queued</Badge>
              </div>
              <Progress value={0} className="h-2" />
              <p className="text-xs text-muted-foreground">Waiting to start - 45 items</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Library Scan</span>
                <Badge className="bg-green-600">Complete</Badge>
              </div>
              <Progress value={100} className="h-2" />
              <p className="text-xs text-muted-foreground">Finished 2 minutes ago</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Information</CardTitle>
            <CardDescription>
              Current system status and configuration
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium">Version</p>
                <p className="text-muted-foreground">v2.0.0-beta</p>
              </div>
              <div>
                <p className="font-medium">Jellyfin Status</p>
                <Badge variant="outline" className="text-green-600 border-green-600">
                  Connected
                </Badge>
              </div>
              <div>
                <p className="font-medium">Database</p>
                <p className="text-muted-foreground">PostgreSQL</p>
              </div>
              <div>
                <p className="font-medium">Queue</p>
                <p className="text-muted-foreground">Redis</p>
              </div>
              <div>
                <p className="font-medium">Workers</p>
                <p className="text-muted-foreground">2 active</p>
              </div>
              <div>
                <p className="font-medium">Uptime</p>
                <p className="text-muted-foreground">2d 14h 32m</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 md:grid-cols-3">
            <button className="flex items-center justify-center gap-2 p-4 border rounded-lg hover:bg-muted transition-colors">
              <Activity className="h-4 w-4" />
              <span>Start Library Scan</span>
            </button>
            <button className="flex items-center justify-center gap-2 p-4 border rounded-lg hover:bg-muted transition-colors">
              <Image className="h-4 w-4" />
              <span>Process All Media</span>
            </button>
            <button className="flex items-center justify-center gap-2 p-4 border rounded-lg hover:bg-muted transition-colors">
              <Clock className="h-4 w-4" />
              <span>View Job Queue</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}