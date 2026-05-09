"use client";

import { FormEvent, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type MetricPoint = { timestamp: string; value: number };

export default function MetricsPage() {
  const [token, setToken] = useState("");
  const [query, setQuery] = useState("rate(http_requests_total[5m])");
  const [series, setSeries] = useState<MetricPoint[]>([]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const data = await apiFetch<{ series: MetricPoint[] }>(
      `/metrics/query?query=${encodeURIComponent(query)}`,
      { token }
    );
    setSeries(data.series);
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-normal">Metrics Explorer</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Query operational signals through the backend metrics service and Prometheus surface.
        </p>
      </div>
      <Card className="p-5">
        <form onSubmit={submit} className="grid gap-3 md:grid-cols-[1fr_2fr_auto]">
          <input
            value={token}
            onChange={(event) => setToken(event.target.value)}
            className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            placeholder="Bearer token"
          />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            placeholder="PromQL query"
          />
          <Button disabled={!token} type="submit">
            Run query
          </Button>
        </form>
        <div className="mt-6 h-96">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={series}>
              <XAxis dataKey="timestamp" tickFormatter={(value) => value.slice(11, 16)} />
              <YAxis />
              <Tooltip />
              <Line dataKey="value" stroke="#0f766e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </AppShell>
  );
}

