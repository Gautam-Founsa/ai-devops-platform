"use client";

import { FormEvent, useState } from "react";
import {
  Bug,
  CheckCircle2,
  FileWarning,
  KeyRound,
  LockKeyhole,
  RefreshCw,
  ScanSearch,
  ShieldAlert,
  Siren,
  Wrench
} from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type Finding = {
  id: string | null;
  scanner: string;
  category: string;
  severity: string;
  title: string;
  description: string;
  file_path: string | null;
  line: number | null;
  cve_id: string | null;
  package_name: string | null;
  installed_version: string | null;
  fixed_version: string | null;
  recommendation: string;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string | null;
};

type ToolStatus = {
  name: string;
  enabled: boolean;
  integrated: boolean;
  mode: string;
  detail: string;
};

type ScanResponse = {
  repository: string | null;
  summary: Record<string, number>;
  findings: Finding[];
  recommendations: string[];
  tools: ToolStatus[];
};

const sampleFiles = [
  {
    path: "Dockerfile",
    content: "FROM node:latest\nUSER root\nRUN npm install express@4.16.0\n"
  },
  {
    path: "terraform/db.tf",
    content:
      'resource "aws_security_group" "db" { ingress { from_port = 5432 cidr_blocks = ["0.0.0.0/0"] } }\n'
  },
  {
    path: ".env.example",
    content: 'AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"\n'
  }
];

