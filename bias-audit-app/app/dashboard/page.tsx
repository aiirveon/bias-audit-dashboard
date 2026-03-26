"use client";

import { useEffect, useState } from "react";
import { TopNav } from "@/components/top-nav";
import { FlagRateChart } from "@/components/dashboard/flag-rate-chart";
import { FairnessHealth } from "@/components/dashboard/fairness-health";
import { FairnessMetrics } from "@/components/dashboard/fairness-metrics";
import { getAuditMetrics } from "@/lib/api";
import type { AuditResult } from "@/lib/api";

const MODEL_STATS = [
  { category: "demographic_bias",    f1: 0.89, support: 100 },
  { category: "gender_stereotyping", f1: 0.94, support: 100 },
  { category: "geographic_bias",     f1: 0.92, support: 100 },
  { category: "neutral",             f1: 0.85, support: 100 },
  { category: "racial_bias",         f1: 0.87, support: 100 },
  { category: "religious_bias",      f1: 0.95, support: 100 },
];

export default function DashboardPage() {
  const [data, setData]       = useState<AuditResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuditMetrics().then(setData).finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <TopNav />

      <div className="max-w-4xl mx-auto px-4 py-8 w-full space-y-6">

        <div>
          <h1 className="text-[10px] tracking-widest text-muted-foreground uppercase">
            AUDIT DASHBOARD
          </h1>
          <p className="text-sm text-foreground mt-1">
            Model evaluation metrics — 3,000 item synthetic dataset · 600 item held-out test set
          </p>
        </div>

        {loading ? (
          <div className="space-y-4">
            <div className="h-24 w-full shimmer" />
            <div className="h-48 w-full shimmer" />
          </div>
        ) : data ? (
          <>
            <FairnessHealth health={data.fairness_health} disparity={data.disparity_ratio} />

            {/* Model performance panel */}
            <div className="bg-panel border border-border p-5 space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-[9px] tracking-widest text-muted-foreground uppercase">
                  MODEL PERFORMANCE — F1 SCORE PER CATEGORY
                </p>
                <span className="text-[9px] tracking-widest uppercase px-2 py-0.5 border border-score-high text-score-high">
                  OVERALL 0.90
                </span>
              </div>

              <div className="space-y-2">
                {MODEL_STATS.map(stat => {
                  const pct      = stat.f1 * 100;
                  const barColor = stat.f1 >= 0.90 ? "bg-score-high"
                    : stat.f1 >= 0.78              ? "bg-score-mid"
                    :                                "bg-score-low";

                  return (
                    <div key={stat.category} className="py-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[9px] tracking-wider text-muted-foreground uppercase">
                          {stat.category.replace(/_/g, " ")}
                        </span>
                        <span className={`font-mono text-[10px] tabular-nums ${barColor.replace("bg-", "text-")}`}>
                          {stat.f1.toFixed(2)}
                        </span>
                      </div>
                      <div className="w-full h-[2px] bg-border/30 relative">
                        <div
                          className={`absolute inset-y-0 left-0 ${barColor}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="pt-2 border-t border-border grid grid-cols-3 gap-4">
                <div>
                  <p className="text-[9px] tracking-widest text-muted-foreground uppercase">TRAIN SET</p>
                  <p className="font-mono text-sm text-foreground tabular-nums">2,400</p>
                </div>
                <div>
                  <p className="text-[9px] tracking-widest text-muted-foreground uppercase">TEST SET</p>
                  <p className="font-mono text-sm text-foreground tabular-nums">600</p>
                </div>
                <div>
                  <p className="text-[9px] tracking-widest text-muted-foreground uppercase">CATEGORIES</p>
                  <p className="font-mono text-sm text-foreground tabular-nums">6</p>
                </div>
              </div>
            </div>

            <FlagRateChart  flagRates={data.flag_rates} />
            <FairnessMetrics />
          </>
        ) : (
          <p className="text-sm text-muted-foreground">Failed to load audit data.</p>
        )}

      </div>
    </div>
  );
}
