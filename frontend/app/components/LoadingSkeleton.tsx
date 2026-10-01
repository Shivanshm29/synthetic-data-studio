export default function LoadingSkeleton() {
  return (
    <div className="animate-fade-in flex flex-col gap-5">
      {/* Live Stage Progress Indicator */}
      <div className="glass rounded-xl p-5 border border-accent/20 bg-gradient-to-r from-surface via-surface-hover/30 to-surface">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-3">
          <div className="flex items-center gap-3">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-accent"></span>
            </span>
            <span className="text-sm font-medium text-foreground">
              Generating Synthetic Dataset...
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-text-muted">
            <span className="px-2 py-0.5 rounded bg-accent/10 text-accent font-mono">
              Ollama & LLM Optimized
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface/80 border border-border">
            <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            <span className="text-text-secondary">1. Schema Inference</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface/80 border border-border">
            <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
            <span className="text-text-secondary">2. Strategy Selection</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface/80 border border-border">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span className="text-text-secondary">3. Batch Data Synthesis</span>
          </div>
        </div>
      </div>

      {/* Table Skeleton */}
      <div className="glass rounded-xl overflow-hidden border border-border">
        <div className="flex gap-4 px-5 py-3 border-b border-border bg-surface/50">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-4 flex-1 rounded animate-shimmer"
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          ))}
        </div>
        {Array.from({ length: 6 }).map((_, row) => (
          <div
            key={row}
            className="flex gap-4 px-5 py-3 border-b border-border/40"
          >
            {Array.from({ length: 5 }).map((_, col) => (
              <div
                key={col}
                className="h-4 flex-1 rounded animate-shimmer"
                style={{
                  animationDelay: `${(row * 5 + col) * 0.05}s`,
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

