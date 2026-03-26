export function WarmingUp() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4 py-20">
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-primary status-pulse" />
        <span className="text-[10px] tracking-widest text-muted-foreground uppercase">
          WARMING UP
        </span>
      </div>
      <p className="text-xs text-muted-foreground max-w-xs text-center leading-relaxed">
        The analysis engine is starting. This takes 20–40 seconds on first load.
      </p>
    </div>
  );
}
