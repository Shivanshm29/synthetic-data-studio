"use client";

import { DataScoutResponse, FetchResult, GapAnalysis } from "../lib/api";

interface DataScoutCardProps {
  analysis: DataScoutResponse;
  onProceedSynthetic: () => void;
  isGenerating?: boolean;
  fetchResult?: FetchResult | null;
  gapAnalysis?: GapAnalysis | null;
  isFetching?: boolean;
  isFillingGaps?: boolean;
  onLoadMore?: (rowCount: number) => void;
  isFetchingMore?: boolean;
  rowCount?: number;
}

export default function DataScoutCard({
  analysis,
  onProceedSynthetic,
  isGenerating,
  fetchResult,
  gapAnalysis,
  isFetching,
  isFillingGaps,
  onLoadMore,
  isFetchingMore,
  rowCount,
}: DataScoutCardProps) {
  const getStrategyBadgeColor = (strategy: string) => {
    switch (strategy) {
      case "Existing Dataset":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "Dataset Augmentation":
      case "Dataset Merge":
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      case "Synthetic Expansion":
      case "Schema Learning":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      default:
        return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
    }
  };

  return (
    <div className="glass rounded-xl p-6 border border-accent/20 flex flex-col gap-6 shadow-2xl animate-fade-in bg-gradient-to-b from-surface/80 via-surface to-surface/90">
      {/* Header Badge & Title */}
      <div className="flex items-center justify-between flex-wrap gap-4 border-b border-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
              />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-foreground tracking-tight">
                DataScout AI Strategy Analysis
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-accent/15 text-accent border border-accent/30">
                10-Step Evaluated
              </span>
            </div>
            <p className="text-xs text-text-muted mt-0.5">
              Domain: <span className="text-text-secondary">{analysis.domain}</span> · Industry:{" "}
              <span className="text-text-secondary">{analysis.industry}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStrategyBadgeColor(
              analysis.strategy
            )}`}
          >
            {analysis.strategy}
          </span>
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-text-muted">Confidence</span>
            <span className="text-xs font-mono font-bold text-foreground">
              {Math.round(analysis.confidence * 100)}%
            </span>
          </div>
        </div>
      </div>

      {/* Reasoning Banner */}
      <div className="p-3.5 rounded-lg bg-surface-hover/40 border border-border text-xs text-text-secondary leading-relaxed">
        <strong className="text-foreground">DataScout AI Assessment: </strong>
        {analysis.reasoning}
      </div>

      {/* Recommended Public Datasets (If Existing Dataset Strategy) */}
      {analysis.existing_datasets && analysis.existing_datasets.length > 0 && (
        <div className="flex flex-col gap-3">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
            Verified Public Datasets Found ({analysis.existing_datasets.length})
          </h3>

          {isFetching && (
            <div className="p-4 rounded-xl bg-surface/60 border border-emerald-500/30 flex items-center gap-3">
              <div className="w-4 h-4 rounded-full border-2 border-emerald-500/30 border-t-emerald-500 animate-spin" />
              <span className="text-sm text-foreground">Fetching data from {analysis.existing_datasets[0]?.source_platform}...</span>
            </div>
          )}

          {fetchResult && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex flex-col gap-3">
              <div className="flex items-center gap-2">
                <span className="text-emerald-400">✓</span>
                <span className="text-sm text-foreground">Loaded {fetchResult.count} rows from {fetchResult.dataset_name}</span>
              </div>
              {fetchResult.truncated && (
                <div className="flex items-center gap-4">
                  <button 
                    onClick={() => onLoadMore && onLoadMore(rowCount || 100)}
                    disabled={isFetchingMore}
                    className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-semibold hover:bg-emerald-500/30 transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    {isFetchingMore ? (
                      <>
                        <div className="w-3 h-3 rounded-full border-2 border-emerald-400/30 border-t-emerald-400 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      `Showing ${fetchResult.count} of ${fetchResult.total_available} rows — Load ${rowCount} rows`
                    )}
                  </button>
                </div>
              )}
            </div>
          )}

          {gapAnalysis?.has_gaps && (
            <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30 flex flex-col gap-3">
              <div className="flex items-center gap-2">
                {isFillingGaps ? (
                  <>
                    <div className="w-4 h-4 rounded-full border-2 border-purple-500/30 border-t-purple-500 animate-spin" />
                    <span className="text-sm text-foreground">Generating missing columns...</span>
                  </>
                ) : (
                  <>
                    <span className="text-purple-400">✓</span>
                    <span className="text-sm text-foreground">Gap Analysis: {gapAnalysis.missing_columns.length} columns will be synthetically generated</span>
                  </>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                {gapAnalysis.missing_columns.map((col) => (
                  <span key={col} className="px-2 py-1 rounded bg-purple-500/20 text-purple-300 text-xs border border-purple-500/30">
                    {col}
                  </span>
                ))}
              </div>
              {!isFillingGaps && fetchResult && (
                <span className="text-xs text-purple-400/80">✓ All columns complete</span>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 gap-4">
            {analysis.existing_datasets.map((ds, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-surface/60 border border-emerald-500/30 hover:border-emerald-500/60 transition-all flex flex-col gap-3"
              >
                <div className="flex items-start justify-between flex-wrap gap-2">
                  <div>
                    <h4 className="text-sm font-bold text-foreground">{ds.name}</h4>
                    <p className="text-xs text-text-secondary mt-1">{ds.description}</p>
                  </div>
                  <a
                    href={ds.download_source}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-[10px] text-text-muted hover:text-emerald-400 transition-colors"
                  >
                    <span>View on {ds.source_platform} ↗</span>
                  </a>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs py-2 border-y border-border/40 font-mono">
                  <div>
                    <span className="text-text-muted block text-[10px]">EST. ROWS</span>
                    <span className="text-foreground font-semibold">{ds.estimated_rows.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-text-muted block text-[10px]">COLUMNS</span>
                    <span className="text-foreground font-semibold">{ds.estimated_columns}</span>
                  </div>
                  <div>
                    <span className="text-text-muted block text-[10px]">LICENSE</span>
                    <span className="text-foreground font-semibold truncate block" title={ds.license}>{ds.license}</span>
                  </div>
                  <div>
                    <span className="text-text-muted block text-[10px]">QUALITY SCORE</span>
                    <span className="text-emerald-400 font-semibold">{Math.round(ds.quality_score * 100)}%</span>
                  </div>
                </div>

                {ds.advantages.length > 0 && (
                  <div className="flex items-center gap-2 flex-wrap text-xs text-emerald-400/90">
                    <span className="font-semibold text-text-muted">Advantages:</span>
                    {ds.advantages.map((adv, aIdx) => (
                      <span key={aIdx} className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                        ✓ {adv}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cost Optimization & Synthetic Plan Summary */}
      {analysis.synthetic_plan && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 rounded-lg bg-surface/50 border border-border">
            <h4 className="font-semibold text-text-muted mb-2 uppercase tracking-wider text-[10px]">
              Cost Optimization Breakdown
            </h4>
            <div className="flex flex-col gap-1.5">
              <div className="flex justify-between">
                <span className="text-text-secondary">Deterministic Fields (Faker):</span>
                <span className="font-mono text-success font-semibold">
                  {analysis.synthetic_plan.deterministic_columns?.length || 0} columns
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">LLM Text Fields:</span>
                <span className="font-mono text-purple-400 font-semibold">
                  {analysis.synthetic_plan.llm_columns?.length || 0} columns
                </span>
              </div>
            </div>
          </div>

          <div className="p-3.5 rounded-lg bg-surface/50 border border-border">
            <h4 className="font-semibold text-text-muted mb-2 uppercase tracking-wider text-[10px]">
              Estimated Quality & Privacy
            </h4>
            <div className="flex flex-col gap-1.5 font-mono">
              <div className="flex justify-between">
                <span className="text-text-secondary">Realism Score:</span>
                <span className="text-foreground font-semibold">
                  {Math.round((analysis.quality_estimate?.realism_score || 0.9) * 100)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Privacy Risk:</span>
                <span className="text-success font-semibold">
                  {analysis.quality_estimate?.privacy_risk || "Low"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Bar */}
      <div className="flex items-center justify-between flex-wrap gap-4 pt-2 border-t border-border/60">
        <span className="text-xs text-text-muted">
          Need a custom local synthetic dataset generated anyway?
        </span>
        <button
          onClick={onProceedSynthetic}
          disabled={isGenerating}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-accent to-purple-600 text-white text-xs font-semibold hover:shadow-lg hover:shadow-accent/25 transition-all cursor-pointer disabled:opacity-50"
        >
          {isGenerating ? "Generating Dataset..." : "Generate Synthetic Dataset"}
        </button>
      </div>
    </div>
  );
}
