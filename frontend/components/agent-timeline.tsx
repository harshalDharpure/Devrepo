"use client";

import { motion } from "framer-motion";
import { AGENT_META, type AgentEvent, type AgentName, type AgentStatus } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";

interface AgentTimelineProps {
  events: AgentEvent[];
  agentStates: Record<string, AgentStatus>;
}

const STATUS_COLORS: Record<AgentStatus, string> = {
  pending: "bg-muted-foreground/30",
  running: "bg-indigo-500 animate-pulse",
  completed: "bg-emerald-500",
  failed: "bg-red-500",
  skipped: "bg-yellow-500",
};

export function AgentTimeline({ events, agentStates }: AgentTimelineProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-4 gap-2">
        {(Object.keys(AGENT_META) as AgentName[]).map((agent) => {
          const meta = AGENT_META[agent];
          const status = agentStates[agent] || "pending";
          return (
            <motion.div
              key={agent}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className={cn(
                "flex flex-col items-center gap-1 p-2 rounded-lg border transition-all",
                status === "running" && "border-indigo-500/50 bg-indigo-500/10 animate-pulse-glow",
                status === "completed" && "border-emerald-500/30 bg-emerald-500/5",
                status === "pending" && "border-border/30 opacity-50"
              )}
            >
              <span className="text-lg">{meta.icon}</span>
              <span className="text-[10px] text-center font-medium leading-tight">{meta.label}</span>
              <div className={cn("h-1.5 w-1.5 rounded-full", STATUS_COLORS[status])} />
            </motion.div>
          );
        })}
      </div>

      <ScrollArea className="h-[280px] rounded-lg border border-border/50 bg-secondary/30 p-3">
        <div className="space-y-2">
          {events.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-8">
              Agent logs will appear here during validation...
            </p>
          )}
          {events.map((event, i) => {
            const meta = AGENT_META[event.agent];
            return (
              <motion.div
                key={`${event.timestamp}-${i}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-start gap-2 text-xs font-mono"
              >
                <span className="text-muted-foreground shrink-0">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
                <span>{meta.icon}</span>
                <span className={cn(
                  "font-semibold shrink-0",
                  event.status === "running" && "text-indigo-400",
                  event.status === "completed" && "text-emerald-400",
                  event.status === "failed" && "text-red-400"
                )}>
                  [{meta.label}]
                </span>
                <span className="text-foreground/80">{event.message}</span>
              </motion.div>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
