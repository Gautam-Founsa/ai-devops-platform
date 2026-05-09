import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function IncidentsPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Incidents</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Incident analysis arrives in Phase 2. Phase 1 provides auth, dashboard, chat, and metrics.
      </Card>
    </AppShell>
  );
}

