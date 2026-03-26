"use client";

import { useState, useEffect, useRef } from "react";
import { TopNav } from "@/components/top-nav";
import { ChatInput } from "@/components/analyser/chat-input";
import { ResultCard } from "@/components/analyser/result-card";
import { WarmingUp } from "@/components/analyser/warming-up";
import { analyseContent, explainResult, pingHealth } from "@/lib/api";

interface AnalysisItem {
  id:          string;
  content:     string;
  score:       number;
  category:    string;
  confidence:  number;
  shap_values: Record<string, number>;
  explanation: string;
  actionTaken?: string;
}

export default function Home() {
  const [ready, setReady]     = useState(false);
  const [loading, setLoading] = useState(false);
  const [items, setItems]     = useState<AnalysisItem[]>([]);
  const bottomRef             = useRef<HTMLDivElement>(null);

  // Silent health ping on mount — cold start wake for Render free tier
  useEffect(() => {
    const poll = async () => {
      const ok = await pingHealth();
      if (ok) { setReady(true); return; }
      setTimeout(poll, 3000);
    };
    poll();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [items]);

  const handleSubmit = async (content: string) => {
    setLoading(true);
    try {
      const result = await analyseContent(content);
      const exp    = await explainResult({
        content,
        score:       result.score,
        category:    result.category,
        confidence:  result.confidence,
        shap_values: result.shap_values,
      });
      setItems(prev => [...prev, {
        id:          crypto.randomUUID(),
        content,
        score:       result.score,
        category:    result.category,
        confidence:  result.confidence,
        shap_values: result.shap_values,
        explanation: exp.explanation,
      }]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (id: string, action: "approve" | "flag" | "escalate") => {
    setItems(prev =>
      prev.map(item => item.id === id ? { ...item, actionTaken: action } : item)
    );
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">

          {!ready && <WarmingUp />}

          {ready && items.length === 0 && (
            <div className="border border-border border-dashed p-10 flex flex-col items-center justify-center text-center space-y-3 mt-20">
              <h3 className="text-sm tracking-wider text-foreground uppercase">
                NO CONTENT ANALYSED YET
              </h3>
              <p className="text-sm text-muted-foreground max-w-sm leading-relaxed">
                Type or paste a headline, social post, or article excerpt below to begin.
              </p>
            </div>
          )}

          {items.map(item => (
            <ResultCard
              key={item.id}
              {...item}
              onAction={(action) => handleAction(item.id, action)}
            />
          ))}

          {loading && (
            <div className="bg-panel border border-border p-4 space-y-3">
              <div className="h-4 w-3/4 shimmer" />
              <div className="h-3 w-1/2 shimmer" />
              <div className="h-16 w-full shimmer" />
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <ChatInput onSubmit={handleSubmit} disabled={!ready} isLoading={loading} />
    </div>
  );
}
