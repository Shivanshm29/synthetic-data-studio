"use client";

import { useState, useMemo } from "react";

interface DataTableProps {
  rows: Record<string, unknown>[];
  columns: string[];
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "\u2014";
  if (typeof value === "boolean") return value ? "True" : "False";
  if (typeof value === "number") {
    if (Number.isInteger(value)) return value.toLocaleString();
    return value.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
  return String(value);
}

function formatHeader(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function DataTable({ rows, columns }: DataTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [copiedCell, setCopiedCell] = useState<string | null>(null);

  const filteredRows = useMemo(() => {
    if (!searchTerm.trim()) return rows;
    const lower = searchTerm.toLowerCase();
    return rows.filter((row) =>
      columns.some((col) =>
        String(row[col] ?? "")
          .toLowerCase()
          .includes(lower)
      )
    );
  }, [rows, columns, searchTerm]);

  const handleCopyCell = (val: string, key: string) => {
    navigator.clipboard.writeText(val);
    setCopiedCell(key);
    setTimeout(() => setCopiedCell(null), 1500);
  };

  if (!rows.length) return null;

  return (
    <div className="glass rounded-xl overflow-hidden border border-border flex flex-col gap-0 shadow-2xl">
      {/* Table Filter Header */}
      <div className="px-5 py-3 border-b border-border bg-surface/40 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <div className="relative">
            <svg
              className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted"
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
            <input
              type="text"
              placeholder="Search dataset rows..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-1.5 rounded-lg bg-surface border border-border text-xs text-foreground placeholder-text-muted outline-none focus:border-accent w-64 transition-colors"
            />
          </div>
          {searchTerm && (
            <span className="text-xs text-text-muted">
              Matching {filteredRows.length} of {rows.length}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 text-xs text-text-muted">
          <span>Click any cell to copy value</span>
        </div>
      </div>

      <div className="overflow-x-auto max-h-[600px]">
        <table className="w-full text-sm" id="data-table">
          <thead className="sticky top-0 bg-surface/95 backdrop-blur z-10 border-b border-border">
            <tr>
              <th className="px-5 py-3 text-left text-xs font-semibold text-text-muted uppercase tracking-wider w-12">
                #
              </th>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-5 py-3 text-left text-xs font-semibold text-text-muted uppercase tracking-wider whitespace-nowrap"
                >
                  <div className="flex items-center gap-1.5">
                    <span>{formatHeader(col)}</span>
                    <span className="text-[10px] text-accent/70 lowercase font-mono font-normal">
                      ({col})
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredRows.map((row, i) => (
              <tr
                key={i}
                className="border-b border-border/30 hover:bg-surface-hover/60 transition-colors group"
              >
                <td className="px-5 py-3 text-text-muted font-mono text-xs select-none">
                  {i + 1}
                </td>
                {columns.map((col) => {
                  const rawVal = String(row[col] ?? "");
                  const cellKey = `${i}-${col}`;
                  const isCopied = copiedCell === cellKey;
                  return (
                    <td
                      key={col}
                      onClick={() => handleCopyCell(rawVal, cellKey)}
                      className="px-5 py-3 text-foreground whitespace-nowrap max-w-[320px] truncate cursor-pointer hover:text-accent transition-colors relative"
                      title={`${rawVal} (Click to copy)`}
                    >
                      {formatCell(row[col])}
                      {isCopied && (
                        <span className="ml-2 inline-flex items-center px-1.5 py-0.5 rounded bg-success/20 text-success text-[10px] font-semibold animate-fade-in">
                          Copied!
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
            {filteredRows.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length + 1}
                  className="px-5 py-8 text-center text-text-muted text-sm"
                >
                  No rows matched your search filter "{searchTerm}"
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="px-5 py-2 border-t border-border bg-surface/30 text-xs text-text-muted flex justify-between items-center">
        <span>Showing {filteredRows.length} rows</span>
        <span>{columns.length} columns defined</span>
      </div>
    </div>
  );
}
