"use client";

import { Download, TrendingUp, Shield, Users, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { ValidationReport } from "@/lib/types";
import { API_URL, cn } from "@/lib/utils";

interface ReportViewProps {
  report: ValidationReport;
}

function ScoreCard({ label, score, invert }: { label: string; score: number; invert?: boolean }) {
  const display = invert ? 100 - score : score;
  const color = display >= 70 ? "text-emerald-400" : display >= 50 ? "text-yellow-400" : "text-red-400";

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className={cn("font-bold", color)}>{score.toFixed(0)}</span>
      </div>
      <Progress value={score} />
    </div>
  );
}

export function ReportView({ report }: ReportViewProps) {
  const handleDownload = () => {
    window.open(`${API_URL}/api/reports/${report.session_id}/pdf`, "_blank");
  };

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gradient">Validation Report</h2>
          <p className="text-sm text-muted-foreground mt-1">{report.idea_summary}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-4xl font-bold text-indigo-400">{report.scores.overall_grade}</div>
            <div className="text-xs text-muted-foreground">Overall Grade</div>
          </div>
          <Button onClick={handleDownload} variant="outline">
            <Download className="h-4 w-4" />
            Download PDF
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-400" />
            Executive Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-line">
            {report.executive_summary}
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Validation Scores</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <ScoreCard label="Validation" score={report.scores.validation_score} />
            <ScoreCard label="Market Opportunity" score={report.scores.market_opportunity_score} />
            <ScoreCard label="Competition Pressure" score={report.scores.competition_score} invert />
            <ScoreCard label="Risk Level" score={report.scores.risk_score} invert />
            <ScoreCard label="Investor Attractiveness" score={report.scores.investor_attractiveness_score} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Users className="h-4 w-4" /> Market Research</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="p-2 rounded bg-secondary/50"><div className="font-bold text-indigo-400">{report.market_research.tam_usd}</div><div className="text-[10px] text-muted-foreground">TAM</div></div>
              <div className="p-2 rounded bg-secondary/50"><div className="font-bold text-purple-400">{report.market_research.sam_usd}</div><div className="text-[10px] text-muted-foreground">SAM</div></div>
              <div className="p-2 rounded bg-secondary/50"><div className="font-bold text-pink-400">{report.market_research.som_usd}</div><div className="text-[10px] text-muted-foreground">SOM</div></div>
            </div>
            <p>Growth: <span className="text-emerald-400">{report.market_research.growth_rate}</span></p>
            <div>
              <p className="font-medium mb-1">Trends</p>
              <ul className="space-y-1">{report.market_research.trends.map((t, i) => <li key={i} className="text-muted-foreground">• {t}</li>)}</ul>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Competitors ({report.competitor_analysis.direct_competitors.length})</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {report.competitor_analysis.direct_competitors.map((c) => (
              <div key={c.name} className="p-3 rounded-lg bg-secondary/30 border border-border/30">
                <div className="font-medium">{c.name}</div>
                <div className="text-xs text-muted-foreground">{c.pricing} · {c.business_model}</div>
              </div>
            ))}
            <p className="text-sm">Saturation: <span className="text-yellow-400">{report.competitor_analysis.market_saturation}</span></p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Shield className="h-4 w-4" /> Legal & Compliance</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>Risk Level: <span className="text-yellow-400 capitalize">{report.legal_analysis.overall_risk_level}</span></p>
            {report.legal_analysis.compliance_risks.map((r, i) => (
              <div key={i} className="flex items-start gap-2"><AlertTriangle className="h-3 w-3 text-yellow-400 mt-0.5 shrink-0" /><span className="text-muted-foreground">{r}</span></div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>SWOT Analysis</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(report.swot).map(([key, items]) => (
              <div key={key} className="p-3 rounded-lg bg-secondary/30">
                <div className="text-xs font-bold uppercase text-indigo-400 mb-2">{key}</div>
                <ul className="space-y-1">{items.map((item, i) => <li key={i} className="text-xs text-muted-foreground">• {item}</li>)}</ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Lean Canvas</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
            {Object.entries(report.lean_canvas).map(([key, value]) => (
              <div key={key} className="p-3 rounded-lg bg-secondary/30">
                <div className="text-xs font-bold uppercase text-purple-400 mb-1">{key.replace(/_/g, " ")}</div>
                <p className="text-muted-foreground text-xs">{value}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Recommendations</CardTitle></CardHeader>
        <CardContent>
          <ol className="space-y-2">{report.recommendations.map((r, i) => (
            <li key={i} className="flex gap-3 text-sm"><span className="text-indigo-400 font-bold">{i + 1}.</span>{r}</li>
          ))}</ol>
        </CardContent>
      </Card>

      {report.evidence_citations.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Evidence Citations</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {report.evidence_citations.slice(0, 6).map((c, i) => (
              <div key={i} className="p-2 rounded bg-secondary/20 text-xs">
                <span className="text-indigo-400 font-medium">[{c.source}]</span> {c.title}
                <p className="text-muted-foreground mt-1">{c.snippet}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
