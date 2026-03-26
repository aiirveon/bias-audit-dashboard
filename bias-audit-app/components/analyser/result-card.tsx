"use client";

interface ResultCardProps {
  content:      string;
  score:        number;
  category:     string;
  confidence:   number;
  shap_values:  Record<string, number>;
  explanation:  string;
  onAction:     (action: "approve" | "flag" | "escalate") => void;
  actionTaken?: string;
}

const getBadgeClass = (category: string, score: number) => {
  if (category === "neutral") return "border-verdict-neutral text-verdict-neutral";
  if (score < 30)             return "border-verdict-low text-verdict-low";
  if (score < 65)             return "border-verdict-medium text-verdict-medium";
  return "border-verdict-high text-verdict-high";
};

const getRiskLabel = (category: string, score: number) => {
  if (category === "neutral") return "NEUTRAL";
  if (score < 30)             return "LOW RISK";
  if (score < 65)             return "MEDIUM RISK";
  return "HIGH RISK";
};

export function ResultCard({
  content, score, category, confidence, shap_values,
  explanation, onAction, actionTaken,
}: ResultCardProps) {
  const badgeClass = getBadgeClass(category, score);
  const shapWords  = Object.keys(shap_values);

  return (
    <div className="bg-panel border border-border p-4 space-y-3">

      {/* Content snippet */}
      <p className="text-sm text-foreground/80 leading-relaxed border-l-2 border-border pl-3 italic">
        "{content.length > 120 ? content.slice(0, 120) + "…" : content}"
      </p>

      {/* Verdict row */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className={`text-[9px] tracking-widest uppercase px-2.5 py-1 border ${badgeClass}`}>
          {category.replace(/_/g, " ")}
        </span>
        <span className="font-mono text-[10px] text-muted-foreground tabular-nums">
          {(confidence * 100).toFixed(0)}% confidence
        </span>
        <span className={`font-mono text-[10px] tabular-nums ${badgeClass.split(" ")[1]}`}>
          {getRiskLabel(category, score)}
        </span>
        <span className="font-mono text-[10px] text-muted-foreground tabular-nums ml-auto">
          Score: {score}
        </span>
      </div>

      {/* SHAP highlights */}
      {shapWords.length > 0 && (
        <div className="space-y-1">
          <p className="text-[9px] tracking-widest text-muted-foreground uppercase">TRIGGERED BY</p>
          <div className="flex flex-wrap gap-1.5">
            {shapWords.slice(0, 6).map((word, i) => (
              <span
                key={i}
                className="text-[10px] px-1.5 py-0.5 bg-primary/10 border border-primary/30 text-primary font-mono"
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Plain English explanation */}
      <div className="bg-recommendations border-l-2 border-primary px-4 py-3">
        <p className="text-[9px] tracking-widest text-primary uppercase mb-1">EXPLANATION</p>
        <p className="text-xs text-foreground/90 leading-relaxed">{explanation}</p>
      </div>

      {/* Reviewer action row */}
      <div className="flex items-center gap-2 pt-1 border-t border-border">
        <p className="text-[9px] tracking-widest text-muted-foreground uppercase mr-auto">
          REVIEWER ACTION
        </p>
        {actionTaken ? (
          <span className="text-[9px] tracking-widest uppercase px-3 py-1.5 border border-border text-muted-foreground">
            {actionTaken.toUpperCase()}
          </span>
        ) : (
          <>
            <button
              onClick={() => onAction("approve")}
              className="px-3 py-1.5 border border-score-high text-score-high text-[9px] tracking-widest uppercase hover:bg-score-high hover:text-background transition-colors"
            >
              APPROVE
            </button>
            <button
              onClick={() => onAction("flag")}
              className="px-3 py-1.5 border border-score-mid text-score-mid text-[9px] tracking-widest uppercase hover:bg-score-mid hover:text-background transition-colors"
            >
              FLAG
            </button>
            <button
              onClick={() => onAction("escalate")}
              className="px-3 py-1.5 border border-destructive text-destructive text-[9px] tracking-widest uppercase hover:bg-destructive hover:text-background transition-colors"
            >
              ESCALATE
            </button>
          </>
        )}
      </div>

    </div>
  );
}
