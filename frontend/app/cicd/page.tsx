import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function CicdPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">CI/CD</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Pipeline analysis, caching suggestions, and parallelization recommendations start in Phase 4.
      </Card>
    </AppShell>
  );
}

