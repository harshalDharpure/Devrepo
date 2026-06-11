"use client";

import { useCallback, useRef, useState } from "react";
import { Bot, Zap } from "lucide-react";
import { AgentTimeline } from "@/components/agent-timeline";
import { IdeaInput } from "@/components/idea-input";
import { ReportView } from "@/components/report-view";
import { WorkflowGraph } from "@/components/workflow-graph";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { AgentEvent, AgentName, AgentStatus, ValidationReport } from "@/lib/types";
import { API_URL } from "@/lib/utils";

const INITIAL_STATES: Record<string, AgentStatus> = {
  front_desk: "pending",
  market_research: "pending",
  competitor_analysis: "pending",
  legal: "pending",
  scoring: "pending",
  report: "pending",
};

export function Dashboard() {
  const [phase, setPhase] = useState<"input" | "running" | "report">("input");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [agentStates, setAgentStates] = useState<Record<string, AgentStatus>>(INITIAL_STATES);
  const [activeAgent, setActiveAgent] = useState<AgentName | undefined>();
  const [progress, setProgress] = useState(0);
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [statusMessage, setStatusMessage] = useState("");
  const eventSourceRef = useRef<EventSource | null>(null);

  const reset = () => {
    eventSourceRef.current?.close();
    setPhase("input");
    setEvents([]);
    setAgentStates(INITIAL_STATES);
    setActiveAgent(undefined);
    setProgress(0);
    setReport(null);
    setStatusMessage("");
  };

  const connectStream = useCallback((sessionId: string) => {
    eventSourceRef.current?.close();
    const es = new EventSource(`${API_URL}/api/validation/${sessionId}/stream`);
    eventSourceRef.current = es;

    es.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);

        if (data.type === "session_complete") {
          es.close();
          if (data.status === "completed") {
            fetch(`${API_URL}/api/reports/${sessionId}`)
              .then((r) => r.json())
              .then((reportData: ValidationReport) => {
                setReport(reportData);
                setPhase("report");
              });
          } else if (data.status === "needs_clarification") {
            setStatusMessage("Clarification needed — please provide more details");
          }
          return;
        }

        const event = data as AgentEvent;
        setEvents((prev) => [...prev, event]);
        setAgentStates((prev) => ({ ...prev, [event.agent]: event.status }));
        if (event.status === "running") setActiveAgent(event.agent);
        setProgress((prev) => Math.max(prev, event.progress));

        const labels: Record<string, string> = {
          market_research: "Market Agent researching…",
          competitor_analysis: "Competitor Agent analyzing landscape…",
          legal: "Legal Agent checking regulations…",
          scoring: "Scoring Engine computing metrics…",
          report: "Report Generator assembling final report…",
          front_desk: "Front Desk Agent validating idea…",
        };
        if (event.status === "running" && labels[event.agent]) {
          setStatusMessage(labels[event.agent]);
        }
      } catch {
        /* ignore parse errors */
      }
    };

    es.onerror = () => es.close();
  }, []);

  const startValidation = async (idea: string) => {
    reset();
    setPhase("running");

    const res = await fetch(`${API_URL}/api/validation/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: idea, clarifications: {} }),
    });
    const data = await res.json();
    connectStream(data.session_id);
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-border/50 glass sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">VenturePilot AI</h1>
              <p className="text-xs text-muted-foreground">Startup Intelligence Operating System</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Zap className="h-3 w-3 text-indigo-400" />
            Powered by Google ADK + Gemini 2.5 Pro
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {phase === "input" && <IdeaInput onSubmit={startValidation} />}

        {phase === "running" && (
          <div className="space-y-6">
            <Card className="border-indigo-500/30">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-indigo-400 animate-pulse">
                    {statusMessage || "Initializing validation pipeline…"}
                  </span>
                  <span className="text-sm text-muted-foreground">{progress.toFixed(0)}%</span>
                </div>
                <Progress value={progress} />
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Agent Workflow</CardTitle>
                </CardHeader>
                <CardContent>
                  <WorkflowGraph agentStates={agentStates} activeAgent={activeAgent} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Live Agent Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <AgentTimeline events={events} agentStates={agentStates} />
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {phase === "report" && report && (
          <>
            <ReportView report={report} />
            <div className="text-center">
              <button onClick={reset} className="text-sm text-indigo-400 hover:underline">
                Validate another idea →
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
