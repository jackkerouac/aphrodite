import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Library Status</CardTitle>
            <CardDescription>Overview of your media library</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Library status information will appear here.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest jobs and processing</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Recent activity will appear here.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Connection and resource metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <p>System status information will appear here.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
