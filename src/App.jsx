import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import Sidebar from "@/components/sidebar"

// Import real API settings page
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
        <Sidebar />
        <div className="flex-1 flex flex-col ml-64">
          <main className="flex-1 p-6">
            <Routes>
              <Route path="/" element={
                <div>
                  <h1 className="text-5xl text-center p-16 text-aphrodite-purple">Aphrodite UI Project</h1>
                  <div className="flex flex-col items-center justify-center">
                    <p className="mb-4">Welcome to the Aphrodite UI Project!</p>
                    <Button variant="outline">Push Me!</Button>
                  </div>
                </div>
              } />
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
    </Router>
  )
}

export default App
