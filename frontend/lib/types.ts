export type AgentName =
  | "front_desk"
  | "orchestrator"
  | "market_research"
  | "competitor_analysis"
  | "legal"
  | "debate"
  | "scoring"
  | "report";

export type AgentStatus = "pending" | "running" | "completed" | "failed" | "skipped";

export interface AgentEvent {
  session_id: string;
  agent: AgentName;
  status: AgentStatus;
  message: string;
  timestamp: string;
  progress: number;
  metadata?: Record<string, unknown>;
}

export interface ValidationScores {
  validation_score: number;
  market_opportunity_score: number;
  competition_score: number;
  risk_score: number;
  investor_attractiveness_score: number;
  overall_grade: string;
}

export interface LeanCanvas {
  problem: string;
  solution: string;
  unique_value_proposition: string;
  unfair_advantage: string;
  customer_segments: string;
  key_metrics: string;
  channels: string;
  cost_structure: string;
  revenue_streams: string;
}

export interface EvidenceCitation {
  source: string;
  title: string;
  snippet: string;
  url?: string;
  relevance_score: number;
}

export interface ValidationReport {
  session_id: string;
  idea_summary: string;
  executive_summary: string;
  key_risks: string[];
  recommendations: string[];
  lean_canvas: LeanCanvas;
  swot: Record<string, string[]>;
  scores: ValidationScores;
  market_research: {
    tam_usd: string;
    sam_usd: string;
    som_usd: string;
    growth_rate: string;
    trends: string[];
    opportunities: string[];
    risks: string[];
    evidence: EvidenceCitation[];
    confidence: number;
  };
  competitor_analysis: {
    direct_competitors: Array<{
      name: string;
      description: string;
      pricing: string;
      business_model: string;
      strengths: string[];
      weaknesses: string[];
    }>;
    market_saturation: string;
    differentiation_opportunities: string[];
    swot: Record<string, string[]>;
    evidence: EvidenceCitation[];
    confidence: number;
  };
  legal_analysis: {
    compliance_risks: string[];
    regulations: string[];
    licensing_requirements: string[];
    privacy_concerns: string[];
    geography_specific: Record<string, string[]>;
    overall_risk_level: string;
    evidence: EvidenceCitation[];
    confidence: number;
  };
  debate: {
    contradictions: string[];
    resolutions: string[];
    consensus_points: string[];
    dissenting_views: string[];
    overall_confidence: number;
  };
  evidence_citations: EvidenceCitation[];
  generated_at: string;
}

export const AGENT_META: Record<AgentName, { label: string; icon: string; color: string }> = {
  front_desk: { label: "Front Desk", icon: "🛎️", color: "#6366f1" },
  orchestrator: { label: "Orchestrator", icon: "🧠", color: "#8b5cf6" },
  market_research: { label: "Market Research", icon: "📊", color: "#06b6d4" },
  competitor_analysis: { label: "Competitor Analysis", icon: "⚔️", color: "#f59e0b" },
  legal: { label: "Legal", icon: "⚖️", color: "#ef4444" },
  debate: { label: "Debate", icon: "💬", color: "#ec4899" },
  scoring: { label: "Scoring Engine", icon: "🎯", color: "#10b981" },
  report: { label: "Report Generator", icon: "📄", color: "#a78bfa" },
};

export const SAMPLE_IDEA =
  "VenturePilot AI — an autonomous multi-agent platform that validates startup ideas using real-world evidence, RAG retrieval, competitor analysis, and legal compliance checks. Target audience is pre-seed founders and angel investors. B2B SaaS model with tiered pricing ($49-$499/mo). Focus on US and EU markets.";
