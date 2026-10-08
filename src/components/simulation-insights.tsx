"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, dt } from "@/lib/api";
import type { Allocation } from "@/lib/types";

type InsightSource = {
  id: string;
  title: string;
  url: string;
  published_at: string | null;
};

type SimulationInsight = {
  status: "completed" | "unavailable" | "processing";
  summary: string;
  findings: { title: string; detail: string; source_ids: string[] }[];
  sources: InsightSource[];
  limitations: string[];
  statistics: Record<string, unknown>;
  attempts: number;
  exhausted: boolean;
  configured?: boolean;
};

const MAX_STATUS_READS = 80;

function safeSourceUrl(url: string): string | null {
  try {
    const parsed = new URL(url);
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : null;
  } catch {
    return null;
  }
}

export default function SimulationInsights({
  simulationId,
  allocation,
}: {
  simulationId: string;
  allocation: Allocation;
}) {
  const client = useQueryClient();
  const queryKey = ["simulation-insights", simulationId];
  const insight = useQuery({
    queryKey,
    queryFn: () => {
      const current = client.getQueryData<SimulationInsight>(queryKey);
      return api<SimulationInsight>(
        `/simulations/${encodeURIComponent(simulationId)}/insights`,
        current?.status === "processing"
          ? undefined
          : { method: "POST", body: JSON.stringify({ allocation }) },
      );
    },
    refetchInterval: (query) =>
      query.state.status !== "error" &&
      query.state.data?.status === "processing" &&
      query.state.dataUpdateCount < MAX_STATUS_READS
        ? 1500
        : false,
    staleTime: Infinity,
    gcTime: 30 * 60 * 1000,
    retry: false,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });
  const data = insight.data;
  const pollingPaused =
    data?.status === "processing" &&
    (client.getQueryState(queryKey)?.dataUpdateCount ?? 0) >= MAX_STATUS_READS;
  if (data?.status === "unavailable" && data.exhausted) return null;
  const sources =
    data?.sources.flatMap((source) => {
      const url = safeSourceUrl(source.url);
      return url ? [{ ...source, url }] : [];
    }) ?? [];

  return (
    <section
      className="glass pad result-route simulation-insights"
      aria-label="Ringkasan AI hasil simulasi"
      aria-busy={insight.isFetching}
    >
      <div className="section-head">
        <div>
          <span className="sim-section-label">RINGKASAN AI</span>
          <h3>Yang perlu kamu perhatikan.</h3>
          <p className="small muted">
            Hasil utama dan perbandingan strategi replay · di luar biaya
            transaksi, pajak, dan slippage.
          </p>
        </div>
      </div>
      {insight.isPending ||
      (!insight.isError && data?.status === "processing") ? (
        <p className="muted" role="status">
          Menyusun analisis…
          {pollingPaused && (
            <button
              type="button"
              className="btn secondary"
              onClick={() => void insight.refetch()}
            >
              Periksa status
            </button>
          )}
        </p>
      ) : insight.isError ? (
        <div role="status">
          <p className="muted">
            Ringkasan AI belum berhasil dimuat. Hasil replay tetap tersedia.
          </p>
          <button
            type="button"
            className="btn secondary"
            onClick={() => void insight.refetch()}
          >
            Periksa status
          </button>
        </div>
      ) : data ? (
        <div className="insight-content">
          <p className="insight-summary">
            {(data.configured === false
              ? "Analisis AI belum tersedia untuk replay ini."
              : data.summary) || "Ringkasan AI belum tersedia untuk hasil ini."}
          </p>
          {data.findings.length > 0 && (
            <div className="insight-findings">
              {data.findings.map((finding, index) => (
                <article key={`${index}-${finding.title}`}>
                  <h4>{finding.title}</h4>
                  <p>{finding.detail}</p>
                  {finding.source_ids.length > 0 && (
                    <div className="insight-links">
                      {sources
                        .filter((source) =>
                          finding.source_ids.includes(source.id),
                        )
                        .map((source) => (
                          <a
                            key={source.id}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {source.title} ↗
                          </a>
                        ))}
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
          {data.limitations.length > 0 && (
            <details className="insight-limitations small muted">
              <summary>Batas data dan analisis</summary>
              {data.limitations.map((limitation, index) => (
                <p key={index}>{limitation}</p>
              ))}
            </details>
          )}
          {sources.length > 0 && (
            <details className="insight-sources small">
              <summary>Sumber konteks ({sources.length})</summary>
              <ul>
                {sources.map((source) => (
                  <li key={source.id}>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {source.title} ↗
                    </a>
                    {source.published_at && (
                      <span className="muted">
                        {" "}
                        · {dt(source.published_at, true)}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </details>
          )}
          {data.status === "unavailable" && !data.exhausted && (
            <button
              type="button"
              className="btn secondary"
              onClick={() => void insight.refetch()}
            >
              Periksa status
            </button>
          )}
        </div>
      ) : null}
    </section>
  );
}
