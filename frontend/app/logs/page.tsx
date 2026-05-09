"use client";

import { FormEvent, useState } from "react";
import { DatabaseZap, Plus, Search } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type LogEntry = {
  id: string;
  service_name: string;
  environment: string;
  level: string;
  message: string;
  trace_id: string | null;
  timestamp: string;
  labels: Record<string, unknown>;
  score: number | null;
};

export default function LogsPage() {
  const [token, setToken] = useState("");
  const [query, setQuery] = useState("checkout timeout payment dependency");
  const [serviceName, setServiceName] = useState("checkout-api");
  const [level, setLevel] = useState("");
  const [message, setMessage] = useState(
    "checkout-api request timed out while calling payment-service after deploy v42"
  );
  const [results, setResults] = useState<LogEntry[]>([]);
  const [semantic, setSemantic] = useState(false);
  const [status, setStatus] = useState("");

  async function ingest(event: FormEvent) {
    event.preventDefault();
    setStatus("Indexing log event");
    await apiFetch<LogEntry>("/logs/ingest", {
      method: "POST",
      token,
      body: JSON.stringify({
        service_name: serviceName,
        environment: "production",
        level: level || "ERROR",
        message,
        trace_id: "trace-phase2-demo",
        labels: { source: "manual", phase: "2" }
      })
    });
    setStatus("Log event stored and indexed");
  }

  async function searchLogs(event: FormEvent) {
    event.preventDefault();
    setStatus("Searching logs");
    const response = await apiFetch<{ semantic: boolean; results: LogEntry[] }>("/logs/search", {
      method: "POST",
      token,
      body: JSON.stringify({
        query,
        service_name: serviceName || null,
        level: level || null,
        limit: 12
      })
    });
    setSemantic(response.semantic);
    setResults(response.results);
    setStatus(response.semantic ? "Semantic search via ChromaDB" : "Keyword fallback search");
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Log Intelligence</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Ingest logs, index them in ChromaDB, and search operational evidence semantically.
          </p>
        </div>
        {status ? (
          <div className="rounded-md border border-border bg-white px-3 py-2 text-sm">{status}</div>
        ) : null}
      </div>

      <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-5">
          <h2 className="text-base font-semibold">Ingest log</h2>
          <form onSubmit={ingest} className="mt-4 grid gap-3">
            <input
              value={token}
              onChange={(event) => setToken(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Bearer token"
            />
            <div className="grid gap-3 md:grid-cols-2">
              <input
                value={serviceName}
                onChange={(event) => setServiceName(event.target.value)}
                className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
                placeholder="Service"
              />
              <input
                value={level}
                onChange={(event) => setLevel(event.target.value)}
                className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
                placeholder="Level"
              />
            </div>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              className="min-h-32 rounded-md border border-border bg-background p-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Log message"
            />
            <Button disabled={!token || !message} type="submit">
              <Plus className="h-4 w-4" aria-hidden />
              Ingest
            </Button>
          </form>
        </Card>

        <Card className="p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Semantic search</h2>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <DatabaseZap className="h-4 w-4" aria-hidden />
              {semantic ? "ChromaDB" : "Fallback"}
            </div>
          </div>
          <form onSubmit={searchLogs} className="mt-4 flex gap-3">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="h-10 flex-1 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Search logs by meaning"
            />
            <Button disabled={!token || !query} type="submit">
              <Search className="h-4 w-4" aria-hidden />
              Search
            </Button>
          </form>
          <div className="mt-5 grid gap-3">
            {results.map((log) => (
              <div key={log.id} className="rounded-md border border-border bg-background p-3">
                <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  <span className="font-medium text-foreground">{log.level}</span>
                  <span>{log.service_name}</span>
                  <span>{new Date(log.timestamp).toLocaleString()}</span>
                  {log.score ? <span>score {log.score}</span> : null}
                </div>
                <p className="mt-2 text-sm leading-6">{log.message}</p>
                {log.trace_id ? (
                  <div className="mt-2 text-xs text-muted-foreground">trace {log.trace_id}</div>
                ) : null}
              </div>
            ))}
          </div>
        </Card>
      </section>
    </AppShell>
  );
}

