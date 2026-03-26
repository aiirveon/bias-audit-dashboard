"use client";

import type { AuditEntry } from "@/lib/api";

interface AuditTableProps {
  entries: AuditEntry[];
}

export function AuditTable({ entries }: AuditTableProps) {
  if (entries.length === 0) {
    return (
      <div className="border border-border border-dashed p-10 flex flex-col items-center justify-center text-center space-y-3">
        <h3 className="text-sm tracking-wider text-foreground uppercase">NO AUDIT ENTRIES YET</h3>
        <p className="text-sm text-muted-foreground max-w-sm leading-relaxed">
          Reviewer actions will appear here after content has been analysed.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-panel border border-border overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-border">
            {["TIMESTAMP", "CONTENT SNIPPET", "CATEGORY", "SCORE", "CONFIDENCE", "ACTION"].map(col => (
              <th key={col} className="px-4 py-3 text-[9px] tracking-widest text-muted-foreground uppercase font-normal">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {entries.map((entry, i) => (
            <tr key={entry.id ?? i} className="border-b border-border/50 hover:bg-panel-dark transition-colors">
              <td className="px-4 py-3 font-mono text-[10px] text-muted-foreground tabular-nums whitespace-nowrap">
                {entry.created_at
                  ? new Date(entry.created_at).toLocaleString("en-GB", { dateStyle: "short", timeStyle: "short" })
                  : "—"}
              </td>
              <td className="px-4 py-3 text-xs text-foreground/80 max-w-[240px] truncate">
                {entry.content_snippet ?? "—"}
              </td>
              <td className="px-4 py-3">
                <span className="text-[9px] tracking-widest uppercase px-2 py-0.5 border border-border text-muted-foreground">
                  {entry.category?.replace(/_/g, " ") ?? "—"}
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-[10px] tabular-nums text-foreground">
                {entry.score ?? "—"}
              </td>
              <td className="px-4 py-3 font-mono text-[10px] tabular-nums text-muted-foreground">
                {entry.confidence != null ? `${(entry.confidence * 100).toFixed(0)}%` : "—"}
              </td>
              <td className="px-4 py-3">
                <span className={`text-[9px] tracking-widest uppercase px-2 py-0.5 border ${
                  entry.reviewer_action === "approve" ? "border-score-high text-score-high" :
                  entry.reviewer_action === "flag"    ? "border-score-mid text-score-mid"   :
                  entry.reviewer_action === "escalate"? "border-destructive text-destructive":
                  "border-border text-muted-foreground"
                }`}>
                  {entry.reviewer_action ?? "PENDING"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
