import { Bell, Search } from "lucide-react";

import { Sidebar } from "@/components/layout/sidebar";
import { Button } from "@/components/ui/button";

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="min-w-0 flex-1">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-border bg-white/95 px-4 backdrop-blur md:px-8">
          <div className="flex min-w-0 items-center gap-3 rounded-md border border-border bg-background px-3 py-2 text-sm text-muted-foreground md:w-96">
            <Search className="h-4 w-4" aria-hidden />
            <span className="truncate">Search services, incidents, clusters</span>
          </div>
          <Button variant="secondary" aria-label="Notifications" className="h-10 w-10 px-0">
            <Bell className="h-4 w-4" aria-hidden />
          </Button>
        </header>
        <div className="px-4 py-6 md:px-8">{children}</div>
      </main>
    </div>
  );
}

