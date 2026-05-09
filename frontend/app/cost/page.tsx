import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function CostPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Cost</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Rightsizing and idle resource recommendations are planned for Phase 5.
      </Card>
    </AppShell>
  );
}

