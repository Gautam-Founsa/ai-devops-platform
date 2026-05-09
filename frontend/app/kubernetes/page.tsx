"use client";

import { FormEvent, useState } from "react";
import {
  Boxes,
  BrainCircuit,
  FileCode2,
  Gauge,
  Layers3,
  Play,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  TriangleAlert
} from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type Overview = {
  name: string;
  provider: string;
  region: string;
  status: string;
  nodes_ready: number;
  nodes_total: number;
  namespaces: number;
  pods_running: number;
  pods_pending: number;
  pods_failed: number;
  cpu_request_percent: number;
  memory_request_percent: number;
};

type Pod = {
  name: string;
  namespace: string;
  workload: string;
  status: string;
  restarts: number;
  cpu_millicores: number;
  memory_mib: number;
  age: string;
  node: string;
  reason: string | null;
};

type CrashLoopAnalysis = {
  pod: Pod;
  likely_causes: string[];
  evidence: string[];
  remediation_steps: string[];
};

type Recommendation = {
  target: string;
  namespace: string;
  recommendation: string;
  current: string;
  suggested: string;
  confidence: number;
  rationale: string;
};

type YamlExplanation = {
  kind: string;
  name: string;
  namespace: string;
  summary: string;
  risks: string[];
  recommendations: string[];
};

type GeneratedManifest = {
  yaml: string;
  notes: string[];
};

const sampleYaml = `apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout-api
  namespace: payments
spec:
  replicas: 1
  selector:
    matchLabels:
      app: checkout-api
  template:
    metadata:
      labels:
        app: checkout-api
    spec:
      containers:
        - name: checkout-api
          image: ghcr.io/acme/checkout-api:v42
          ports:
            - containerPort: 8080`;

