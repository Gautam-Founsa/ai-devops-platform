"use client";

import { FormEvent, useState } from "react";
import { LogIn } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch, type AuthResponse } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    const response = await apiFetch<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    setToken(response.access_token);
  }

  return (
    <main className="grid min-h-screen place-items-center bg-background p-4">
      <Card className="w-full max-w-md p-6">
        <h1 className="text-xl font-semibold">Sign in</h1>
        <p className="mt-1 text-sm text-muted-foreground">Use your platform account to continue.</p>
        <form onSubmit={submit} className="mt-6 grid gap-4">
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            type="email"
            placeholder="Email"
          />
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            type="password"
            placeholder="Password"
          />
          <Button type="submit">
            <LogIn className="h-4 w-4" aria-hidden />
            Sign in
          </Button>
        </form>
        {token ? (
          <textarea
            readOnly
            className="mt-4 h-28 w-full rounded-md border border-border bg-muted p-3 text-xs"
            value={token}
          />
        ) : null}
      </Card>
    </main>
  );
}

