"use client";

import { Activity, AlertTriangle, CheckCircle2, Clock3 } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";

const latency = [
  { time: "09:00", value: 142 },
  { time: "10:00", value: 138 },
  { time: "11:00", value: 165 },
  { time: "12:00", value: 221 },
  { time: "13:00", value: 188 },
  { time: "14:00", value: 172 }
];

const stats = [
  { label: "Healthy services", value: "24", icon: CheckCircle2 },
  { label: "Open incidents", value: "3", icon: AlertTriangle },
  { label: "P95 latency", value: "172 ms", icon: Activity },
  { label: "Deploys today", value: "11", icon: Clock3 }
];

export default function DashboardPage() {
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-normal">Operations Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Live command surface for incidents, deployments, metrics, and AI-assisted triage.
        </p>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{stat.label}</span>
                <Icon className="h-4 w-4 text-primary" aria-hidden />
              </div>
              <div className="mt-3 text-3xl font-semibold">{stat.value}</div>
            </Card>
          );
        })}
      </section>

      <section className="mt-6 grid gap-4 xl:grid-cols-[1.5fr_1fr]">
        <Card className="h-96 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">API latency</h2>
            <span className="text-xs text-muted-foreground">P95, last 6 hours</span>
          </div>
          <ResponsiveContainer width="100%" height="85%">
            <AreaChart data={latency}>
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area dataKey="value" stroke="#0f766e" fill="#99f6e4" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
        <Card className="p-5">
          <h2 className="text-base font-semibold">Active AI findings</h2>
          <div className="mt-4 grid gap-3">
            {["checkout latency rose after deploy v42", "redis memory fragmentation above baseline", "api-gateway error budget burn increasing"].map(
              (finding) => (
                <div key={finding} className="rounded-md border border-border p-3 text-sm">
                  {finding}
                </div>
              )
            )}
          </div>
        </Card>
      </section>
    </AppShell>
  );
}
