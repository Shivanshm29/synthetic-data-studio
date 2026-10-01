"use client";

import { useCallback } from "react";

interface ExportBarProps {
  data: Record<string, unknown>[];
  onToast: (message: string, type: "success" | "error") => void;
}

export default function ExportBar({ data, onToast }: ExportBarProps) {
  const downloadCSV = useCallback(() => {
    if (!data.length) return;
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(","),
      ...data.map((row) =>
        headers
          .map((h) => {
            const val = String(row[h] ?? "");
            return val.includes(",") ||
              val.includes('"') ||
              val.includes("\n")
              ? `"${val.replace(/"/g, '""')}"`
              : val;
          })
          .join(",")
      ),
    ];
    const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "synthetic_data.csv";
    a.click();
    URL.revokeObjectURL(url);
    onToast("Downloaded CSV", "success");
  }, [data, onToast]);

  const downloadJSON = useCallback(() => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "synthetic_data.json";
    a.click();
    URL.revokeObjectURL(url);
    onToast("Downloaded JSON", "success");
  }, [data, onToast]);

  const downloadJSONL = useCallback(() => {
    const lines = data.map((row) => JSON.stringify(row)).join("\n");
    const blob = new Blob([lines], { type: "application/x-ndjson" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "synthetic_data.jsonl";
    a.click();
    URL.revokeObjectURL(url);
    onToast("Downloaded JSONL", "success");
  }, [data, onToast]);

  const downloadSQL = useCallback(() => {
    if (!data.length) return;
    const headers = Object.keys(data[0]);
    const tableName = "synthetic_dataset";
    const sqlStatements = data.map((row) => {
      const vals = headers.map((h) => {
        const v = row[h];
        if (v === null || v === undefined) return "NULL";
        if (typeof v === "number" || typeof v === "boolean") return String(v);
        return `'${String(v).replace(/'/g, "''")}'`;
      });
      return `INSERT INTO ${tableName} (${headers.join(", ")}) VALUES (${vals.join(", ")});`;
    });
    const blob = new Blob([sqlStatements.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "synthetic_data.sql";
    a.click();
    URL.revokeObjectURL(url);
    onToast("Downloaded SQL Inserts", "success");
  }, [data, onToast]);

  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      onToast("Copied to clipboard", "success");
    } catch {
      onToast("Failed to copy", "error");
    }
  }, [data, onToast]);

  const btnClass =
    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface border border-border text-xs text-text-secondary hover:text-foreground hover:border-accent/50 hover:bg-surface-hover transition-all cursor-pointer shadow-sm";

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <button onClick={copyToClipboard} className={btnClass} id="copy-button">
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Copy
      </button>
      <button onClick={downloadCSV} className={btnClass} id="csv-button">
        CSV
      </button>
      <button onClick={downloadJSON} className={btnClass} id="json-button">
        JSON
      </button>
      <button onClick={downloadJSONL} className={btnClass} id="jsonl-button">
        JSONL
      </button>
      <button onClick={downloadSQL} className={btnClass} id="sql-button">
        SQL
      </button>
    </div>
  );
}

