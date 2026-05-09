import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Settings</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Organization, RBAC, OAuth, and integrations will expand from the Phase 1 auth foundation.
      </Card>
    </AppShell>
  );
}

