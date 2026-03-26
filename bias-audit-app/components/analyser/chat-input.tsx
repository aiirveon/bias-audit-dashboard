"use client";

import { useState } from "react";

interface ChatInputProps {
  onSubmit:   (content: string) => void;
  disabled?:  boolean;
  isLoading?: boolean;
}

export function ChatInput({ onSubmit, disabled, isLoading }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = () => {
    if (!value.trim() || disabled || isLoading) return;
    onSubmit(value.trim());
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-border bg-panel-dark p-4">
      <div className="flex gap-3 items-end max-w-4xl mx-auto">
        <textarea
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isLoading}
          placeholder={
            disabled
              ? "Waiting for engine to warm up..."
              : "Paste a headline, social post, or article excerpt..."
          }
          rows={3}
          className="flex-1 bg-background border border-border text-sm text-foreground placeholder:text-muted-foreground p-3 resize-none focus:outline-none focus:border-primary transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSubmit}
          disabled={!value.trim() || disabled || isLoading}
          className="h-[76px] px-6 bg-primary text-primary-foreground text-[10px] font-medium tracking-[0.2em] uppercase hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          {isLoading ? "ANALYSING..." : "ANALYSE"}
        </button>
      </div>
    </div>
  );
}
