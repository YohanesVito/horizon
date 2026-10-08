"use client";

import { useId, useState } from "react";
import { ChevronDown, Sparkles } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { aiProse } from "@/lib/ai-prose";
import { api, dt } from "@/lib/api";
import type { Allocation, Trade } from "@/lib/types";

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
  sections?: {
    event_id: string;
    symbol: string;
    cum_date: string | null;
    status: "completed" | "unavailable";
    summary: string | null;
    findings: { title: string; detail: string; source_ids: string[] }[];
  }[];
  sources: InsightSource[];
  limitations: string[];
  statistics: Record<string, unknown>;
  attempts: number;
  exhausted: boolean;
  configured?: boolean;
  provenance?: {
    holding_analysis_version?: number;
    date_grounding_version?: number;
    analysis_mode?: string;
  };
};

const MAX_STATUS_READS = 80;

type InsightProps = {
  simulationId: string;
  allocation: Allocation;
  trades?: Trade[];
  analysisMode?: string;
  eventId?: string;
};

export default function SimulationInsights(props: InsightProps) {
  if (props.eventId) {
    const trade = props.trades?.find((item) => item.event_id === props.eventId);
    if (!trade) return null;
    return <InsightAccordion {...props} trade={trade} />;
  }
  if (props.analysisMode !== "independent_events")
    return <InsightPanel {...props} />;
  const symbols = [
    ...new Set((props.trades ?? []).map((trade) => trade.symbol)),
  ];
  // All panels mount together: each ticker starts its own request and completes independently.
  return (
    <>
      {symbols.map((symbol) => (
        <InsightPanel
          key={`${props.simulationId}:${symbol}`}
          {...props}
          symbol={symbol}
          trades={(props.trades ?? []).filter(
            (trade) => trade.symbol === symbol,
          )}
        />
      ))}
    </>
  );
}

function InsightAccordion({
  trade,
  ...props
}: InsightProps & { trade: Trade }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className="event-insight-accordion">
      <button
        type="button"
        className="event-insight-toggle"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen(!open)}
      >
        <span className="event-insight-label">
          <span className="event-insight-icon" aria-hidden="true">
            <Sparkles size={18} strokeWidth={2} />
          </span>
          Ringkasan AI · {trade.symbol}
        </span>
        <ChevronDown className="event-insight-chevron" size={18} aria-hidden="true" />
      </button>
      <div id={id} hidden={!open}>
        <InsightPanel
          {...props}
          trades={[trade]}
          symbol={
            props.analysisMode === "independent_events"
              ? trade.symbol
              : undefined
          }
          embedded
        />
      </div>
    </div>
  );
}

function InsightPanel({
  simulationId,
  allocation,
  trades = [],
  analysisMode,
  symbol,
  embedded = false,
}: {
  simulationId: string;
  allocation: Allocation;
  trades?: Trade[];
  analysisMode?: string;
  symbol?: string;
  embedded?: boolean;
}) {
  const client = useQueryClient();
  const queryKey = ["simulation-insights", simulationId, symbol ?? "legacy"];
  const insight = useQuery({
    queryKey,
    queryFn: () => {
      const current = client.getQueryData<SimulationInsight>(queryKey);
      return api<SimulationInsight>(
        `/simulations/${encodeURIComponent(simulationId)}/insights${symbol ? `?symbol=${encodeURIComponent(symbol)}` : ""}`,
        current?.status === "processing"
          ? undefined
          : {
              method: "POST",
              body: JSON.stringify({
                allocation,
                ...(symbol ? { symbol } : {}),
              }),
            },
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
  if (data?.status === "unavailable" && data.exhausted && !symbol) return null;

  return (
    <section
      className={
        embedded
          ? "simulation-insights event-insight-content"
          : "glass pad result-route simulation-insights"
      }
      aria-label={`Ringkasan AI analisis historis${symbol ? ` ${symbol}` : ""}`}
      aria-busy={insight.isFetching}
    >
      {!embedded && (
        <div className="section-head">
          <div>
            <span className="sim-section-label">
              RINGKASAN AI{symbol ? ` · ${symbol}` : ""}
            </span>
            <h3>
              {symbol
                ? `${symbol}: yang perlu kamu perhatikan.`
                : "Yang perlu kamu perhatikan."}
            </h3>
            <p className="small muted">
              {analysisMode === "independent_events"
                ? "Rentang nilai posisi sampai dua hari bursa setelah payment; setiap peristiwa memakai seluruh modal secara independen."
                : "Ringkasan hasil strategi simulasi tersimpan."}{" "}
              Di luar biaya transaksi, pajak, dan slippage.
            </p>
          </div>
        </div>
      )}
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
          {!embedded &&
            trades
              .filter((trade) => trade.shares > 0 && trade.observation)
              .map((trade) => (
                <p className="small muted" key={trade.event_id}>
                  {trade.symbol} · Cum {dt(trade.observation!.cum_date, true)} ·
                  Ex {dt(trade.observation!.ex_date, true)} · Payment{" "}
                  {dt(trade.observation!.payment_date, true)}
                </p>
              ))}
          {data.status === "completed" &&
            !data.provenance?.holding_analysis_version && (
              <p className="small muted">
                Ringkasan tersimpan ini membahas strategi simulasi; belum
                mencakup rentang nilai posisi sampai dua hari bursa setelah
                payment.
              </p>
            )}
          {data.status === "completed" &&
            !data.provenance?.date_grounding_version && (
              <p className="small muted">
                Tanggal peristiwa mengacu pada data di kartu; narasi AI lama
                belum melalui pembaruan acuan tanggal.
              </p>
            )}
          {analysisMode === "independent_events" && (
            <div className="insight-findings">
              {!data.sections && data.status === "completed" && (
                <p className="small muted">
                  Ringkasan tersimpan ini masih memakai format lama; section per
                  peristiwa belum tersedia.
                </p>
              )}
              {trades.map((trade) => {
                const section = data.sections?.find(
                  (item) => item.event_id === trade.event_id,
                );
                return (
                  <article key={trade.event_id}>
                    {!embedded && (
                      <h4>
                        {trade.symbol} · Cum{" "}
                        {dt(
                          trade.observation?.cum_date ?? trade.entry_date,
                          true,
                        )}
                      </h4>
                    )}
                    <p>
                      {aiProse(section?.summary ||
                        (data.exhausted
                          ? "Ringkasan AI ticker ini gagal setelah tiga percobaan. Analisis angka tetap tersedia."
                          : "Ringkasan AI peristiwa ini belum tersedia."))}
                    </p>
                    {section?.findings.map((finding, index) => (
                      <div key={index}>
                        <h5>{aiProse(finding.title)}</h5>
                        <p>{aiProse(finding.detail)}</p>

                      </div>
                    ))}
                  </article>
                );
              })}
            </div>
          )}
          {(analysisMode !== "independent_events" ||
            (!embedded && !data.sections)) && (
            <p className="insight-summary">
              {aiProse((data.configured === false
                ? "Analisis AI belum tersedia untuk replay ini."
                : data.summary) ||
                "Ringkasan AI belum tersedia untuk hasil ini.")}
            </p>
          )}
          {analysisMode !== "independent_events" &&
            data.findings.length > 0 && (
              <div className="insight-findings">
                {data.findings.map((finding, index) => (
                  <article key={`${index}-${aiProse(finding.title)}`}>
                    <h4>{aiProse(finding.title)}</h4>
                    <p>{aiProse(finding.detail)}</p>

                  </article>
                ))}
              </div>
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
