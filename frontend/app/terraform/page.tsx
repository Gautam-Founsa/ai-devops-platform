"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  FileCode2,
  LockKeyhole,
  Play,
  ServerCog,
  ShieldAlert,
  Sparkles,
  TriangleAlert
} from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type Template = {
  id: string;
  name: string;
  description: string;
  resources: string[];
};

type Finding = {
  severity: string;
  code: string;
  message: string;
  recommendation: string;
};

type GenerateResponse = {
  template: string;
  files: Record<string, string>;
  explanation: string;
  security_best_practices: string[];
  validation: Finding[];
};

type ValidateResponse = {
  valid: boolean;
  findings: Finding[];
};

export default function TerraformPage() {
  const [token, setToken] = useState("");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [template, setTemplate] = useState("ecs-rds-alb");
  const [prompt, setPrompt] = useState(
    "Create a production AWS ECS Fargate service for checkout-api with an ALB, private PostgreSQL RDS, encrypted storage, logs, and least-privilege security groups."
  );
  const [appName, setAppName] = useState("checkout-api");
  const [region, setRegion] = useState("us-east-1");
  const [image, setImage] = useState("ghcr.io/acme/checkout-api:v42");
  const [generated, setGenerated] = useState<GenerateResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState("main.tf");
  const [validation, setValidation] = useState<ValidateResponse | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (!token) return;
    apiFetch<Template[]>("/terraform/templates", { token })
      .then(setTemplates)
      .catch((error) => setStatus(error instanceof Error ? error.message : "Failed to load templates"));
  }, [token]);

  const fileNames = useMemo(() => Object.keys(generated?.files ?? {}), [generated]);
  const selectedContent = generated?.files[selectedFile] ?? "";

  async function generate(event: FormEvent) {
    event.preventDefault();
    setStatus("Generating Terraform");
    const response = await apiFetch<GenerateResponse>("/terraform/generate", {
      method: "POST",
      token,
      body: JSON.stringify({
        prompt,
        template,
        app_name: appName,
        region,
        environment: "prod",
        container_image: image
      })
    });
    setGenerated(response);
    const firstFile = Object.keys(response.files)[0] ?? "versions.tf";
    setSelectedFile(firstFile);
    setValidation({ valid: response.validation.length === 0, findings: response.validation });
    setStatus("Terraform generated");
  }

  async function validate() {
    if (!generated) return;
    setStatus("Validating Terraform");
    const response = await apiFetch<ValidateResponse>("/terraform/validate", {
      method: "POST",
      token,
      body: JSON.stringify({ files: generated.files })
    });
    setValidation(response);
    setStatus(response.valid ? "Validation passed" : "Validation found issues");
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Terraform Generator</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Convert infrastructure intent into AWS ECS, RDS, and ALB Terraform with validation and security guidance.
          </p>
        </div>
        {status ? (
          <div className="rounded-md border border-border bg-white px-3 py-2 text-sm">{status}</div>
        ) : null}
      </div>

      <section className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" aria-hidden />
            <h2 className="text-base font-semibold">Natural language to Terraform</h2>
          </div>
          <form onSubmit={generate} className="grid gap-3">
            <input
              value={token}
              onChange={(event) => setToken(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Bearer token"
            />
            <div className="grid gap-3 md:grid-cols-2">
              <input
                value={appName}
                onChange={(event) => setAppName(event.target.value)}
                className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
                placeholder="Application name"
              />
              <input
                value={region}
                onChange={(event) => setRegion(event.target.value)}
                className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
                placeholder="AWS region"
              />
            </div>
            <input
              value={image}
              onChange={(event) => setImage(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
              placeholder="Container image"
            />
            <select
              value={template}
              onChange={(event) => setTemplate(event.target.value)}
              className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="ecs-rds-alb">ECS + RDS + ALB</option>
              <option value="ecs">ECS Fargate</option>
              <option value="rds">RDS PostgreSQL</option>
              <option value="alb">Application Load Balancer</option>
            </select>
            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              className="min-h-40 rounded-md border border-border bg-background p-3 text-sm leading-6 outline-none focus:ring-2 focus:ring-primary"
              placeholder="Describe the infrastructure you want"
            />
            <Button disabled={!token || !prompt} type="submit">
              <Play className="h-4 w-4" aria-hidden />
              Generate Terraform
            </Button>
          </form>

          <div className="mt-6">
            <h3 className="text-sm font-semibold">AWS templates</h3>
            <div className="mt-3 grid gap-3">
              {(templates.length ? templates : fallbackTemplates).map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setTemplate(item.id)}
                  className={`rounded-md border p-3 text-left transition ${
                    template === item.id ? "border-primary bg-emerald-50" : "border-border bg-background"
                  }`}
                >
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <ServerCog className="h-4 w-4" aria-hidden />
                    {item.name}
                  </div>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">{item.description}</p>
                </button>
              ))}
            </div>
          </div>
        </Card>

        <div className="grid gap-4">
          <Card className="p-5">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <FileCode2 className="h-5 w-5 text-primary" aria-hidden />
                <h2 className="text-base font-semibold">Generated files</h2>
              </div>
              <Button disabled={!generated} type="button" variant="secondary" onClick={validate}>
                Validate
              </Button>
            </div>
            {generated ? (
              <>
                <p className="mb-4 rounded-md border border-border bg-background p-3 text-sm leading-6">
                  {generated.explanation}
                </p>
                <div className="mb-3 flex flex-wrap gap-2">
                  {fileNames.map((fileName) => (
                    <button
                      key={fileName}
                      type="button"
                      onClick={() => setSelectedFile(fileName)}
                      className={`rounded-md border px-3 py-2 text-xs ${
                        selectedFile === fileName ? "border-primary bg-emerald-50" : "border-border bg-white"
                      }`}
                    >
                      {fileName}
                    </button>
                  ))}
                </div>
                <pre className="max-h-[520px] overflow-auto rounded-md border border-border bg-slate-950 p-4 text-xs leading-5 text-white">
                  {selectedContent}
                </pre>
              </>
            ) : (
              <div className="rounded-md border border-border bg-background p-4 text-sm text-muted-foreground">
                Generate Terraform to inspect multi-file HCL output.
              </div>
            )}
          </Card>

          <section className="grid gap-4 lg:grid-cols-2">
            <Card className="p-5">
              <div className="mb-4 flex items-center gap-2">
                {validation?.valid ? (
                  <CheckCircle2 className="h-5 w-5 text-emerald-600" aria-hidden />
                ) : (
                  <TriangleAlert className="h-5 w-5 text-amber-600" aria-hidden />
                )}
                <h2 className="text-base font-semibold">Validation</h2>
              </div>
              {validation ? (
                validation.findings.length ? (
                  <div className="grid gap-3">
                    {validation.findings.map((finding) => (
                      <FindingCard key={finding.code} finding={finding} />
                    ))}
                  </div>
                ) : (
                  <div className="rounded-md border border-border bg-emerald-50 p-3 text-sm text-emerald-800">
                    No high-confidence validation findings.
                  </div>
                )
              ) : (
                <div className="text-sm text-muted-foreground">Validation runs after generation.</div>
              )}
            </Card>

            <Card className="p-5">
              <div className="mb-4 flex items-center gap-2">
                <LockKeyhole className="h-5 w-5 text-primary" aria-hidden />
                <h2 className="text-base font-semibold">Security best practices</h2>
              </div>
              <div className="grid gap-2">
                {(generated?.security_best_practices ?? defaultPractices).map((practice) => (
                  <div key={practice} className="rounded-md border border-border bg-background p-3 text-sm leading-6">
                    {practice}
                  </div>
                ))}
              </div>
            </Card>
          </section>
        </div>
      </section>
    </AppShell>
  );
}

