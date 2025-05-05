import { Outlet, NavLink } from "react-router-dom";

export default function Settings() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      <p className="text-muted-foreground">
        Manage your application settings and preferences.
      </p>
      
      <div className="flex flex-col md:flex-row gap-6">
        <aside className="md:w-1/4">
          <nav className="space-y-1">
            <NavLink 
              to="/settings/api"
              className={({ isActive }) => 
                `block px-4 py-2 rounded-md ${isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`
              }
            >
              API Settings
            </NavLink>
            {/* Add more settings links here */}
          </nav>
        </aside>
        <div className="flex-1">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
