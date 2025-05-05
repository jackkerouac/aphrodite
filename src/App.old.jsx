import './App.css'
import { Button } from "@/components/ui/button"
// Commenting out the problematic imports until we properly setup the components
// import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
// import { AppSidebar } from "@/components/app-sidebar"

function App() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-5xl text-center p-16 text-aphrodite-purple">Aphrodite with Vite, React, and Tailwind v4 and Shadcn UI</h1>
      <Button variant="outline">Push Me!</Button>
    </div>
  )
}

export default App
