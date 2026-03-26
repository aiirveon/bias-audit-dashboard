"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface FlagRateChartProps {
  flagRates: Record<string, number>;
}

const CATEGORY_COLOURS: Record<string, string> = {
  demographic_bias:    "#E85D4A",
  gender_stereotyping: "#E8954A",
  geographic_bias:     "#E8C547",
  racial_bias:         "#E85D4A",
  religious_bias:      "#E8954A",
  neutral:             "#4CAF50",
};

export function FlagRateChart({ flagRates }: FlagRateChartProps) {
  const data = Object.entries(flagRates).map(([category, rate]) => ({
    category: category.replace(/_/g, " ").toUpperCase(),
    rate,
    key: category,
  }));

  return (
    <div className="bg-panel border border-border p-5 space-y-4">
      <p className="text-[9px] tracking-widest text-muted-foreground uppercase">
        FLAG RATES BY CATEGORY (%)
      </p>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 0, right: 0, bottom: 40, left: 0 }}>
            <XAxis
              dataKey="category"
              tick={{ fill: "#888888", fontSize: 8, fontFamily: "Inter" }}
              angle={-25}
              textAnchor="end"
              interval={0}
            />
            <YAxis tick={{ fill: "#888888", fontSize: 9 }} width={30} />
            <Tooltip
              contentStyle={{ background: "#141414", border: "1px solid #2A2A2A", borderRadius: "2px" }}
              labelStyle={{ color: "#888888", fontSize: "10px" }}
              itemStyle={{ color: "#F0F0F0", fontSize: "11px" }}
            />
            <Bar dataKey="rate" radius={[1, 1, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.key} fill={CATEGORY_COLOURS[entry.key] || "#E8C547"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
