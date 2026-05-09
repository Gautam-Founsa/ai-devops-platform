import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function LogsPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Logs</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Semantic log search and clustering are planned for Phase 2.
      </Card>
    </AppShell>
  );
}

