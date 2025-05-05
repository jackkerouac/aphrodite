import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import Sidebar from "@/components/sidebar"
import { Toaster } from "@/components/ui/sonner.jsx"

// Import pages
import Dashboard from "@/pages/dashboard"
import RunAphrodite from "@/pages/run-aphrodite"
import Preview from "@/pages/preview"
import JobHistory from "@/pages/job-history"
import Logs from "@/pages/logs"
import Scheduler from "@/pages/scheduler"
import ApiSettingsPage from "@/pages/settings/api"

// Placeholder components for each settings page
const UserSettings = () => <div>User Settings Page</div>;
const AudioBadgeSettings = () => <div>Audio Badge Settings Page</div>;
const ResolutionBadgeSettings = () => <div>Resolution Badge Settings Page</div>;
const ReviewBadgeSettings = () => <div>Review Badge Settings Page</div>;

// Main settings page component
const Settings = () => (
  <div>
    <h1>Settings Page</h1>
    <p>Please select a settings category from the sidebar</p>
  </div>
);

function App() {
  return (
    <Router>
      <div className="flex min-h-screen">
        <Toaster position="top-right" closeButton richColors />
        <Sidebar />
        <div className="flex-1 flex flex-col ml-64">
          <main className="flex-1 p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/run-aphrodite" element={<RunAphrodite />} />
              <Route path="/preview" element={<Preview />} />
              <Route path="/job-history" element={<JobHistory />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="/scheduler" element={<Scheduler />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/settings/user" element={<UserSettings />} />
              <Route path="/settings/api" element={<ApiSettingsPage />} />
              <Route path="/settings/audio-badge" element={<AudioBadgeSettings />} />
              <Route path="/settings/resolution-badge" element={<ResolutionBadgeSettings />} />
              <Route path="/settings/review-badge" element={<ReviewBadgeSettings />} />
            </Routes>
          </main>
        </div>
      </div>
      {/* The Toaster component will display notifications */}
    </Router>
  )
}

export default App
