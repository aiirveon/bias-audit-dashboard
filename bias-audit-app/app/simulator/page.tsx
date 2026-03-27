"use client";
import { useState, useRef, useEffect } from "react";
import { TopNav } from "@/components/top-nav";
import { analyseContent, explainResult } from "@/lib/api";

type ModerationStatus = "pending" | "analysing" | "approved" | "flagged" | "removed";

interface Comment {
  id: string;
  author: string;
  text: string;
  timestamp: string;
  status: ModerationStatus;
  score?: number;
  category?: string;
  confidence?: number;
  shap_values?: Record<string, number>;
  explanation?: string;
}

const AVATARS = ["AT", "BK", "CL", "DM", "EN", "FO", "GP", "HQ"];
const AUTHORS = ["Alex T.", "Bex K.", "Carl L.", "Dana M.", "Eren N.", "Fiona O.", "Greg P.", "Hana Q."];

function getAuthor(id: string) {
  const idx = Math.abs(id.charCodeAt(0) + id.charCodeAt(1)) % AUTHORS.length;
  return { name: AUTHORS[idx], avatar: AVATARS[idx] };
}

function timeNow() {
  return new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

const getBadgeClass = (category: string, score: number) => {
  if (category === "neutral") return "border-verdict-neutral text-verdict-neutral";
  if (score < 30) return "border-verdict-low text-verdict-low";
  if (score < 65) return "border-verdict-medium text-verdict-medium";
  return "border-verdict-high text-verdict-high";
};

const getRiskLabel = (category: string, score: number) => {
  if (category === "neutral") return "NEUTRAL";
  if (score < 30) return "LOW RISK";
  if (score < 65) return "MEDIUM RISK";
  return "HIGH RISK";
};

export default function SimulatorPage() {
  const [comments, setComments] = useState<Comment[]>([]);
  const [input, setValue] = useState("");
  const [isPosting, setIsPosting] = useState(false);
  const feedBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    feedBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [comments]);

  const handlePost = async () => {
    if (!input.trim() || isPosting) return;
    const id = crypto.randomUUID();
    const text = input.trim();

    // Skip analysis for very short inputs — model unreliable under 4 words
    const wordCount = text.split(/\s+/).length;
    if (wordCount < 4) {
      const shortComment: Comment = {
        id,
        author: getAuthor(id).name,
        text,
        timestamp: timeNow(),
        status: "approved",
      };
      setComments(prev => [...prev, shortComment]);
      setValue("");
      setIsPosting(false);
      return;
    }

    setValue("");
    setIsPosting(true);

    const newComment: Comment = {
      id,
      author: getAuthor(id).name,
      text,
      timestamp: timeNow(),
      status: "analysing",
    };
    setComments(prev => [...prev, newComment]);

    try {
      const result = await analyseContent(text);
      const exp = await explainResult({
        content: text,
        score: result.score,
        category: result.category,
        confidence: result.confidence,
        shap_values: result.shap_values,
      });
      setComments(prev =>
        prev.map(c =>
          c.id === id
            ? {
                ...c,
                status: "pending",
                score: result.score,
                category: result.category,
                confidence: result.confidence,
                shap_values: result.shap_values,
                explanation: exp.explanation,
              }
            : c
        )
      );
    } catch {
      setComments(prev =>
        prev.map(c => (c.id === id ? { ...c, status: "approved" } : c))
      );
    } finally {
      setIsPosting(false);
    }
  };

  const handleAction = (id: string, action: "approved" | "flagged" | "removed") => {
    setComments(prev =>
      prev.map(c => (c.id === id ? { ...c, status: action } : c))
    );
  };

  const pending = comments.filter(c => c.status === "pending" || c.status === "analysing");
  const reviewed = comments.filter(c => c.status === "approved" || c.status === "flagged" || c.status === "removed");

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />
      <div className="flex-1 overflow-hidden grid grid-cols-2 divide-x divide-border">

        {/* ── LEFT: PUBLIC FEED ── */}
        <div className="flex flex-col h-full">
          <div className="px-5 py-3 border-b border-border bg-panel-dark flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-score-high status-pulse" />
            <span className="text-[10px] tracking-widest text-muted-foreground uppercase">Public Feed</span>
            <span className="text-[9px] text-muted-foreground ml-auto">{comments.length} comments</span>
          </div>

          <div className="flex-1 panel-scroll px-4 py-4 space-y-3">
            {comments.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-2 py-20">
                <p className="text-[10px] tracking-widest text-muted-foreground uppercase">No comments yet</p>
                <p className="text-xs text-muted-foreground max-w-xs leading-relaxed">
                  Type something below and post it. It will appear here instantly.
                </p>
              </div>
            )}
            {comments.map(comment => {
              const { avatar } = getAuthor(comment.id);
              const isRemoved = comment.status === "removed";
              const isFlagged = comment.status === "flagged";
              const isAnalysing = comment.status === "analysing";
              return (
                <div key={comment.id} className={`bg-panel border p-3 space-y-1 transition-colors ${
                  isRemoved ? "border-destructive/30 opacity-40" :
                  isFlagged ? "border-score-mid/50" :
                  "border-border"
                }`}>
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-panel-dark border border-border flex items-center justify-center shrink-0">
                      <span className="text-[8px] font-mono text-muted-foreground">{avatar}</span>
                    </div>
                    <span className="text-[11px] text-foreground font-medium">{comment.author}</span>
                    <span className="text-[9px] text-muted-foreground ml-auto">{comment.timestamp}</span>
                    {isAnalysing && (
                      <span className="text-[8px] tracking-widest text-muted-foreground uppercase">
                        checking...
                      </span>
                    )}
                    {isFlagged && (
                      <span className="text-[8px] tracking-widest uppercase text-score-mid border border-score-mid px-1.5 py-0.5">
                        FLAGGED
                      </span>
                    )}
                    {isRemoved && (
                      <span className="text-[8px] tracking-widest uppercase text-destructive border border-destructive px-1.5 py-0.5">
                        REMOVED
                      </span>
                    )}
                  </div>
                  <p className={`text-sm leading-relaxed pl-9 ${
                    isRemoved ? "line-through text-muted-foreground" : "text-foreground/90"
                  }`}>
                    {comment.text}
                  </p>
                </div>
              );
            })}
            <div ref={feedBottomRef} />
          </div>

          {/* Comment input */}
          <div className="border-t border-border bg-panel-dark p-3">
            <div className="flex gap-2 items-end">
              <textarea
                value={input}
                onChange={e => setValue(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handlePost(); }
                }}
                placeholder="Write a comment..."
                rows={2}
                className="flex-1 bg-background border border-border text-sm text-foreground placeholder:text-muted-foreground p-2.5 resize-none focus:outline-none focus:border-primary transition-colors"
              />
              <button
                onClick={handlePost}
                disabled={!input.trim() || isPosting}
                className="h-[60px] px-4 bg-primary text-primary-foreground text-[10px] font-medium tracking-[0.2em] uppercase hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
              >
                {isPosting ? "..." : "POST"}
              </button>
            </div>
          </div>
        </div>

        {/* ── RIGHT: MODERATION QUEUE ── */}
        <div className="flex flex-col h-full">
          <div className="px-5 py-3 border-b border-border bg-panel-dark flex items-center gap-2">
            <span className="text-[10px] tracking-widest text-muted-foreground uppercase">Moderation Queue</span>
            {pending.length > 0 && (
              <span className="text-[9px] font-mono bg-destructive/20 text-destructive border border-destructive/30 px-1.5 py-0.5">
                {pending.length} awaiting review
              </span>
            )}
          </div>

          <div className="flex-1 panel-scroll px-4 py-4 space-y-3">
            {pending.length === 0 && reviewed.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-2 py-20">
                <p className="text-[10px] tracking-widest text-muted-foreground uppercase">Queue empty</p>
                <p className="text-xs text-muted-foreground max-w-xs leading-relaxed">
                  Comments posted to the feed will appear here for moderation.
                </p>
              </div>
            )}

            {/* Pending / analysing */}
            {pending.map(comment => (
              <div key={comment.id} className="bg-panel border border-border p-4 space-y-3">
                <p className="text-sm text-foreground/80 border-l-2 border-border pl-3 italic leading-relaxed">
                  "{comment.text.length > 100 ? comment.text.slice(0, 100) + "…" : comment.text}"
                </p>

                {comment.status === "analysing" ? (
                  <div className="space-y-2">
                    <div className="h-3 w-1/2 shimmer" />
                    <div className="h-3 w-3/4 shimmer" />
                    <div className="h-10 w-full shimmer" />
                  </div>
                ) : (
                  <>
                    {/* Verdict row */}
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className={`text-[9px] tracking-widest uppercase px-2.5 py-1 border ${getBadgeClass(comment.category!, comment.score!)}`}>
                        {comment.category!.replace(/_/g, " ")}
                      </span>
                      <span className="font-mono text-[10px] text-muted-foreground tabular-nums">
                        {((comment.confidence || 0) * 100).toFixed(0)}% confidence
                      </span>
                      <span className={`font-mono text-[10px] tabular-nums ${getBadgeClass(comment.category!, comment.score!).split(" ")[1]}`}>
                        {getRiskLabel(comment.category!, comment.score!)}
                      </span>
                      <span className="font-mono text-[10px] text-muted-foreground ml-auto">
                        {comment.score}
                      </span>
                    </div>

                    {/* SHAP words */}
                    {Object.keys(comment.shap_values || {}).length > 0 && (
                      <div className="space-y-1">
                        <p className="text-[9px] tracking-widest text-muted-foreground uppercase">Triggered by</p>
                        <div className="flex flex-wrap gap-1.5">
                          {Object.keys(comment.shap_values!).slice(0, 5).map((word, i) => (
                            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-primary/10 border border-primary/30 text-primary font-mono">
                              {word}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Explanation */}
                    <div className="bg-recommendations border-l-2 border-primary px-3 py-2">
                      <p className="text-[9px] tracking-widest text-primary uppercase mb-1">Explanation</p>
                      <p className="text-xs text-foreground/90 leading-relaxed">{comment.explanation}</p>
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center gap-2 pt-1 border-t border-border">
                      <p className="text-[9px] tracking-widest text-muted-foreground uppercase mr-auto">Action</p>
                      <button
                        onClick={() => handleAction(comment.id, "approved")}
                        className="px-3 py-1.5 border border-score-high text-score-high text-[9px] tracking-widest uppercase hover:bg-score-high hover:text-background transition-colors">
                        APPROVE
                      </button>
                      <button
                        onClick={() => handleAction(comment.id, "flagged")}
                        className="px-3 py-1.5 border border-score-mid text-score-mid text-[9px] tracking-widest uppercase hover:bg-score-mid hover:text-background transition-colors">
                        FLAG
                      </button>
                      <button
                        onClick={() => handleAction(comment.id, "removed")}
                        className="px-3 py-1.5 border border-destructive text-destructive text-[9px] tracking-widest uppercase hover:bg-destructive hover:text-background transition-colors">
                        REMOVE
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}

            {/* Reviewed section */}
            {reviewed.length > 0 && (
              <div className="space-y-2">
                <p className="text-[9px] tracking-widest text-muted-foreground uppercase pt-2">Reviewed</p>
                {reviewed.map(comment => (
                  <div key={comment.id} className="bg-panel border border-border/50 p-3 flex items-center gap-3 opacity-60">
                    <p className="text-xs text-muted-foreground flex-1 truncate italic">
                      "{comment.text.slice(0, 60)}{comment.text.length > 60 ? "…" : ""}"
                    </p>
                    <span className={`text-[9px] tracking-widest uppercase px-2 py-0.5 border shrink-0 ${
                      comment.status === "approved" ? "border-score-high text-score-high" :
                      comment.status === "flagged" ? "border-score-mid text-score-mid" :
                      "border-destructive text-destructive"
                    }`}>
                      {comment.status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
