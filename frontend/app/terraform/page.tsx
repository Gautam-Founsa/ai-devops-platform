import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

export default function TerraformPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-semibold">Terraform</h1>
      <Card className="mt-6 p-5 text-sm text-muted-foreground">
        Natural language IaC generation begins in Phase 4.
      </Card>
    </AppShell>
  );
}

