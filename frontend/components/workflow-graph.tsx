"use client";

import { motion } from "framer-motion";
import { AGENT_META, type AgentName, type AgentStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

interface WorkflowGraphProps {
  agentStates: Record<string, AgentStatus>;
  activeAgent?: AgentName;
}

const NODES: { id: AgentName; x: number; y: number }[] = [
  { id: "front_desk", x: 50, y: 10 },
  { id: "orchestrator", x: 50, y: 28 },
  { id: "market_research", x: 15, y: 52 },
  { id: "competitor_analysis", x: 50, y: 52 },
  { id: "legal", x: 85, y: 52 },
  { id: "debate", x: 50, y: 72 },
  { id: "scoring", x: 50, y: 86 },
  { id: "report", x: 50, y: 96 },
];

const EDGES: [AgentName, AgentName][] = [
  ["front_desk", "orchestrator"],
  ["orchestrator", "market_research"],
  ["orchestrator", "competitor_analysis"],
  ["orchestrator", "legal"],
  ["market_research", "debate"],
  ["competitor_analysis", "debate"],
  ["legal", "debate"],
  ["debate", "scoring"],
  ["scoring", "report"],
];

export function WorkflowGraph({ agentStates, activeAgent }: WorkflowGraphProps) {
  return (
    <div className="relative w-full aspect-[2/1] min-h-[200px]">
      <svg viewBox="0 0 100 100" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.6" />
          </linearGradient>
        </defs>

        {EDGES.map(([from, to]) => {
          const fromNode = NODES.find((n) => n.id === from)!;
          const toNode = NODES.find((n) => n.id === to)!;
          const isActive =
            agentStates[from] === "completed" && agentStates[to] === "running";

          return (
            <line
              key={`${from}-${to}`}
              x1={fromNode.x}
              y1={fromNode.y + 3}
              x2={toNode.x}
              y2={toNode.y - 3}
              stroke={isActive ? "#818cf8" : "url(#edgeGrad)"}
              strokeWidth={isActive ? 0.6 : 0.3}
              strokeDasharray={isActive ? "2 1" : undefined}
              className={isActive ? "animate-flow" : undefined}
            />
          );
        })}

        {NODES.map((node) => {
          const status = agentStates[node.id] || "pending";
          const meta = AGENT_META[node.id];
          const isActive = activeAgent === node.id || status === "running";

          return (
            <g key={node.id}>
              <motion.circle
                cx={node.x}
                cy={node.y}
                r={isActive ? 4.5 : 3.5}
                fill={status === "completed" ? "#10b981" : status === "running" ? meta.color : "#1e293b"}
                stroke={isActive ? meta.color : "#334155"}
                strokeWidth={0.5}
                animate={isActive ? { scale: [1, 1.15, 1] } : {}}
                transition={{ repeat: Infinity, duration: 2 }}
              />
              <text
                x={node.x}
                y={node.y + 0.8}
                textAnchor="middle"
                fontSize="2.5"
                fill="white"
              >
                {meta.icon}
              </text>
              <text
                x={node.x}
                y={node.y + 7}
                textAnchor="middle"
                fontSize="2"
                fill="#94a3b8"
              >
                {meta.label.split(" ")[0]}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
