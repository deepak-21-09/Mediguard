"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Pill,
  Activity,
  MessageSquare,
  Calendar,
  FileText,
  Bell,
  User,
  Shield,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/medications", label: "Medications", icon: Pill },
  { href: "/dashboard/symptoms", label: "Symptoms", icon: Activity },
  { href: "/dashboard/chat", label: "MedAgent AI", icon: MessageSquare },
  { href: "/dashboard/appointments", label: "Appointments", icon: Calendar },
  { href: "/dashboard/reminders", label: "Reminders", icon: Bell },
  { href: "/dashboard/reports", label: "Reports", icon: FileText },
  { href: "/dashboard/emergency", label: "Emergency Card", icon: AlertTriangle },
  { href: "/dashboard/profile", label: "Profile", icon: User },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen bg-[#1E3A5F] text-white flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-white/10">
        <Shield className="w-6 h-6 text-teal-300" />
        <span className="text-xl font-bold">MediGuard</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 text-sm font-medium transition",
              pathname === href || pathname.startsWith(href + "/")
                ? "bg-white/15 text-white"
                : "text-blue-200 hover:bg-white/10 hover:text-white"
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-white/10 text-xs text-blue-300">
        MediGuard v1.0 — Not medical advice
      </div>
    </aside>
  );
}
