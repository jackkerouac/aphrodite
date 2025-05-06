import { HomeIcon, PlayIcon, EyeIcon, ClockIcon, ScrollTextIcon, CalendarIcon, SettingsIcon, UserIcon, KeyIcon, VolumeIcon, MonitorIcon, CheckCircleIcon } from "lucide-react";

export type Route = {
  path: string;
  name: string;
  icon: typeof HomeIcon;
  children?: Route[];
};

export const routes = {
  dashboard: {
    path: "/",
    name: "Dashboard",
    icon: HomeIcon
  },
  runAphrodite: {
    path: "/run",
    name: "Run Aphrodite",
    icon: PlayIcon
  },
  preview: {
    path: "/preview",
    name: "Preview",
    icon: EyeIcon
  },
  jobHistory: {
    path: "/history",
    name: "Job History",
    icon: ClockIcon
  },
  logs: {
    path: "/logs",
    name: "Logs",
    icon: ScrollTextIcon
  },
  scheduler: {
    path: "/scheduler",
    name: "Scheduler",
    icon: CalendarIcon
  },
  settings: {
    path: "/settings",
    name: "Settings",
    icon: SettingsIcon,
    children: [
      {
        path: "/settings/api",
        name: "API Settings",
        icon: KeyIcon
      },
      {
        path: "/settings/audio-badge",
        name: "Audio Badge Settings",
        icon: VolumeIcon
      },
      {
        path: "/settings/resolution-badge",
        name: "Resolution Badge Settings",
        icon: MonitorIcon
      },
      {
        path: "/settings/review-badge",
        name: "Review Badge Settings",
        icon: CheckCircleIcon
      }
    ]
  }
};

export const mainNavItems = [
  routes.dashboard,
  routes.runAphrodite,
  routes.preview,
  routes.jobHistory,
  routes.logs,
  routes.scheduler,
  routes.settings
];
