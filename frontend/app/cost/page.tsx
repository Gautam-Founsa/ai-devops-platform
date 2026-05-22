"use client";

import { useState } from "react";
import {
  ArrowDownRight,
  CircleDollarSign,
  CloudOff,
  Gauge,
  RefreshCw,
  Scale,
  WalletCards
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type Breakdown = {
  service: string;
  category: string;
  monthly_cost: number;
  change_percent: number;
  owner: string;
};

type TrendPoint = {
  date: string;
  amount: number;
};

type CostSummary = {
  currency: string;
  month_to_date: number;
  forecast_monthly: number;
  previous_month: number;
  potential_savings: number;
  idle_spend: number;
  rightsizing_savings: number;
  breakdown: Breakdown[];
  trend: TrendPoint[];
};

type Recommendation = {
  id: string;
  category: string;
  priority: string;
  resource: string;
  service: string;
  current_monthly_cost: number;
  estimated_monthly_savings: number;
  title: string;
  rationale: string;
  action: string;
  confidence: number;
};

export default function CostPage() {
  const [token, setToken] = useState("");
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [status, setStatus] = useState("");

  async function loadCostAdvisor() {
    setStatus("Loading cost intelligence");
    const [summaryResponse, recommendationResponse] = await Promise.all([
      apiFetch<CostSummary>("/cost/summary", { token }),
      apiFetch<Recommendation[]>("/cost/recommendations", { token })
    ]);
    setSummary(summaryResponse);
    setRecommendations(recommendationResponse);
    setStatus("Cost advisor ready");
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Cost Optimization Advisor</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Find rightsizing opportunities, idle resources, and the spend drivers worth acting on first.
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
          <Button disabled={!token} type="button" onClick={loadCostAdvisor}>
            <RefreshCw className="h-4 w-4" aria-hidden />
            Load cost advisor
          </Button>
        </div>
      </Card>

      <section className="grid gap-4 xl:grid-cols-4">
        <MetricCard
          icon={WalletCards}
          label="Month to date"
          value={money(summary?.month_to_date, summary?.currency)}
          detail="current spend"
        />
        <MetricCard
          icon={Gauge}
          label="Monthly forecast"
          value={money(summary?.forecast_monthly, summary?.currency)}
          detail={
            summary
              ? `${percent((summary.forecast_monthly - summary.previous_month) / summary.previous_month)} vs previous`
              : "projected"
          }
        />
        <MetricCard
          icon={ArrowDownRight}
          label="Savings found"
          value={money(summary?.potential_savings, summary?.currency)}
          detail="monthly potential"
        />
        <MetricCard
          icon={CloudOff}
          label="Idle spend"
          value={money(summary?.idle_spend, summary?.currency)}
          detail="resources to stop or prune"
        />
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="h-[380px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Daily spend trend</h2>
            <span className="text-xs text-muted-foreground">Month to date</span>
          </div>
          <ResponsiveContainer width="100%" height="85%">
            <AreaChart data={summary?.trend ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => money(Number(value), summary?.currency)} />
              <Area dataKey="amount" stroke="#0f766e" fill="#99f6e4" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        <Card className="h-[380px] p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Cost breakdown</h2>
            <span className="text-xs text-muted-foreground">{summary?.breakdown.length ?? 0} spend groups</span>
          </div>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={summary?.breakdown ?? []} layout="vertical" margin={{ left: 18 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="service" type="category" width={126} />
              <Tooltip formatter={(value) => money(Number(value), summary?.currency)} />
              <Bar dataKey="monthly_cost" fill="#0f766e" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </section>

      <section className="mt-4 grid gap-4 xl:grid-cols-[1fr_360px]">
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <CircleDollarSign className="h-5 w-5 text-primary" aria-hidden />
            <h2 className="text-base font-semibold">Recommendations</h2>
          </div>
          <div className="grid gap-3">
            {recommendations.length ? (
              recommendations.map((item) => <RecommendationCard key={item.id} item={item} currency={summary?.currency} />)
            ) : (
              <div className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">
                Load cost intelligence to review optimization opportunities.
              </div>
            )}
          </div>
        </Card>

        <div className="grid gap-4">
          <Card className="p-5">
            <div className="mb-4 flex items-center gap-2">
              <Scale className="h-5 w-5 text-primary" aria-hidden />
              <h2 className="text-base font-semibold">Rightsizing</h2>
            </div>
            <div className="text-3xl font-semibold">
              {money(summary?.rightsizing_savings, summary?.currency)}
            </div>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Savings from request, retention, and capacity tuning without removing required services.
            </p>
          </Card>

          <Card className="p-5">
            <h2 className="text-base font-semibold">Spend groups</h2>
            <div className="mt-4 grid gap-2">
              {(summary?.breakdown ?? []).map((item) => (
                <div key={item.service} className="rounded-md border border-border bg-background p-3">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="font-medium">{item.service}</span>
                    <span>{money(item.monthly_cost, summary?.currency)}</span>
                  </div>
                  <div className="mt-1 flex items-center justify-between gap-3 text-xs text-muted-foreground">
                    <span>{item.owner}</span>
                    <span>{item.change_percent > 0 ? "+" : ""}{item.change_percent}%</span>
                  </div>
                </div>
              ))}
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
  icon: typeof WalletCards;
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

function RecommendationCard({
  item,
  currency
}: {
  item: Recommendation;
  currency: string | undefined;
}) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-sm bg-muted px-2 py-1 text-xs">{item.category}</span>
            <span className="rounded-sm bg-muted px-2 py-1 text-xs">{item.priority}</span>
          </div>
          <h3 className="mt-3 text-sm font-semibold">{item.title}</h3>
          <p className="mt-1 text-xs text-muted-foreground">{item.service} / {item.resource}</p>
        </div>
        <div className="text-right">
          <div className="text-xl font-semibold text-primary">
            {money(item.estimated_monthly_savings, currency)}
          </div>
          <div className="text-xs text-muted-foreground">monthly savings</div>
        </div>
      </div>
      <p className="mt-3 text-sm leading-6">{item.rationale}</p>
      <div className="mt-3 rounded-md border border-border bg-white p-3 text-sm leading-6">{item.action}</div>
      <div className="mt-2 text-xs text-muted-foreground">
        {Math.round(item.confidence * 100)}% confidence from utilization and activity signals
      </div>
    </div>
  );
}

function money(value: number | undefined, currency = "USD") {
  if (value === undefined) return "-";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 0
  }).format(value);
}

function percent(value: number) {
  return `${value >= 0 ? "+" : ""}${Math.round(value * 100)}%`;
}