export default function KubernetesPage() {
  const [token, setToken] = useState("");
  const [overview, setOverview] = useState<Overview | null>(null);
  const [pods, setPods] = useState<Pod[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selectedPod, setSelectedPod] = useState<Pod | null>(null);
  const [analysis, setAnalysis] = useState<CrashLoopAnalysis | null>(null);
  const [yamlText, setYamlText] = useState(sampleYaml);
  const [yamlExplanation, setYamlExplanation] = useState<YamlExplanation | null>(null);
  const [appName, setAppName] = useState("inventory-api");
  const [image, setImage] = useState("ghcr.io/acme/inventory-api:v1");
  const [generated, setGenerated] = useState<GeneratedManifest | null>(null);
  const [status, setStatus] = useState("");

  async function loadCluster() {
    setStatus("Loading cluster intelligence");
    const [overviewResponse, podsResponse, recommendationResponse] = await Promise.all([
      apiFetch<Overview>("/k8s/overview", { token }),
      apiFetch<Pod[]>("/k8s/pods", { token }),
      apiFetch<Recommendation[]>("/k8s/recommendations", { token })
    ]);
    setOverview(overviewResponse);
    setPods(podsResponse);
    setRecommendations(recommendationResponse);
    setSelectedPod(podsResponse.find((pod) => pod.status === "CrashLoopBackOff") ?? podsResponse[0] ?? null);
    setStatus("Cluster snapshot ready");
  }

  async function analyzeCrashLoop(pod = selectedPod) {
    if (!pod) return;
    setStatus(`Analyzing ${pod.name}`);
    const response = await apiFetch<CrashLoopAnalysis>("/k8s/crashloop/analyze", {
      method: "POST",
      token,
      body: JSON.stringify({ namespace: pod.namespace, pod_name: pod.name })
    });
    setAnalysis(response);
    setStatus("CrashLoopBackOff analysis ready");
  }

  async function explainYaml(event: FormEvent) {
    event.preventDefault();
    setStatus("Explaining YAML");
    const response = await apiFetch<YamlExplanation>("/k8s/explain", {
      method: "POST",
      token,
      body: JSON.stringify({ yaml: yamlText })
    });
    setYamlExplanation(response);
    setStatus("YAML explanation ready");
  }

  async function generateManifest(event: FormEvent) {
    event.preventDefault();
    setStatus("Generating manifest");
    const response = await apiFetch<GeneratedManifest>("/k8s/generate", {
      method: "POST",
      token,
      body: JSON.stringify({
        app_name: appName,
        image,
        namespace: "default",
        replicas: 2,
        port: 8080,
        cpu_request: "100m",
        memory_request: "128Mi"
      })
    });
    setGenerated(response);
    setStatus("Manifest generated");
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Kubernetes Intelligence</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Cluster health, pod triage, resource guidance, YAML explanation, and manifest generation.
          </p>
        </div>
        {status ? (
          <div className="rounded-md border border-border bg-white px-3 py-2 text-sm">{status}</div>
        ) : null}
      </div>

      <Card className="mb-4 p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_auto]">
          <input
            value={token}
            onChange={(event) => setToken(event.target.value)}
            className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            placeholder="Bearer token"
          />
          <Button disabled={!token} type="button" onClick={loadCluster}>
            <RefreshCw className="h-4 w-4" aria-hidden />
            Load cluster
          </Button>
        </div>
      </Card>

      <section className="grid gap-4 xl:grid-cols-4">
        <MetricCard icon={Boxes} label="Cluster" value={overview?.name ?? "Not loaded"} detail={overview?.status ?? "waiting"} />
        <MetricCard
          icon={ShieldCheck}
          label="Nodes ready"
          value={overview ? `${overview.nodes_ready}/${overview.nodes_total}` : "-"}
          detail={overview ? `${overview.provider} ${overview.region}` : "provider"}
        />
        <MetricCard
          icon={Layers3}
          label="Pods"
          value={overview ? `${overview.pods_running} running` : "-"}
          detail={overview ? `${overview.pods_pending} pending, ${overview.pods_failed} unhealthy` : "status"}
        />
        <MetricCard
          icon={Gauge}
          label="Requests"
          value={overview ? `${overview.cpu_request_percent}% CPU` : "-"}
          detail={overview ? `${overview.memory_request_percent}% memory` : "capacity"}
        />
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Pod explorer</h2>
            <span className="text-xs text-muted-foreground">{pods.length} pods</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th className="py-2 pr-3 font-medium">Pod</th>
                  <th className="py-2 pr-3 font-medium">Namespace</th>
                  <th className="py-2 pr-3 font-medium">Status</th>
                  <th className="py-2 pr-3 font-medium">Restarts</th>
                  <th className="py-2 pr-3 font-medium">Usage</th>
                  <th className="py-2 pr-3 font-medium">Node</th>
                  <th className="py-2 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {pods.map((pod) => (
                  <tr key={`${pod.namespace}/${pod.name}`} className="border-b border-border">
                    <td className="py-3 pr-3 font-medium">{pod.name}</td>
                    <td className="py-3 pr-3">{pod.namespace}</td>
                    <td className="py-3 pr-3">
                      <span className={statusClass(pod.status)}>{pod.status}</span>
                    </td>
                    <td className="py-3 pr-3">{pod.restarts}</td>
                    <td className="py-3 pr-3">
                      {pod.cpu_millicores}m / {pod.memory_mib}Mi
                    </td>
                    <td className="py-3 pr-3">{pod.node}</td>
                    <td className="py-3">
                      <Button
                        className="h-8 px-3"
                        type="button"
                        variant="secondary"
                        onClick={() => {
                          setSelectedPod(pod);
                          void analyzeCrashLoop(pod);
                        }}
                      >
                        Analyze
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <TriangleAlert className="h-5 w-5 text-destructive" aria-hidden />
            <h2 className="text-base font-semibold">CrashLoopBackOff analyzer</h2>
          </div>
          {analysis ? (
            <div className="grid gap-4">
              <div className="rounded-md border border-border bg-background p-3">
                <div className="font-medium">{analysis.pod.name}</div>
                <div className="mt-1 text-xs text-muted-foreground">
                  {analysis.pod.namespace} · {analysis.pod.restarts} restarts · {analysis.pod.reason}
                </div>
              </div>
              <InsightList title="Likely causes" items={analysis.likely_causes} />
              <InsightList title="Evidence" items={analysis.evidence} />
              <InsightList title="Remediation" items={analysis.remediation_steps} />
            </div>
          ) : (
            <div className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">
              Select a pod with restart pressure to generate an analysis.
            </div>
          )}
        </Card>
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" aria-hidden />
            <h2 className="text-base font-semibold">Resource recommendations</h2>
          </div>
          <div className="grid gap-3">
            {recommendations.map((item) => (
              <div key={`${item.namespace}/${item.target}`} className="rounded-md border border-border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-medium">{item.target}</div>
                  <div className="text-xs text-muted-foreground">{Math.round(item.confidence * 100)}%</div>
                </div>
                <p className="mt-2 text-sm">{item.recommendation}</p>
                <div className="mt-2 text-xs text-muted-foreground">
                  {item.current} {'->' } {item.suggested}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <BrainCircuit className="h-5 w-5 text-primary" aria-hidden />
            <h2 className="text-base font-semibold">YAML explanation</h2>
          </div>
          <form onSubmit={explainYaml} className="grid gap-3">
            <textarea
              value={yamlText}
              onChange={(event) => setYamlText(event.target.value)}
              className="min-h-72 rounded-md border border-border bg-background p-3 font-mono text-xs outline-none focus:ring-2 focus:ring-primary"
            />
            <Button disabled={!token} type="submit">
              <Play className="h-4 w-4" aria-hidden />
              Explain YAML
            </Button>
          </form>
          {yamlExplanation ? (
            <div className="mt-4 rounded-md border border-border bg-background p-3">
              <div className="text-sm font-medium">{yamlExplanation.summary}</div>
              <InsightList title="Risks" items={yamlExplanation.risks} />
              <InsightList title="Recommendations" items={yamlExplanation.recommendations} />
            </div>
          ) : null}
        </Card>
      </section>

      <section className="mt-4">
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <FileCode2 className="h-5 w-5 text-primary" aria-hidden />
            <h2 className="text-base font-semibold">Manifest generation</h2>
          </div>
          <form onSubmit={generateManifest} className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
            <input
              value={appName}
              onChange={(event) => setAppName(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="App name"
            />
            <input
              value={image}
              onChange={(event) => setImage(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Container image"
            />
            <Button disabled={!token} type="submit">
              Generate
            </Button>
          </form>
          {generated ? (
            <div className="mt-4 grid gap-3 xl:grid-cols-[1fr_340px]">
              <pre className="max-h-96 overflow-auto rounded-md border border-border bg-slate-950 p-4 text-xs text-white">
                {generated.yaml}
              </pre>
              <div className="rounded-md border border-border bg-background p-3">
                <InsightList title="Notes" items={generated.notes} />
              </div>
            </div>
          ) : null}
        </Card>
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
  icon: typeof Boxes;
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
      <div className="mt-3 truncate text-2xl font-semibold">{value}</div>
      <div className="mt-1 truncate text-xs text-muted-foreground">{detail}</div>
    </Card>
  );
}

function InsightList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="mt-3">
      <div className="text-xs font-medium uppercase text-muted-foreground">{title}</div>
      <div className="mt-2 grid gap-2">
        {items.map((item) => (
          <div key={item} className="rounded-md border border-border bg-white p-2 text-sm leading-6">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

function statusClass(status: string) {
  if (status === "Running") return "rounded-sm bg-emerald-50 px-2 py-1 text-xs text-emerald-700";
  if (status === "Pending") return "rounded-sm bg-amber-50 px-2 py-1 text-xs text-amber-700";
  return "rounded-sm bg-red-50 px-2 py-1 text-xs text-red-700";
}

