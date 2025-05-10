// src/App.jsx

import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import Sidebar from "@/components/sidebar"
import { Toaster } from "@/components/ui/sonner.jsx"
import { UserProvider } from "@/contexts/UserContext"
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Import pages
import Dashboard from "@/pages/dashboard"
import RunAphrodite from "@/pages/run-aphrodite"
import Preview from "@/pages/preview"
import JobHistory from "@/pages/job-history"
import Logs from "@/pages/logs"
import Scheduler from "@/pages/scheduler"
import ApiSettingsPage from "@/pages/settings/api"
import TestLibraryItems from "@/pages/test-library-items.tsx";
import TestIntegration from "@/pages/test-integration.tsx";
import TestJobs from "@/pages/test-jobs.tsx";
import { TestWebSocket } from "@/pages/test-websocket.tsx";
import { UserSelector } from "@/components/user-selector"

// Placeholder components for each settings page
const UserSettings = () => (
  <div className="max-w-2xl mx-auto">
    <h1 className="text-2xl font-bold mb-6">User Settings</h1>
    <UserSelector />
  </div>
);

// Main settings page component
const Settings = () => (
  <div>
    <h1>Settings Page</h1>
    <p>Please select a settings category from the sidebar</p>
  </div>
);

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <UserProvider>
        <Router>
          <div className="flex min-h-screen">
            <Toaster position="top-right" closeButton richColors />
            <Sidebar />
            <div className="flex-1 flex flex-col ml-64">
              <main className="flex-1 p-6">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/run" element={<RunAphrodite />} />
                  <Route path="/preview" element={<Preview />} />
                  <Route path="/history" element={<JobHistory />} />
                  <Route path="/logs" element={<Logs />} />
                  <Route path="/scheduler" element={<Scheduler />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/settings/user" element={<UserSettings />} />
                  <Route path="/settings/api" element={<ApiSettingsPage />} />
                <Route path="/test-library-items" element={<TestLibraryItems />} />
                <Route path="/test-integration" element={<TestIntegration />} />
                <Route path="/test-jobs" element={<TestJobs />} />
                <Route path="/test-websocket" element={<TestWebSocket />} />
                </Routes>
              </main>
            </div>
          </div>
          {/* The Toaster component will display notifications */}
        </Router>
      </UserProvider>
    </QueryClientProvider>
  )
}

export default App