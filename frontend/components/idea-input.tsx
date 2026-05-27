"use client";

import { useState } from "react";
import { Sparkles, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SAMPLE_IDEA } from "@/lib/types";

interface IdeaInputProps {
  onSubmit: (idea: string) => void;
  disabled?: boolean;
}

export function IdeaInput({ onSubmit, disabled }: IdeaInputProps) {
  const [idea, setIdea] = useState("");

  const handleSubmit = () => {
    if (idea.trim().length >= 10) onSubmit(idea.trim());
  };

  return (
    <Card className="border-indigo-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Rocket className="h-5 w-5 text-indigo-400" />
          Describe Your Startup Idea
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Describe your startup idea — target audience, business model, geography, industry..."
          className="w-full h-32 rounded-lg bg-secondary/50 border border-border p-4 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder:text-muted-foreground"
          disabled={disabled}
        />
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setIdea(SAMPLE_IDEA)}
            className="text-xs text-muted-foreground hover:text-indigo-400 transition-colors"
            disabled={disabled}
          >
            Load sample idea
          </button>
          <Button onClick={handleSubmit} disabled={disabled || idea.trim().length < 10} size="lg">
            <Sparkles className="h-4 w-4" />
            Validate Idea
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
