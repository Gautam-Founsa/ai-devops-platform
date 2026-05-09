import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function SecurityPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Security</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Misconfiguration, secrets, and CVE enrichment are planned for Phase 5.
      </Card>
    </AppShell>
  );
}

