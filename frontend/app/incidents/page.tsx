"use client";

import { FormEvent, useState } from "react";
import { AlertTriangle, Bot, GitCommitVertical, ListChecks } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type Incident = {
  id: string;
  title: string;
  severity: string;
  status: string;
  summary: string | null;
  created_at: string;
};

type TimelineEvent = {
  id: string;
  event_type: string;
  title: string;
  description: string;
  occurred_at: string;
  evidence: Record<string, unknown>;
};

type Analysis = {
  incident: Incident;
  timeline: TimelineEvent[];
  suspected_root_cause: string;
  recommended_actions: string[];
  evidence_logs: Array<{
    id: string;
    service_name: string;
    level: string;
    message: string;
    timestamp: string;
    score: number | null;
  }>;
};

export default function IncidentsPage() {
  const [token, setToken] = useState("");
  const [title, setTitle] = useState("Checkout latency regression");
  const [query, setQuery] = useState("checkout timeout payment dependency latency deploy");
  const [serviceName, setServiceName] = useState("checkout-api");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(false);

  async function analyze(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await apiFetch<Analysis>("/incidents/analyze", {
        method: "POST",
        token,
        body: JSON.stringify({
          title,
          query,
          service_name: serviceName || null,
          severity: "sev2",
          limit: 12
        })
      });
      setAnalysis(response);
      const list = await apiFetch<Incident[]>("/incidents", { token });
      setIncidents(list);
    } finally {
      setLoading(false);
    }
  }

  async function loadIncidents() {
    const list = await apiFetch<Incident[]>("/incidents", { token });
    setIncidents(list);
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-normal">Incident Analyzer</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Reconstruct timelines from semantic log evidence and turn raw signals into triage steps.
        </p>
      </div>

      <section className="grid gap-4 xl:grid-cols-[0.85fr_1.15fr]">
        <Card className="p-5">
          <h2 className="text-base font-semibold">Analyze incident</h2>
          <form onSubmit={analyze} className="mt-4 grid gap-3">
            <input
              value={token}
              onChange={(event) => setToken(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Bearer token"
            />
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Incident title"
            />
            <input
              value={serviceName}
              onChange={(event) => setServiceName(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Service filter"
            />
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="min-h-28 rounded-md border border-border bg-background p-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="What should the analyzer investigate?"
            />
            <div className="flex gap-3">
              <Button disabled={!token || loading} type="submit">
                <Bot className="h-4 w-4" aria-hidden />
                Analyze
              </Button>
              <Button disabled={!token} type="button" variant="secondary" onClick={loadIncidents}>
                Load incidents
              </Button>
            </div>
          </form>

          <div className="mt-6">
            <h3 className="text-sm font-semibold">Recent incidents</h3>
            <div className="mt-3 grid gap-2">
              {incidents.map((incident) => (
                <div key={incident.id} className="rounded-md border border-border p-3 text-sm">
                  <div className="font-medium">{incident.title}</div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {incident.severity} · {incident.status} ·{" "}
                    {new Date(incident.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        <div className="grid gap-4">
          {analysis ? (
            <>
              <Card className="p-5">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="mt-1 h-5 w-5 text-destructive" aria-hidden />
                  <div>
                    <h2 className="text-base font-semibold">{analysis.incident.title}</h2>
                    <p className="mt-2 text-sm leading-6">{analysis.incident.summary}</p>
                    <div className="mt-3 rounded-md bg-muted p-3 text-sm">
                      Suspected root cause: {analysis.suspected_root_cause}
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="p-5">
                <div className="mb-5 flex items-center gap-2">
                  <GitCommitVertical className="h-5 w-5 text-primary" aria-hidden />
                  <h2 className="text-base font-semibold">Timeline</h2>
                </div>
                <div className="relative grid gap-4">
                  {analysis.timeline.map((event) => (
                    <div key={event.id} className="grid grid-cols-[120px_1fr] gap-4">
                      <time className="text-xs text-muted-foreground">
                        {new Date(event.occurred_at).toLocaleTimeString()}
                      </time>
                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="rounded-sm bg-muted px-2 py-1 text-xs">
                            {event.event_type}
                          </span>
                          <span className="text-sm font-medium">{event.title}</span>
                        </div>
                        <p className="mt-2 text-sm leading-6">{event.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-5">
                <div className="mb-4 flex items-center gap-2">
                  <ListChecks className="h-5 w-5 text-primary" aria-hidden />
                  <h2 className="text-base font-semibold">Recommended actions</h2>
                </div>
                <div className="grid gap-2">
                  {analysis.recommended_actions.map((action) => (
                    <div key={action} className="rounded-md border border-border p-3 text-sm">
                      {action}
                    </div>
                  ))}
                </div>
              </Card>
            </>
          ) : (
            <Card className="p-5 text-sm text-muted-foreground">
              Run an analysis after ingesting logs to build an incident timeline.
            </Card>
          )}
        </div>
      </section>
    </AppShell>
  );
}

