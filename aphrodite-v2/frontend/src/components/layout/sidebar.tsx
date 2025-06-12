'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Home,
  BarChart3,
  Image,
  Clock,
  Eye,
  Wrench,
  Settings,
  Info,
  Github,
  Coffee
} from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { ThemeSwitcher } from '@/components/ui/theme-switcher';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Poster Manager', href: '/poster-manager', icon: Image },
  { name: 'Schedules', href: '/schedules', icon: Clock },
  { name: 'Preview', href: '/preview', icon: Eye },
  { name: 'Maintenance', href: '/maintenance', icon: Wrench },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'About', href: '/about', icon: Info },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="bg-background w-80 min-h-screen border-r">
      <div className="px-4 py-6">
        {/* Logo Section */}
        <div className="flex flex-col items-center mb-6">
          <div className="flex items-center justify-center">
            <img 
              src="/images/android-chrome-192x192.png" 
              alt="Aphrodite logo"
              className="w-20 h-20"
            />
          </div>
          <h2 className="mt-2 text-xl font-bold">Aphrodite</h2>
        </div>
        
        {/* Navigation Menu */}
        <nav className="space-y-1">
          <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Main Menu
          </div>
          
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>
        
        {/* Divider */}
        <div className="my-8 border-t" />
        
        {/* Footer with avatar, theme switcher, and links */}
        <div className="flex items-center justify-between mt-8 p-4">
          <Avatar className="w-8 h-8">
            <AvatarImage 
              src="/images/professor_relaxing.png" 
              alt="Professor Relaxing Avatar"
            />
            <AvatarFallback>PR</AvatarFallback>
          </Avatar>
          
          <div className="flex gap-3 items-center">
            <ThemeSwitcher />
            <a 
              href="https://github.com/jackkerouac/aphrodite" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:opacity-80 transition-opacity"
            >
              <img src="/images/github_light.png" alt="GitHub" className="w-8 h-8" />
            </a>
            <a 
              href="https://ko-fi.com/jackkerouac" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:opacity-80 transition-opacity"
            >
              <img src="/images/kofi.png" alt="Ko-fi" className="w-8 h-8" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
