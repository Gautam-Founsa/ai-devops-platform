"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Bot,
  Boxes,
  ChartNoAxesCombined,
  CircleDollarSign,
  FileCode2,
  Gauge,
  GitBranch,
  LockKeyhole,
  RadioTower,
  ScrollText,
  Settings,
  ShieldAlert
} from "lucide-react";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/chat", label: "AI Chat", icon: Bot },
  { href: "/incidents", label: "Incidents", icon: ShieldAlert },
  { href: "/metrics", label: "Metrics", icon: ChartNoAxesCombined },
  { href: "/logs", label: "Logs", icon: ScrollText },
  { href: "/deployments", label: "Deployments", icon: GitBranch },
  { href: "/kubernetes", label: "Kubernetes", icon: Boxes },
  { href: "/terraform", label: "Terraform", icon: FileCode2 },
  { href: "/cicd", label: "CI/CD", icon: Activity },
  { href: "/security", label: "Security", icon: LockKeyhole },
  { href: "/cost", label: "Cost", icon: CircleDollarSign },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden min-h-screen w-64 shrink-0 border-r border-border bg-white lg:block">
      <div className="flex h-16 items-center gap-3 border-b border-border px-5">
        <RadioTower className="h-6 w-6 text-primary" aria-hidden />
        <div>
          <div className="text-sm font-semibold">AI DevOps</div>
          <div className="text-xs text-muted-foreground">Infrastructure Copilot</div>
        </div>
      </div>
      <nav className="grid gap-1 p-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex h-10 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground",
                active && "bg-muted font-medium text-foreground"
              )}
            >
              <Icon className="h-4 w-4" aria-hidden />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

