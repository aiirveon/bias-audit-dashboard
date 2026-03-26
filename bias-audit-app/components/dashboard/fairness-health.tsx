interface FairnessHealthProps {
  health:    "green" | "amber" | "red";
  disparity: number;
}

const healthConfig = {
  green: { label: "HEALTHY",  color: "text-score-high", border: "border-score-high", dot: "bg-score-high" },
  amber: { label: "REVIEW",   color: "text-score-mid",  border: "border-score-mid",  dot: "bg-score-mid"  },
  red:   { label: "CRITICAL", color: "text-score-low",  border: "border-score-low",  dot: "bg-score-low"  },
};

export function FairnessHealth({ health, disparity }: FairnessHealthProps) {
  const cfg = healthConfig[health];

  return (
    <div className={`bg-panel border ${cfg.border} p-5 flex items-center justify-between`}>
      <div className="space-y-1">
        <p className="text-[9px] tracking-widest text-muted-foreground uppercase">
          OVERALL FAIRNESS HEALTH
        </p>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
          <span className={`text-sm font-medium tracking-wider ${cfg.color}`}>
            {cfg.label}
          </span>
        </div>
      </div>
      <div className="text-right">
        <p className="text-[9px] tracking-widest text-muted-foreground uppercase">DISPARITY RATIO</p>
        <p className={`font-mono text-xl tabular-nums ${cfg.color}`}>{disparity.toFixed(2)}×</p>
        <p className="text-[9px] text-muted-foreground">max / min flag rate</p>
      </div>
    </div>
  );
}
