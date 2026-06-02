import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VenturePilot AI — Startup Intelligence OS",
  description: "Autonomous multi-agent startup validation powered by Google ADK + Gemini",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
