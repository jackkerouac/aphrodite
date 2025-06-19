'use client';

import { useState, useEffect } from 'react';
import { Sidebar } from './sidebar';
import { MobileHeader } from './mobile-header';
import { cn } from '@/lib/utils';
import { Toaster } from 'sonner';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  return (
    <div className="min-h-screen bg-background flex">
      {/* Mobile overlay */}
      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0',
          isMobile ? (sidebarOpen ? 'translate-x-0' : '-translate-x-full') : 'translate-x-0'
        )}
      >
        <Sidebar />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <MobileHeader onMenuClick={() => setSidebarOpen(true)} />

        {/* Page content */}
        <main className="flex-1 p-4 w-full max-w-screen-xl mx-auto overflow-y-auto">
          {children}

          {/* Footer */}
          <footer className="mt-8 py-4 text-center text-muted-foreground text-sm">
            <p>Aphrodite © 2025</p>
          </footer>
        </main>
      </div>
      
      {/* Toast notifications */}
      <Toaster position="top-right" closeButton richColors />
    </div>
  );
}