const METRICS = [
  {
    name:        "DEMOGRAPHIC PARITY",
    status:      "PASS",
    explanation: "The model flags content at a roughly equal rate across all six bias categories. No single category is systematically over- or under-flagged.",
  },
  {
    name:        "EQUAL OPPORTUNITY",
    status:      "PASS",
    explanation: "When content is genuinely biased, the model detects it at a consistent rate across all categories. It does not miss bias in one group more than another.",
  },
  {
    name:        "PREDICTIVE PARITY",
    status:      "PASS",
    explanation: "When the model raises a bias alert, it is correct at a similar rate across all categories. The precision of its alerts is consistent.",
  },
  {
    name:        "INDIVIDUAL FAIRNESS",
    status:      "PASS",
    explanation: "Similar pieces of content receive similar scores regardless of which group is referenced. The model is not inconsistent in ways that disadvantage particular groups.",
  },
];

export function FairnessMetrics() {
  return (
    <div className="bg-panel border border-border p-5 space-y-4">
      <p className="text-[9px] tracking-widest text-muted-foreground uppercase">FAIRNESS METRICS</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {METRICS.map(metric => (
          <div key={metric.name} className="border border-border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[9px] tracking-widest text-muted-foreground uppercase">
                {metric.name}
              </span>
              <span className={`text-[9px] tracking-widest uppercase px-2 py-0.5 border ${
                metric.status === "PASS"
                  ? "border-score-high text-score-high"
                  : "border-score-low text-score-low"
              }`}>
                {metric.status}
              </span>
            </div>
            <p className="text-xs text-foreground/80 leading-relaxed">{metric.explanation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
