"use client";

import { FormEvent, useState } from "react";
import {
  CheckCircle2,
  GitBranch,
  Gauge,
  LockKeyhole,
  Play,
  Rocket,
  ShieldAlert,
  Sparkles,
  Split,
  TimerReset,
  Workflow
} from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type Finding = {
  severity: string;
  category: string;
  title: string;
  detail: string;
  recommendation: string;
};

type JobSummary = {
  name: string;
  runs_on: string;
  steps: number;
  uses_cache: boolean;
  uploads_artifacts: boolean;
  has_permissions: boolean;
  has_timeout: boolean;
  matrix: boolean;
};

type Analysis = {
  workflow_name: string;
  triggers: string[];
  jobs: JobSummary[];
  findings: Finding[];
  caching_suggestions: string[];
  parallelization_suggestions: string[];
  security_best_practices: string[];
  score: number;
};

type OptimizeResponse = {
  optimized_workflow_yaml: string;
  changes: string[];
  analysis: Analysis;
};

const sampleWorkflow = `name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - run: npm test
      - run: npm run build`;

export default function CicdPage() {
  const [token, setToken] = useState("");
  const [workflowYaml, setWorkflowYaml] = useState(sampleWorkflow);
  const [repository, setRepository] = useState("acme/checkout-api");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [optimized, setOptimized] = useState<OptimizeResponse | null>(null);
  const [status, setStatus] = useState("");

  async function analyze(event: FormEvent) {
    event.preventDefault();
    setStatus("Analyzing workflow");
    const response = await apiFetch<Analysis>("/cicd/analyze", {
      method: "POST",
      token,
      body: JSON.stringify({ workflow_yaml: workflowYaml, repository })
    });
    setAnalysis(response);
    setStatus("Analysis ready");
  }

  async function optimize() {
    setStatus("Optimizing workflow");
    const response = await apiFetch<OptimizeResponse>("/cicd/optimize", {
      method: "POST",
      token,
      body: JSON.stringify({ workflow_yaml: workflowYaml, goals: ["cache", "parallel", "security"] })
    });
    setOptimized(response);
    setAnalysis(response.analysis);
    setStatus("Optimized workflow generated");
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">CI/CD Analyzer</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Parse GitHub Actions workflows, detect inefficiencies, and generate safer faster pipelines.
          </p>
        </div>
        {status ? (
          <div className="rounded-md border border-border bg-white px-3 py-2 text-sm">{status}</div>
        ) : null}
      </div>

      <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <Workflow className="h-5 w-5 text-primary" aria-hidden />
            <h2 className="text-base font-semibold">GitHub Actions workflow</h2>
          </div>
          <form onSubmit={analyze} className="grid gap-3">
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
            <textarea
              value={workflowYaml}
              onChange={(event) => setWorkflowYaml(event.target.value)}
              className="min-h-[520px] rounded-md border border-border bg-slate-950 p-4 font-mono text-xs leading-5 text-white outline-none focus:ring-2 focus:ring-primary"
              spellCheck={false}
            />
            <div className="flex flex-wrap gap-3">
              <Button disabled={!token || !workflowYaml} type="submit">
                <Play className="h-4 w-4" aria-hidden />
                Analyze
              </Button>
              <Button disabled={!token || !workflowYaml} type="button" variant="secondary" onClick={optimize}>
                <Sparkles className="h-4 w-4" aria-hidden />
                Optimize
              </Button>
            </div>
          </form>
        </Card>

        <div className="grid gap-4">
          <section className="grid gap-4 md:grid-cols-4">
            <MetricCard icon={Gauge} label="Score" value={analysis ? `${analysis.score}` : "-"} detail="pipeline health" />
            <MetricCard icon={GitBranch} label="Triggers" value={analysis ? `${analysis.triggers.length}` : "-"} detail={analysis?.triggers.join(", ") ?? "events"} />
            <MetricCard icon={Rocket} label="Jobs" value={analysis ? `${analysis.jobs.length}` : "-"} detail="workflow jobs" />
            <MetricCard icon={ShieldAlert} label="Findings" value={analysis ? `${analysis.findings.length}` : "-"} detail="risks and inefficiencies" />
          </section>

          <Card className="p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-base font-semibold">Job summary</h2>
              <span className="text-xs text-muted-foreground">{analysis?.workflow_name ?? "No workflow loaded"}</span>
            </div>
            {analysis ? (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[680px] text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs text-muted-foreground">
                      <th className="py-2 pr-3 font-medium">Job</th>
                      <th className="py-2 pr-3 font-medium">Runner</th>
                      <th className="py-2 pr-3 font-medium">Steps</th>
                      <th className="py-2 pr-3 font-medium">Cache</th>
                      <th className="py-2 pr-3 font-medium">Timeout</th>
                      <th className="py-2 font-medium">Matrix</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysis.jobs.map((job) => (
                      <tr key={job.name} className="border-b border-border">
                        <td className="py-3 pr-3 font-medium">{job.name}</td>
                        <td className="py-3 pr-3">{job.runs_on}</td>
                        <td className="py-3 pr-3">{job.steps}</td>
                        <td className="py-3 pr-3">{job.uses_cache ? "yes" : "no"}</td>
                        <td className="py-3 pr-3">{job.has_timeout ? "yes" : "no"}</td>
                        <td className="py-3">{job.matrix ? "yes" : "no"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">
                Run an analysis to inspect jobs, runners, caching, timeouts, and matrix usage.
              </div>
            )}
          </Card>

          <section className="grid gap-4 lg:grid-cols-2">
            <AdviceCard icon={TimerReset} title="Caching suggestions" items={analysis?.caching_suggestions ?? []} />
            <AdviceCard icon={Split} title="Parallelization suggestions" items={analysis?.parallelization_suggestions ?? []} />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <Card className="p-5">
              <div className="mb-4 flex items-center gap-2">
                <ShieldAlert className="h-5 w-5 text-destructive" aria-hidden />
                <h2 className="text-base font-semibold">Findings</h2>
              </div>
              {analysis?.findings.length ? (
                <div className="grid gap-3">
                  {analysis.findings.map((finding) => (
                    <FindingCard key={`${finding.category}-${finding.title}`} finding={finding} />
                  ))}
                </div>
              ) : (
                <div className="rounded-md border border-border bg-background p-3 text-sm text-muted-foreground">
                  No findings yet.
                </div>
              )}
            </Card>

            <AdviceCard
              icon={LockKeyhole}
              title="Security best practices"
              items={analysis?.security_best_practices ?? defaultSecurity}
            />
          </section>
        </div>
      </section>

      {optimized ? (
        <section className="mt-4 grid gap-4 xl:grid-cols-[360px_1fr]">
          <Card className="p-5">
            <div className="mb-4 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" aria-hidden />
              <h2 className="text-base font-semibold">Optimization changes</h2>
            </div>
            <div className="grid gap-2">
              {optimized.changes.map((change) => (
                <div key={change} className="rounded-md border border-border bg-background p-3 text-sm">
                  {change}
                </div>
              ))}
            </div>
          </Card>
          <Card className="p-5">
            <h2 className="mb-4 text-base font-semibold">Optimized workflow</h2>
            <pre className="max-h-[520px] overflow-auto rounded-md border border-border bg-slate-950 p-4 text-xs leading-5 text-white">
              {optimized.optimized_workflow_yaml}
            </pre>
          </Card>
        </section>
      ) : null}
    </AppShell>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail
}: {
  icon: typeof Gauge;
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
      <div className="mt-1 truncate text-xs text-muted-foreground">{detail}</div>
    </Card>
  );
}

function AdviceCard({
  icon: Icon,
  title,
  items
}: {
  icon: typeof LockKeyhole;
  title: string;
  items: string[];
}) {
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center gap-2">
        <Icon className="h-5 w-5 text-primary" aria-hidden />
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      <div className="grid gap-2">
        {(items.length ? items : ["Run an analysis to populate this panel."]).map((item) => (
          <div key={item} className="rounded-md border border-border bg-background p-3 text-sm leading-6">
            {item}
          </div>
        ))}
      </div>
    </Card>
  );
}

function FindingCard({ finding }: { finding: Finding }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-medium">{finding.title}</div>
        <span className="rounded-sm bg-muted px-2 py-1 text-xs">{finding.severity}</span>
      </div>
      <p className="mt-2 text-sm leading-6">{finding.detail}</p>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{finding.recommendation}</p>
    </div>
  );
}

const defaultSecurity = [
  "Use least-privilege `permissions` at the workflow or job level.",
  "Pin third-party actions to immutable SHAs for production release workflows.",
  "Use OIDC or GitHub secrets for credentials.",
  "Use protected environments for deployments."
];

