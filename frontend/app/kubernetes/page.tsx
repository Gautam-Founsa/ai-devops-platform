import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function KubernetesPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Kubernetes</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Cluster health, pod analysis, and YAML generation are planned for Phase 3.
      </Card>
    </AppShell>
  );
}

