import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { mainNavItems } from "@/lib/routes";
import { GithubIcon, ChevronDownIcon, ChevronRightIcon } from "lucide-react";
import { useState } from "react";

export default function Sidebar() {
  const { pathname } = useLocation();
  const version = "v0.1.0"; // Version number
  const [openSection, setOpenSection] = useState("Settings");

  const toggleSection = (sectionName: string) => {
    if (openSection === sectionName) {
      setOpenSection("");
    } else {
      setOpenSection(sectionName);
    }
  };

  return (
    <div className="hidden md:flex h-screen w-64 flex-col fixed inset-y-0 z-50 border-r bg-background">
      {/* Sidebar Header with Logo */}
      <div className="flex flex-col h-32 items-center justify-center border-b px-6">
        <img 
          src="/aphrodite_logo_dark.png" 
          alt="Aphrodite Logo" 
          className="h-16 w-auto mb-2" 
        />
        <Link to="/" className="flex items-center">
          <span className="text-xl font-bold text-aphrodite-purple">Aphrodite</span>
        </Link>
      </div>
      
      {/* Navigation Links */}
      <div className="flex-1 overflow-auto py-4">
        <nav className="grid items-start px-4 text-sm font-medium gap-1">
          {mainNavItems.map((item, index) => {
            const Icon = item.icon;
            const hasChildren = item.children && item.children.length > 0;
            const isOpen = openSection === item.name;
            const isActive = pathname === item.path || 
                            (hasChildren && item.children?.some(child => pathname === child.path));
            
            return (
              <div key={index} className="space-y-1">
                {hasChildren ? (
                  <button
                    onClick={() => toggleSection(item.name)}
                    className={cn(
                      "w-full flex items-center justify-between gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary hover:bg-accent",
                      isActive && "text-primary"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="h-4 w-4" />
                      <span>{item.name}</span>
                    </div>
                    {isOpen ? (
                      <ChevronDownIcon className="h-4 w-4" />
                    ) : (
                      <ChevronRightIcon className="h-4 w-4" />
                    )}
                  </button>
                ) : (
                  <Link
                    to={item.path}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary hover:bg-accent",
                      pathname === item.path && "bg-accent text-primary"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                )}
                
                {/* Show children if section is open */}
                {hasChildren && isOpen && (
                  <div className="pl-6 space-y-1">
                    {item.children?.map((child, childIndex) => {
                      const ChildIcon = child.icon;
                      return (
                        <Link
                          key={childIndex}
                          to={child.path}
                          className={cn(
                            "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary hover:bg-accent",
                            pathname === child.path && "bg-accent text-primary"
                          )}
                        >
                          <ChildIcon className="h-4 w-4" />
                          <span>{child.name}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </div>
      
      {/* Sidebar Footer */}
      <div className="mt-auto border-t px-6 py-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">{version}</span>
          <div className="flex items-center space-x-2">
            <a 
              href="https://github.com/yourusername/aphrodite" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              <GithubIcon className="h-4 w-4" />
            </a>
            <a 
              href="https://ko-fi.com/yourusername" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M5 9h14l1 10H4L5 9z" />
                <path d="M4.5 6h15" />
                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
