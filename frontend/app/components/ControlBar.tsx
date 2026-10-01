"use client";

interface ControlBarProps {
  rowCount: number;
  onRowCountChange: (count: number) => void;
  onProcessRequest: () => void;
  loading: boolean;
  analyzing: boolean;
  disabled: boolean;
}

const PRESETS = [10, 100, 1000, 10000];

export default function ControlBar({
  rowCount,
  onRowCountChange,
  onProcessRequest,
  loading,
  analyzing,
  disabled,
}: ControlBarProps) {
  const isWorking = loading || analyzing;

  return (
    <div className="flex items-center justify-between flex-wrap gap-4">
      <div className="flex items-center gap-2">
        <span className="text-sm text-text-secondary">Synthetic Rows:</span>
        <div className="flex items-center gap-1.5">
          {PRESETS.map((preset) => (
            <button
              key={preset}
              onClick={() => onRowCountChange(preset)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer ${
                rowCount === preset
                  ? "bg-accent text-white shadow-md shadow-accent/20"
                  : "bg-surface border border-border text-text-secondary hover:text-foreground hover:border-border-hover"
              }`}
            >
              {preset >= 1000 ? `${preset / 1000}K` : preset}
            </button>
          ))}
        </div>
        <input
          type="number"
          value={rowCount}
          onChange={(e) =>
            onRowCountChange(Math.max(1, parseInt(e.target.value) || 1))
          }
          min={1}
          max={1000000}
          className="w-24 px-3 py-1.5 rounded-lg bg-surface border border-border text-sm text-foreground outline-none focus:border-accent transition-colors"
          id="row-count-input"
        />
      </div>

      <button
        onClick={onProcessRequest}
        disabled={disabled || isWorking}
        className="group relative px-6 py-2.5 rounded-xl bg-gradient-to-r from-accent to-purple-500 text-white text-sm font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-accent/25 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed cursor-pointer"
        id="process-button"
      >
        <div className="flex items-center gap-2">
          {analyzing ? (
            <>
              <svg className="w-4 h-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
                <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" className="opacity-75" />
              </svg>
              DataScout AI Searching Online Datasets...
            </>
          ) : loading ? (
            <>
              <svg className="w-4 h-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
                <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" className="opacity-75" />
              </svg>
              Generating Synthetic Dataset...
            </>
          ) : (
            <>
              <svg className="w-4 h-4 transition-transform group-hover:rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Find Public or Generate Synthetic Data
            </>
          )}
        </div>
      </button>
    </div>
  );
}

