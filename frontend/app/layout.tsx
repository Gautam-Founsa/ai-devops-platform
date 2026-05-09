import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI DevOps Platform",
  description: "Autonomous AI infrastructure assistant for SRE and DevOps teams"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

