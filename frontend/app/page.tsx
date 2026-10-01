"use client";

import { useState, useCallback, useEffect } from "react";
import {
  generateFromPrompt,
  analyzeWithDataScout,
  GenerateResponse,
  DataScoutResponse,
  fetchDatasetData,
  analyzeGaps,
  fillGaps,
  FetchResult,
  GapAnalysis,
} from "./lib/api";
import Header from "./components/Header";
import PromptInput from "./components/PromptInput";
import ControlBar from "./components/ControlBar";
import DataTable from "./components/DataTable";
import ExportBar from "./components/ExportBar";
import EmptyState from "./components/EmptyState";
import Toast from "./components/Toast";
import LoadingSkeleton from "./components/LoadingSkeleton";
import DataScoutCard from "./components/DataScoutCard";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [rowCount, setRowCount] = useState(100);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [dataScoutAnalysis, setDataScoutAnalysis] = useState<DataScoutResponse | null>(null);
  const [data, setData] = useState<GenerateResponse | null>(null);
  const [generationTime, setGenerationTime] = useState<number | null>(null);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const [fetchResult, setFetchResult] = useState<FetchResult | null>(null);
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysis | null>(null);
  const [isFetching, setIsFetching] = useState(false);
  const [isFetchingMore, setIsFetchingMore] = useState(false);
  const [isFillingGaps, setIsFillingGaps] = useState(false);
  const [fetchSource, setFetchSource] = useState<{ platform: string; dataset_id: string; name: string } | null>(null);

  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (data) {
        e.preventDefault();
      }
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [data]);

  const showToast = useCallback(
    (message: string, type: "success" | "error") => {
      setToast({ message, type });
    },
    []
  );

  const handleGenerateSynthetic = useCallback(async () => {
    if (!prompt.trim()) {
      showToast("Please enter a dataset description", "error");
      return;
    }

    setLoading(true);
    setData(null);
    const startTime = Date.now();

    try {
      const result = await generateFromPrompt(prompt, rowCount);
      setData(result);
      setGenerationTime((Date.now() - startTime) / 1000);
      showToast(`Generated ${result.count} synthetic rows successfully`, "success");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Generation failed";
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [prompt, rowCount, showToast]);

  const handleProcessRequest = useCallback(async () => {
    if (!prompt.trim()) {
      showToast("Please enter a dataset description", "error");
      return;
    }

    setAnalyzing(true);
    setData(null);
    setDataScoutAnalysis(null);

    try {
      // Step 1: Automatic DataScout AI Online Search & Strategy Evaluation
      const analysis = await analyzeWithDataScout(prompt);
      setDataScoutAnalysis(analysis);

      // Check if existing public open datasets exist (HF / Kaggle / Public repos)
      // Only consider datasets that have a valid source_platform and dataset_id for fetching
      const fetchableDatasets = (analysis.existing_datasets || []).filter(
        ds => ds.source_platform && ds.source_platform !== "unknown" && ds.dataset_id
      );
      const hasExistingPublicData =
        fetchableDatasets.length > 0;

      if (hasExistingPublicData) {
        // Sort by quality × similarity (best first)
        const sortedDatasets = [...fetchableDatasets].sort(
          (a, b) => (b.quality_score * b.similarity_score) - (a.quality_score * a.similarity_score)
        );
        
        // Try fetching datasets in order until one succeeds
        setIsFetching(true);
        let fetchSucceeded = false;
        
        for (const best of sortedDatasets) {
          setFetchSource({ platform: best.source_platform, dataset_id: best.dataset_id, name: best.name });
          
          try {
            const fetched = await fetchDatasetData(best.source_platform, best.dataset_id, 100);
            
            if (fetched.rows.length > 0) {
              setFetchResult(fetched);
              setData({ rows: fetched.rows, count: fetched.count });
              showToast(`Loaded ${fetched.count} rows from ${best.name}`, "success");
              fetchSucceeded = true;
              
              // Analyze gaps
              try {
                const gaps = await analyzeGaps(prompt, fetched.columns);
                setGapAnalysis(gaps);
                
                // Auto-fill gaps if missing columns
                if (gaps.has_gaps && gaps.missing_columns.length > 0) {
                  setIsFillingGaps(true);
                  try {
                    const filled = await fillGaps(prompt, fetched.rows, gaps.missing_columns);
                    setData({ rows: filled.rows, count: filled.count });
                    showToast(`Added ${gaps.missing_columns.length} synthetic columns`, "success");
                  } catch {
                    showToast("Could not generate missing columns", "error");
                  } finally {
                    setIsFillingGaps(false);
                  }
                }
              } catch {
                // Gap analysis failed — data is still usable
              }
              break; // Success — stop trying other datasets
            } else if (fetched.requires_auth) {
              console.warn(`Dataset ${best.name} requires auth, trying next...`);
              continue; // Try next dataset
            } else {
              console.warn(`Dataset ${best.name} returned empty, trying next...`);
              continue; // Try next dataset
            }
          } catch (err) {
            console.warn(`Fetch failed for ${best.name}:`, err);
            continue; // Try next dataset
          }
        }
        
        setIsFetching(false);
        setAnalyzing(false);
        
        if (!fetchSucceeded) {
          showToast("Could not fetch any dataset. Generating synthetic data...", "error");
          await handleGenerateSynthetic();
        }
        return;
      }

      // AUTOMATIC PREFERENCE 2: No suitable public dataset found. Automatically fallback to synthetic generation!
      showToast("No suitable public dataset found online. Automatically generating synthetic dataset...", "success");
      setAnalyzing(false);
      await handleGenerateSynthetic();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Dataset processing failed";
      showToast(msg, "error");
      setAnalyzing(false);
    }
  }, [prompt, handleGenerateSynthetic, showToast]);

  const handleLoadMore = useCallback(async (desiredRows: number) => {
    if (!fetchSource) return;
    setIsFetchingMore(true);
    try {
      const fetched = await fetchDatasetData(fetchSource.platform, fetchSource.dataset_id, desiredRows);
      setFetchResult(fetched);
      
      if (fetched.rows.length > 0) {
        // Re-run gap filling if we had gaps
        if (gapAnalysis?.has_gaps && gapAnalysis.missing_columns.length > 0) {
          setIsFillingGaps(true);
          try {
            const filled = await fillGaps(prompt, fetched.rows, gapAnalysis.missing_columns);
            setData({ rows: filled.rows, count: filled.count });
          } catch {
            setData({ rows: fetched.rows, count: fetched.count });
          } finally {
            setIsFillingGaps(false);
          }
        } else {
          setData({ rows: fetched.rows, count: fetched.count });
        }
        showToast(`Loaded ${fetched.count} rows`, "success");
      }
    } catch {
      showToast("Failed to load more rows", "error");
    } finally {
      setIsFetchingMore(false);
    }
  }, [fetchSource, gapAnalysis, prompt, showToast]);

  const handleExampleClick = useCallback((example: string) => {
    setPrompt(example);
    setDataScoutAnalysis(null);
    setData(null);
    setFetchResult(null);
    setGapAnalysis(null);
    setFetchSource(null);
  }, []);

  const columns = data?.rows?.[0] ? Object.keys(data.rows[0]) : [];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
        <PromptInput
          value={prompt}
          onChange={(val) => {
            setPrompt(val);
            setDataScoutAnalysis(null);
            setFetchResult(null);
            setGapAnalysis(null);
            setFetchSource(null);
          }}
          onExampleClick={handleExampleClick}
          disabled={loading || analyzing}
        />

        <ControlBar
          rowCount={rowCount}
          onRowCountChange={setRowCount}
          onProcessRequest={handleProcessRequest}
          loading={loading}
          analyzing={analyzing}
          disabled={!prompt.trim()}
        />



        {dataScoutAnalysis && (
          <DataScoutCard
            analysis={dataScoutAnalysis}
            onProceedSynthetic={handleGenerateSynthetic}
            isGenerating={loading}
            fetchResult={fetchResult}
            gapAnalysis={gapAnalysis}
            isFetching={isFetching}
            isFillingGaps={isFillingGaps}
            onLoadMore={handleLoadMore}
            isFetchingMore={isFetchingMore}
            rowCount={rowCount}
          />
        )}

        {loading && <LoadingSkeleton />}

        {data && !loading && (
          <div className="animate-fade-in flex flex-col gap-4">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4 text-sm text-text-secondary">
                <span className="flex items-center gap-1.5 font-semibold text-foreground">
                  <span className="w-2 h-2 rounded-full bg-success" />
                  {data.count} rows generated
                </span>
                <span>·</span>
                <span>{columns.length} columns</span>
                {generationTime !== null && (
                  <>
                    <span>·</span>
                    <span>{generationTime.toFixed(1)}s</span>
                  </>
                )}
              </div>
              <ExportBar data={data.rows} onToast={showToast} />
            </div>
            <DataTable rows={data.rows} columns={columns} />
          </div>
        )}

        {!data && !loading && !dataScoutAnalysis && (
          <EmptyState onExampleClick={handleExampleClick} />
        )}
      </main>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