function FindingCard({ finding }: { finding: Finding }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <ShieldAlert className="h-4 w-4 text-destructive" aria-hidden />
          {finding.code}
        </div>
        <span className="rounded-sm bg-muted px-2 py-1 text-xs">{finding.severity}</span>
      </div>
      <p className="mt-2 text-sm leading-6">{finding.message}</p>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{finding.recommendation}</p>
    </div>
  );
}

const fallbackTemplates: Template[] = [
  {
    id: "ecs-rds-alb",
    name: "ECS + RDS + ALB",
    description: "Production web service baseline combining ECS Fargate, RDS PostgreSQL, and ALB.",
    resources: ["aws_ecs_service", "aws_db_instance", "aws_lb"]
  },
  {
    id: "ecs",
    name: "AWS ECS Fargate",
    description: "Container service with task definition, logs, IAM, and private networking.",
    resources: ["aws_ecs_service"]
  },
  {
    id: "rds",
    name: "AWS RDS PostgreSQL",
    description: "Encrypted private PostgreSQL database with subnet and security group controls.",
    resources: ["aws_db_instance"]
  },
  {
    id: "alb",
    name: "AWS Application Load Balancer",
    description: "Public ALB, target group, listener, and health checks.",
    resources: ["aws_lb"]
  }
];

const defaultPractices = [
  "Keep Terraform state in an encrypted remote backend with locking.",
  "Pin provider versions and review plans before apply.",
  "Avoid public database ingress and prefer private subnets for application/data tiers.",
  "Tag resources with environment, owner, and cost-center metadata."
];

