import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function DeploymentsPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Deployments</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Deployment regression analysis is staged for Phase 3.
      </Card>
    </AppShell>
  );
}