export default function SecurityPage() {
  const [token, setToken] = useState("");
  const [repository, setRepository] = useState("acme/checkout-api");
  const [path, setPath] = useState("Dockerfile");
  const [content, setContent] = useState(sampleFiles[0].content);
  const [scan, setScan] = useState<ScanResponse | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [status, setStatus] = useState("");

  async function runScan(event: FormEvent) {
    event.preventDefault();
    setStatus("Running security scan");
    const response = await apiFetch<ScanResponse>("/security/scan", {
      method: "POST",
      token,
      body: JSON.stringify({
        repository,
        include_trivy: true,
        include_semgrep: true,
        files: [{ path, content }]
      })
    });
    setScan(response);
    setFindings(response.findings);
    setStatus("Security scan complete");
  }

  async function runDemoScan() {
    setStatus("Running demo scan");
    const response = await apiFetch<ScanResponse>("/security/scan", {
      method: "POST",
      token,
      body: JSON.stringify({
        repository,
        include_trivy: true,
        include_semgrep: true,
        files: sampleFiles
      })
    });
    setScan(response);
    setFindings(response.findings);
    setStatus("Demo scan complete");
  }

  async function loadFindings() {
    setStatus("Loading findings");
    const response = await apiFetch<Finding[]>("/security/findings", { token });
    setFindings(response);
    setStatus("Findings loaded");
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Security Scanner</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Detect secrets, misconfigurations, vulnerable packages, and CI/IaC risk with Trivy and Semgrep hooks.
          </p>
        </div>
        {status ? (
          <div className="rounded-md border border-border bg-white px-3 py-2 text-sm">{status}</div>
        ) : null}
      </div>

      <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <ScanSearch className="h-5 w-5 text-primary" aria-hidden />
            <h2 className="text-base font-semibold">Scan source content</h2>
          </div>
          <form onSubmit={runScan} className="grid gap-3">
            <input
              value={token}
              onChange={(event) => setToken(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Bearer token"
            />
            <input
              value={repository}
              onChange={(event) => setRepository(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Repository"
            />
            <input
              value={path}
              onChange={(event) => setPath(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="File path"
            />
            <textarea
              value={content}
              onChange={(event) => setContent(event.target.value)}
              className="min-h-[420px] rounded-md border border-border bg-slate-950 p-4 font-mono text-xs leading-5 text-white outline-none focus:ring-2 focus:ring-primary"
              spellCheck={false}
            />
            <div className="flex flex-wrap gap-3">
              <Button disabled={!token || !content} type="submit">
                <ShieldAlert className="h-4 w-4" aria-hidden />
                Scan file
              </Button>
              <Button disabled={!token} type="button" variant="secondary" onClick={runDemoScan}>
                Run demo scan
              </Button>
              <Button disabled={!token} type="button" variant="secondary" onClick={loadFindings}>
                <RefreshCw className="h-4 w-4" aria-hidden />
                Load findings
              </Button>
            </div>
          </form>
        </Card>

        <div className="grid gap-4">
          <section className="grid gap-4 md:grid-cols-4">
            <MetricCard icon={Siren} label="Critical" value={`${scan?.summary.critical ?? countSeverity(findings, "critical")}`} detail="block release" />
            <MetricCard icon={ShieldAlert} label="High" value={`${scan?.summary.high ?? countSeverity(findings, "high")}`} detail="fix quickly" />
            <MetricCard icon={FileWarning} label="Medium" value={`${scan?.summary.medium ?? countSeverity(findings, "medium")}`} detail="planned fix" />
            <MetricCard icon={CheckCircle2} label="Total" value={`${scan?.summary.total ?? findings.length}`} detail="open findings" />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <Card className="p-5">
              <div className="mb-4 flex items-center gap-2">
                <Wrench className="h-5 w-5 text-primary" aria-hidden />
                <h2 className="text-base font-semibold">Scanner integrations</h2>
              </div>
              <div className="grid gap-3">
                {(scan?.tools ?? fallbackTools).map((tool) => (
                  <div key={tool.name} className="rounded-md border border-border bg-background p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="font-medium">{tool.name}</div>
                      <span className="rounded-sm bg-muted px-2 py-1 text-xs">{tool.mode}</span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{tool.detail}</p>
                  </div>
                ))}
              </div>
            </Card>

            <AdviceCard title="Security recommendations" items={scan?.recommendations ?? defaultRecommendations} />
          </section>

          <Card className="p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-base font-semibold">Findings</h2>
              <span className="text-xs text-muted-foreground">{findings.length} results</span>
            </div>
            <div className="grid gap-3">
              {findings.length ? (
                findings.map((finding, index) => (
                  <FindingCard key={finding.id ?? `${finding.title}-${index}`} finding={finding} />
                ))
              ) : (
                <div className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">
                  Run a scan or load persisted findings.
                </div>
              )}
            </div>
          </Card>
        </div>
      </section>
    </AppShell>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail
}: {
  icon: typeof Siren;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        <Icon className="h-4 w-4 text-primary" aria-hidden />
      </div>
      <div className="mt-3 text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-muted-foreground">{detail}</div>
    </Card>
  );
}

function AdviceCard({ title, items }: { title: string; items: string[] }) {
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center gap-2">
        <LockKeyhole className="h-5 w-5 text-primary" aria-hidden />
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      <div className="grid gap-2">
        {items.map((item) => (
          <div key={item} className="rounded-md border border-border bg-background p-3 text-sm leading-6">
            {item}
          </div>
        ))}
      </div>
    </Card>
  );
}

function FindingCard({ finding }: { finding: Finding }) {
  const Icon = finding.category === "secret" ? KeyRound : finding.category === "vulnerability" ? Bug : FileWarning;
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-medium">
          <Icon className="h-4 w-4 text-destructive" aria-hidden />
          {finding.title}
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="rounded-sm bg-muted px-2 py-1">{finding.scanner}</span>
          <span className="rounded-sm bg-muted px-2 py-1">{finding.severity}</span>
        </div>
      </div>
      <p className="mt-2 text-sm leading-6">{finding.description}</p>
      <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
        {finding.file_path ? <span>{finding.file_path}{finding.line ? `:${finding.line}` : ""}</span> : null}
        {finding.cve_id ? <span>{finding.cve_id}</span> : null}
        {finding.package_name ? <span>{finding.package_name} {finding.installed_version ?? ""}</span> : null}
        {finding.fixed_version ? <span>fixed {finding.fixed_version}</span> : null}
      </div>
      <div className="mt-3 rounded-md border border-border bg-white p-3 text-sm leading-6">
        {finding.recommendation}
      </div>
    </div>
  );
}

function countSeverity(findings: Finding[], severity: string) {
  return findings.filter((finding) => finding.severity === severity).length;
}

const fallbackTools: ToolStatus[] = [
  {
    name: "trivy",
    enabled: true,
    integrated: true,
    mode: "static-fallback",
    detail: "Trivy integration is wired; install the binary in the backend image to enable native scans."
  },
  {
    name: "semgrep",
    enabled: true,
    integrated: true,
    mode: "static-fallback",
    detail: "Semgrep integration is wired; install the binary in the backend image to enable native scans."
  }
];

const defaultRecommendations = [
  "Fail CI on critical secrets, public database exposure, and exploitable critical CVEs.",
  "Run Trivy for image, filesystem, IaC, and dependency scanning in CI.",
  "Run Semgrep with organization-approved rule packs for code security checks."
];

