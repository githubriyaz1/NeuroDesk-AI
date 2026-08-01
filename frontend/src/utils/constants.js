export const APP_NAME = "NeuroDesk AI";
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const NAVIGATION_ITEMS = [
  { id: "dashboard", label: "Dashboard", path: "/", icon: "LayoutDashboard" },
  { id: "workspace", label: "Workspace", path: "/workspace", icon: "FolderKanban" },
  { id: "ai-studio", label: "AI Studio", path: "/ai-studio", icon: "Cpu" },
  { id: "project-generator", label: "AI Project Generator", path: "/project-generator", icon: "Sparkles" },
  { id: "ai-chat", label: "AI Chat", path: "/chat", icon: "MessageSquareText" },
  { id: "workflows", label: "Workflows", path: "/workflows", icon: "GitFork" },
  { id: "profile", label: "Profile Settings", path: "/profile", icon: "User" },
  { id: "settings", label: "Settings", path: "/settings", icon: "Settings" },
];
