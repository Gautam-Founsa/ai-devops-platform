"use client";

import { FormEvent, useState } from "react";
import { Bot, Send, UserRound } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatPage() {
  const [token, setToken] = useState("");
  const [input, setInput] = useState("Why is checkout latency high?");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Ask about metrics, incidents, deployments, Kubernetes health, or infrastructure changes."
    }
  ]);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!input.trim()) return;
    const question = input.trim();
    setMessages((current) => [...current, { role: "user", content: question }]);
    setInput("");
    setLoading(true);
    try {
      const response = await apiFetch<{ answer: string }>("/chat", {
        method: "POST",
        token,
        body: JSON.stringify({ message: question })
      });
      setMessages((current) => [...current, { role: "assistant", content: response.answer }]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: "assistant", content: error instanceof Error ? error.message : "Request failed" }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-normal">AI Chat Copilot</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Natural language triage for telemetry, incidents, deployments, and infrastructure context.
        </p>
      </div>
      <Card className="grid min-h-[680px] grid-rows-[auto_1fr_auto] overflow-hidden">
        <div className="border-b border-border p-4">
          <label className="text-xs font-medium text-muted-foreground" htmlFor="token">
            Bearer token
          </label>
          <input
            id="token"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            placeholder="Paste token from /login"
          />
        </div>
        <div className="space-y-4 overflow-y-auto p-4">
          {messages.map((message, index) => {
            const Icon = message.role === "assistant" ? Bot : UserRound;
            return (
              <div key={`${message.role}-${index}`} className="flex gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted">
                  <Icon className="h-4 w-4" aria-hidden />
                </div>
                <div className="max-w-3xl rounded-md border border-border bg-background p-3 text-sm leading-6">
                  {message.content}
                </div>
              </div>
            );
          })}
        </div>
        <form onSubmit={submit} className="flex gap-3 border-t border-border p-4">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            className="h-11 flex-1 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            placeholder="Ask what changed, what is failing, or what to do next"
          />
          <Button disabled={loading || !token} type="submit">
            <Send className="h-4 w-4" aria-hidden />
            Send
          </Button>
        </form>
      </Card>
    </AppShell>
  );
}

