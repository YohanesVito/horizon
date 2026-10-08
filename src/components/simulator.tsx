"use client";
import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowUpRight,
  Check,
  ChevronDown,
  Clock3,
  Copy,
  Play,
  Route,
} from "lucide-react";
import { api, dt, money, pct, tradingDayText } from "@/lib/api";
import type {
  Allocation,
  Catalog,
  Replay,
  Run,
  SimInput,
  Trade,
} from "@/lib/types";
import Chart, { lineOption } from "./chart";
import MoneyInput from "./money-input";
import SimulationInsights from "./simulation-insights";
const labels: Record<Allocation, string> = {
  single: "All-in pertama",
  equal: "Bagi rata",
  rotation: "Rotasi modal",
};
const exitLabels: Record<SimInput["exit_rule"], string> = {
  price_bep: "Setelah sinyal BEP harga",
  ex_close: "Close ex-date",
  payment_close: "Close payment date",
  holding_period: "Batas hari bursa pengamatan",
};
type SimulationDraft = Omit<SimInput, "capital"> & { capital: string };
function inputSignature(input: SimInput | SimulationDraft, startDate?: string) {
  return JSON.stringify([
    Number(input.capital),
    [...input.event_ids].sort(),
    input.allocation,
    input.compare,
    input.timing_mode ?? "custom",
    ...(input.timing_mode === "payment_plus_2"
      ? []
      : [
          input.entry_sessions_before_cum,
          input.exit_rule,
          input.max_holding_sessions,
          input.start_date ?? startDate,
          input.end_date,
        ]),
  ]);
}
export default function Simulator({
  catalog,
  initialEventId,
}: {
  catalog: Catalog;
  initialEventId?: string;
}) {
  const events = catalog.events.filter((e) => e.replay_available);
  const initialEvent = events.find((e) => e.id === initialEventId);
  const [input, setInput] = useState<SimulationDraft>({
    capital: "",
    timing_mode: "payment_plus_2",
    event_ids: initialEvent
      ? [initialEvent.id]
      : events
          .filter((e) =>
            ["BBCA:2025-03-21", "BMRI:2025-04-14", "LPPF:2025-04-22"].includes(
              e.id,
            ),
          )
          .map((e) => e.id),
    allocation: "rotation",
    entry_sessions_before_cum: 5,
    exit_rule: "price_bep",
    max_holding_sessions: 20,
    end_date: initialEvent
      ? (catalog.meta.replay_end ?? "2025-12-31")
      : "2025-05-20",
    start_date: initialEvent
      ? (catalog.meta.replay_start ?? "2025-01-01")
      : "2025-03-01",
    compare: true,
  });
  const [jobId, setJobId] = useState<string | null>(null),
    [chosen, setChosen] = useState<Allocation>("rotation");
  const [copiedFrom, setCopiedFrom] = useState<string | null>(null);
  const [capitalResetKey, setCapitalResetKey] = useState(0);
  const [showAllHistory, setShowAllHistory] = useState(false);
  const capitalField = useRef<HTMLInputElement>(null);
  const client = useQueryClient();
  const run = useQuery({
    queryKey: ["run", jobId],
    queryFn: () => api<Run>(`/simulations/${jobId}`),
    enabled: !!jobId,
    refetchInterval: (q) =>
      q.state.status === "error" ||
      (q.state.data && ["completed", "failed"].includes(q.state.data.status))
        ? false
        : 500,
  });
  const history = useQuery({
    queryKey: ["runs"],
    queryFn: () => api<Run[]>("/simulations"),
    refetchInterval: (q) =>
      q.state.data?.some((r) => r.status === "running" || r.status === "queued")
        ? 1500
        : false,
  });
  const visibleHistory = history.data?.filter((r) => r.status !== "failed");
  const submit = useMutation({
    mutationFn: (
      body: Pick<
        SimInput,
        "capital" | "event_ids" | "allocation" | "compare" | "timing_mode"
      >,
    ) =>
      api<Run>("/simulations", { method: "POST", body: JSON.stringify(body) }),
    onSuccess: (r) => {
      setJobId(r.id);
      setChosen(r.input.allocation);
      client.invalidateQueries({ queryKey: ["runs"] });
    },
  });
  const busy =
    submit.isPending ||
    (!!jobId &&
      (!run.data || ["queued", "running"].includes(run.data.status)) &&
      !run.isError);
  const result = run.data?.result;
  const selected =
    result?.alternatives.find((r) => r.allocation === chosen) ??
    result?.primary;
  const draftDiffers = result
    ? inputSignature(input) !==
      inputSignature(result.input, result.primary.start_date)
    : false;
  const unavailableEvents =
    result?.input.event_ids.filter(
      (id) => !events.some((event) => event.id === id),
    ) ?? [];
  const set = <K extends keyof SimulationDraft>(
    key: K,
    value: SimulationDraft[K],
  ) => setInput({ ...input, [key]: value });
  const chooseAllocation = (allocation: Allocation) => {
    setInput((current) => ({
      ...current,
      allocation,
      event_ids:
        allocation === "single"
          ? current.event_ids.slice(0, 1)
          : current.event_ids,
    }));
  };
  const toggle = (id: string) =>
    set(
      "event_ids",
      input.event_ids.includes(id)
        ? input.event_ids.filter((e) => e !== id)
        : input.allocation === "single"
          ? [id]
          : [...input.event_ids, id],
    );
  return (
    <div className="simulator">
      <div className="sim-setup">
        <section
          className="glass pad sim-form-panel"
          aria-labelledby="sim-form-title"
        >
          <div className="sim-panel-heading">
            <span className="sim-section-label">01 / ATUR SKENARIO</span>
            <h2 id="sim-form-title">Bangun skenario replay.</h2>
          </div>
          {initialEvent && (
            <p className="notice">
              Peristiwa terpilih:{" "}
              <strong>
                {initialEvent.symbol} · ex {dt(initialEvent.ex_date, true)}
              </strong>
              . Periode pengamatan mengikuti jadwal dividen secara otomatis.
            </p>
          )}
          {copiedFrom && (
            <p className="notice" role="status">
              Draf disalin dari hasil {copiedFrom.slice(0, 8)}. Hasil asal tidak
              berubah. Replay baru memakai harga masuk rata-rata 5 hari bursa
              dan pengamatan payment +2 hari bursa.
            </p>
          )}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = new FormData(e.currentTarget);
              const next = {
                ...input,
                event_ids:
                  input.allocation === "single"
                    ? input.event_ids.slice(0, 1)
                    : [...input.event_ids],
                timing_mode: "payment_plus_2" as const,
                capital: String(form.get("capital")),
              };
              setInput(next);
              submit.mutate({
                capital: Number(next.capital),
                event_ids: next.event_ids,
                allocation: next.allocation,
                compare: next.compare,
                timing_mode: "payment_plus_2",
              });
            }}
          >
            <div className="sim-step sim-step-first">
              <div className="sim-step-heading">
                <span className="sim-step-number">01</span>
                <div>
                  <h3>Tentukan modal awal</h3>
                  <p>Berapa dana yang ingin kamu uji?</p>
                </div>
              </div>
              <div className="form-grid">
                <label className="sim-capital-field">
                  Modal awal (Rp)
                  <MoneyInput
                    inputRef={capitalField}
                    resetKey={capitalResetKey}
                    name="capital"
                    required
                    min="1"
                    max="1000000000000"
                    step="1"
                    placeholder="Masukkan modal"
                    value={input.capital}
                    onValueChange={(value) => set("capital", value)}
                  />
                </label>
              </div>
            </div>
            <div className="sim-step">
              <div className="sim-step-heading">
                <span className="sim-step-number">02</span>
                <div>
                  <h3>Pilih strategi alokasi</h3>
                  <p>Tentukan cara modal bergerak di antara event.</p>
                </div>
              </div>
              <fieldset className="strategy-picker">
                <legend>Strategi utama</legend>
                <div className="strategy-cards">
                  {(
                    [
                      [
                        "single",
                        "Seluruh modal pada event dengan cum date pertama.",
                      ],
                      ["equal", "Porsi modal tetap untuk setiap event."],
                      [
                        "rotation",
                        "Kas yang tersedia dipakai untuk event berikutnya.",
                      ],
                    ] as const
                  ).map(([mode, explanation]) => (
                    <label
                      className={`strategy-card ${input.allocation === mode ? "selected" : ""}`}
                      key={mode}
                    >
                      <span className="strategy-choice">
                        <input
                          type="radio"
                          name="allocation"
                          value={mode}
                          checked={input.allocation === mode}
                          onChange={() => chooseAllocation(mode)}
                        />
                        <strong>{labels[mode]}</strong>
                      </span>
                      <span>{explanation}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
            </div>
            <div className="sim-step">
              <div className="sim-step-heading">
                <span className="sim-step-number">03</span>
                <div>
                  <h3>Pilih peristiwa</h3>
                  <p>
                    {input.allocation === "single"
                      ? "Strategi all-in pertama hanya memakai satu event."
                      : "Pilih event historis yang ingin diuji, maksimal 10."}
                  </p>
                </div>
              </div>
              <fieldset className="sim-event-fieldset">
                <legend>
                  Event terpilih{" "}
                  <span className="muted">
                    · {input.event_ids.length}/
                    {input.allocation === "single" ? 1 : 10}
                  </span>
                </legend>
                <div className="event-picker">
                  {events.map((e) => (
                    <label
                      className={`event-option ${input.event_ids.includes(e.id) ? "checked" : ""}`}
                      key={e.id}
                    >
                      <input
                        type="checkbox"
                        checked={input.event_ids.includes(e.id)}
                        disabled={
                          !input.event_ids.includes(e.id) &&
                          input.allocation !== "single" &&
                          input.event_ids.length >= 10
                        }
                        onChange={() => toggle(e.id)}
                      />
                      <span>
                        <strong>{e.symbol}</strong>
                        <small>Ex {dt(e.ex_date)}</small>
                      </span>
                      <span className="event-dps">
                        {money(e.dps)}
                        <small>/ saham</small>
                      </span>
                      {input.event_ids.includes(e.id) && <Check size={16} />}
                    </label>
                  ))}
                </div>
              </fieldset>
            </div>
            <p className="small muted sim-auto-method">
              Harga masuk memakai rata-rata harga penutupan 5 hari bursa sebelum
              cum-date (tidak termasuk cum-date), sebagai harga referensi
              simulasi. Jumlah saham mengikuti lot 100 saham. Pengamatan sampai
              2 hari bursa setelah payment, lalu penjualan simulasi pada harga
              penutupan. Periode ditentukan otomatis dari peristiwa terpilih;
              data yang belum lengkap ditandai parsial. Ini bukan transaksi
              nyata atau strategi beli bertahap.
            </p>
            <button
              className="btn primary full sim-submit"
              disabled={busy || !input.event_ids.length}
              type="submit"
            >
              {busy ? (
                <>
                  <span className="spinner" /> Menghitung simulasi…
                </>
              ) : (
                <>
                  <Play size={16} /> Lihat hasil replay
                </>
              )}
            </button>
            <p className="sim-note">
              Replay historis, bukan proyeksi. Hasil di luar biaya transaksi,
              pajak, dan slippage.
            </p>
          </form>
        </section>
        <aside className="glass pad history-panel">
          <span className="sim-section-label">ARSIP</span>
          <h2>Riwayat replay</h2>
          {history.isError ? (
            <div className="notice error">Riwayat belum dapat dimuat.</div>
          ) : history.isPending ? (
            <p className="muted">Memuat…</p>
          ) : !visibleHistory?.length ? (
            <div className="empty compact">
              <Clock3 size={25} />
              <p>
                Simulasi pertamamu
                <br />
                akan muncul di sini.
              </p>
            </div>
          ) : (
            <div className="run-list">
              {(showAllHistory
                ? visibleHistory
                : visibleHistory.slice(0, 6)
              ).map((r) => (
                <button
                  className={jobId === r.id ? "active" : ""}
                  key={r.id}
                  aria-label={`Buka hasil ${r.id.slice(0, 8)}`}
                  aria-pressed={jobId === r.id}
                  aria-current={jobId === r.id ? "true" : undefined}
                  onClick={() => {
                    setJobId(r.id);
                    setChosen(r.input.allocation);
                  }}
                >
                  <span>
                    <strong>{labels[r.input.allocation]}</strong>
                    <small>
                      {money(r.input.capital, true)} ·{" "}
                      {r.input.event_ids.length} event
                    </small>
                    <small>
                      {[
                        ...new Set(
                          r.input.event_ids.map((id) => id.split(":")[0]),
                        ),
                      ].join(", ")}
                    </small>
                    <small>
                      s.d. {dt(r.input.end_date, true)} · {r.id.slice(0, 8)}
                    </small>
                  </span>
                  <span
                    className={`status ${r.status === "completed" ? "ready" : ""}`}
                  >
                    {r.status === "completed"
                      ? "Selesai"
                      : r.status === "failed"
                        ? "Gagal"
                        : "Proses"}
                  </span>
                </button>
              ))}
            </div>
          )}
          {!!visibleHistory && visibleHistory.length > 6 && (
            <button
              className="btn subtle full"
              aria-expanded={showAllHistory}
              onClick={() => setShowAllHistory(!showAllHistory)}
            >
              {showAllHistory
                ? "Tampilkan 6 terbaru"
                : `Lihat semua (${visibleHistory.length})`}
            </button>
          )}
          <div className="history-foot">
            <span className="small-dot" />
            Hasil lama tetap mengikuti input lamanya.
          </div>
        </aside>
      </div>
      {(submit.isError || run.isError || run.data?.status === "failed") && (
        <div className="notice error" role="alert">
          {tradingDayText(
            submit.error?.message ??
              run.error?.message ??
              run.data?.error ??
              "",
          )}
        </div>
      )}
      {selected && result && (
        <section className="results">
          <div className="sim-results-intro">
            <span className="sim-section-label">02 / HASIL REPLAY</span>
            <h2>Apa yang terjadi dengan modal?</h2>
            <p>
              {dt(result.primary.start_date, true)} –{" "}
              {dt(result.input.end_date, true)} · Historis, sebelum biaya dan
              pajak.
            </p>
          </div>
          {draftDiffers && (
            <p className="notice sim-draft-warning" role="status">
              Form sekarang berbeda. Hasil ini tetap memakai aturan yang
              tersimpan saat replay dijalankan.
            </p>
          )}
          <div className="sim-results-heading">
            <span className="sim-section-label">PERBANDINGAN ALOKASI</span>
            <p>Pilih strategi untuk melihat rinciannya.</p>
          </div>
          <div className="comparison-grid">
            {result.alternatives.map((r) => (
              <button
                className={`glass comparison ${chosen === r.allocation ? "selected" : ""}`}
                key={r.allocation}
                onClick={() => setChosen(r.allocation)}
                aria-pressed={chosen === r.allocation}
              >
                <div className="spread">
                  <span>{labels[r.allocation]}</span>
                  {chosen === r.allocation ? (
                    <Check size={17} />
                  ) : (
                    <ArrowUpRight size={17} />
                  )}
                </div>
                <strong className={r.gross_pnl >= 0 ? "positive" : "negative"}>
                  {r.gross_pnl > 0 ? "+" : ""}
                  {money(r.gross_pnl)}
                </strong>
                <small>{pct(r.return_pct)} return total</small>
                <div className="comparison-footer">
                  <span>Drawdown {pct(r.max_drawdown_pct)}</span>
                  <span>
                    {r.trades.filter((t) => t.shares > 0).length} posisi dalam simulasi
                  </span>
                </div>
              </button>
            ))}
          </div>
          <ResultView
            replay={selected}
            alternatives={result.alternatives}
            showAssumptions={false}
            simulationAllocation={result.input.allocation}
            simulationId={
              run.data?.status === "completed" ? run.data.id : undefined
            }
          />
          <details
            className="glass result-disclosure run-snapshot"
            aria-label="Input asli hasil"
          >
            <summary>
              <span className="disclosure-title">
                Aturan yang dipakai pada hasil ini
              </span>
              <small>ID {run.data?.id.slice(0, 8)}</small>
              <ChevronDown size={18} aria-hidden="true" />
            </summary>
            <div className="disclosure-content">
              <div className="run-snapshot-actions">
                <button
                  className="btn subtle"
                  disabled={busy || unavailableEvents.length > 0}
                  onClick={() => {
                    setInput({
                      ...result.input,
                      capital: String(result.input.capital),
                      timing_mode: "payment_plus_2",
                      event_ids:
                        result.input.allocation === "single"
                          ? result.input.event_ids.slice(0, 1)
                          : [...result.input.event_ids],
                      start_date:
                        result.input.start_date ?? result.primary.start_date,
                    });
                    setCopiedFrom(run.data!.id);
                    setCapitalResetKey((revision) => revision + 1);
                    capitalField.current?.focus({ preventScroll: true });
                    capitalField.current?.scrollIntoView({ block: "center" });
                  }}
                >
                  <Copy size={15} /> Gunakan input hasil ini
                </button>
              </div>
              <dl className="run-input-grid">
                <div>
                  <dt>Modal awal</dt>
                  <dd>{money(result.input.capital)}</dd>
                </div>
                <div>
                  <dt>Aturan masuk</dt>
                  <dd>
                    {result.input.timing_mode === "payment_plus_2"
                      ? "Rata-rata 5 close sebelum cum-date"
                      : result.input.entry_sessions_before_cum === 0
                        ? "Close pada cum date"
                        : `${result.input.entry_sessions_before_cum} hari bursa sebelum cum date`}
                  </dd>
                </div>
                <div>
                  <dt>Aturan keluar</dt>
                  <dd>
                    {result.input.timing_mode === "payment_plus_2"
                      ? "Close payment +2 hari bursa"
                      : exitLabels[result.input.exit_rule]}
                  </dd>
                </div>
                <div>
                  <dt>Periode pengamatan</dt>
                  <dd>
                    {result.input.timing_mode === "payment_plus_2"
                      ? "Otomatis mengikuti jadwal dividen"
                      : `${result.input.max_holding_sessions} hari bursa setelah ex-date`}
                  </dd>
                </div>
                <div>
                  <dt>Strategi utama</dt>
                  <dd>{labels[result.input.allocation]}</dd>
                </div>
                <div>
                  <dt>Perbandingan alokasi</dt>
                  <dd>
                    {result.input.compare
                      ? "Tiga strategi"
                      : "Strategi utama saja"}
                  </dd>
                </div>
              </dl>
              <div className="run-events">
                <p className="small muted">
                  Event yang dipilih (tanggal ex-dividen)
                </p>
                <ul>
                  {result.input.event_ids.map((id) => {
                    const event = catalog.events.find((e) => e.id === id);
                    return (
                      <li key={id}>
                        {event
                          ? `${event.symbol} · ${dt(event.ex_date, true)}`
                          : id}
                      </li>
                    );
                  })}
                </ul>
              </div>
              <p className="tiny muted run-version">
                Engine {result.primary.rules_version} · Data{" "}
                {result.primary.dataset_version ??
                  run.data?.dataset_version ??
                  "Versi tidak tercatat"}
                . Simulasi baru memakai engine dan dataset aktif.
              </p>
              {unavailableEvents.length > 0 && (
                <p className="notice">
                  Input belum bisa disalin: event {unavailableEvents.join(", ")}{" "}
                  tidak tersedia untuk replay pada dataset aktif.
                </p>
              )}
            </div>
          </details>
          <ReplayAssumptions replay={selected} />
        </section>
      )}
      {!selected && !busy && (
        <div className="glass sim-empty">
          <Route size={32} aria-hidden="true" />
          <div>
            <span className="sim-section-label">HASIL REPLAY</span>
            <h2>Hasilnya akan muncul di sini.</h2>
            <p className="muted">
              Atur modal dan peristiwa, lalu jalankan replay.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
export function ResultView({
  replay: r,
  alternatives,
  simulationId,
  showAssumptions = true,
  simulationAllocation,
}: {
  replay: Replay;
  alternatives: Replay[];
  simulationId?: string;
  showAssumptions?: boolean;
  simulationAllocation?: Allocation;
}) {
  const dates = [
    ...new Set(alternatives.flatMap((a) => a.curve.map((c) => c.date))),
  ].sort();
  const colors = ["#FF4713", "#66B2BF", "#D9AF59"];
  return (
    <>
      <div className="glass pad result-chart">
        <div className="section-head">
          <div>
            <span className="sim-section-label">LINTASAN MODAL</span>
            <h3>Bagaimana nilainya bergerak?</h3>
            <p className="small muted">
              Nilai portofolio historis: kas, saham, dan piutang.
            </p>
          </div>
          <div className="chart-legend">
            {alternatives.map((a, i) => (
              <span key={a.allocation}>
                <i style={{ background: colors[i] }} />
                {labels[a.allocation]}
              </span>
            ))}
          </div>
        </div>
        <Chart
          label="Perbandingan nilai portofolio tiga strategi historis"
          height={380}
          option={lineOption(
            dates,
            alternatives.map((a, i) => ({
              name: labels[a.allocation],
              color: colors[i],
              values: dates.map(
                (d) =>
                  a.curve.filter((p) => p.date <= d).at(-1)?.nav ?? a.capital,
              ),
            })),
          )}
        />
      </div>
      <div className="result-metrics">
        <div className="glass pad">
          <small>Nilai akhir</small>
          <strong>{money(r.ending_nav)}</strong>
          <span>Termasuk saham dan piutang</span>
        </div>
        <div className="glass pad">
          <small>Hak dividen</small>
          <strong>{money(r.dividends)}</strong>
          <span>Belum dibayar: {money(r.pending_dividends)}</span>
        </div>
        <div className="glass pad">
          <small>Kas tersedia</small>
          <strong>{money(r.ending_cash)}</strong>
          <span>Piutang jual: {money(r.pending_sales)}</span>
        </div>
      </div>
      {simulationId && (
        <SimulationInsights
          simulationId={simulationId}
          trades={r.trades}
          allocation={simulationAllocation ?? r.allocation}
        />
      )}
      <section className="glass pad result-route">
        <div className="section-head">
          <div>
            <span className="sim-section-label">
              PERGERAKAN SEKITAR DIVIDEN
            </span>
            <h3>
              {labels[r.allocation]}: bagaimana jika posisi tetap dipegang?
            </h3>
            <p className="small muted">
              Pengamatan historis dari cum-date sampai 2 hari bursa setelah
              payment. Skenario posisi ini terpisah dari aturan keluar replay.
            </p>
          </div>
        </div>
        <div className="route-list">
          {r.trades.map((t, i) => (
            <PositionObservationCard key={t.event_id} trade={t} index={i} />
          ))}
        </div>
      </section>
      <details className="glass result-disclosure cash-flow-disclosure">
        <summary>
          <span className="disclosure-title">Rincian arus kas & dividen</span>
          <small>{r.ledger.length} aktivitas</small>
          <ChevronDown size={18} aria-hidden="true" />
        </summary>
        <div className="disclosure-content">
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Tanggal</th>
                  <th>Aktivitas</th>
                  <th>Emiten</th>
                  <th>Jumlah</th>
                  <th>Catatan</th>
                </tr>
              </thead>
              <tbody>
                {r.ledger.map((l, i) => (
                  <tr key={i}>
                    <td>{dt(l.date, true)}</td>
                    <td>{l.kind}</td>
                    <td>{l.symbol}</td>
                    <td>{money(l.amount)}</td>
                    <td className="ledger-detail">
                      {tradingDayText(l.detail)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </details>
      {showAssumptions && <ReplayAssumptions replay={r} />}
    </>
  );
}

function ReplayAssumptions({ replay: r }: { replay: Replay }) {
  return (
    <details className="glass result-disclosure assumptions">
      <summary>
        <span className="disclosure-title">Asumsi dan batas hasil ini</span>
        <ChevronDown size={18} aria-hidden="true" />
      </summary>
      <div className="disclosure-content">
        <ul>
          {r.assumptions.map((s) => (
            <li key={s}>{tradingDayText(s)}</li>
          ))}
        </ul>
        <p>
          Angka kerugian historis bukan probabilitas trap. Strategi terbaik pada
          replay ini belum tentu terbaik di masa depan.
        </p>
      </div>
    </details>
  );
}

function PositionObservationCard({
  trade: t,
  index,
}: {
  trade: Trade;
  index: number;
}) {
  const averageEntry = t.entry_price_basis === "prior5_close_mean";
  const referenceDates = t.entry_reference_dates ?? [];
  const o = t.observation;
  const points = o?.points ?? [];
  const option = lineOption(
    points.map((p) => p.date),
    [
      {
        name: "Harga penutupan",
        values: points.map((p) => p.close),
        color: "#FF4713",
      },
      {
        name: "Tertinggi harian",
        values: points.map((p) => p.high),
        color: "#397d60",
      },
      {
        name: "Terendah harian",
        values: points.map((p) => p.low),
        color: "#66B2BF",
      },
    ],
  );
  return (
    <div className="route-step observation-step">
      <div className="route-index">{String(index + 1).padStart(2, "0")}</div>
      <div className="route-body">
        <h3>{t.symbol}</h3>
        <div className="observation-entry">
          <div>
            <span>
              {averageEntry ? "Rentang harga masuk" : "Tanggal masuk"}
            </span>
            <strong>
              {averageEntry && referenceDates.length
                ? `${dt(referenceDates[0], true)} — ${dt(referenceDates.at(-1), true)}`
                : dt(t.entry_date, true)}
            </strong>
            {averageEntry && (
              <small>
                Rata-rata 5 hari bursa · pencatatan simulasi pada cum-date{" "}
                {dt(t.entry_date, true)}
              </small>
            )}
          </div>
          <div>
            <span>
              {averageEntry ? "Harga masuk rata-rata" : "Harga beli per saham"}
            </span>
            <strong>{money(t.entry_price)}</strong>
          </div>
          <div>
            <span>Jumlah</span>
            <strong>{(t.shares / 100).toLocaleString("id-ID")} lot</strong>
            <small>{t.shares.toLocaleString("id-ID")} saham</small>
          </div>
          <div>
            <span>Modal posisi</span>
            <strong>{money(o?.invested ?? t.entry_price * t.shares)}</strong>
          </div>
        </div>
        {!o ? (
          <p className="notice">
            Analisis rentang harga belum tersedia untuk replay ini. Jalankan
            replay baru untuk melihat pengamatan sampai payment +2 hari bursa.
          </p>
        ) : (
          <>
            <div className="observation-window">
              <strong>
                {dt(o.cum_date, true)} —{" "}
                {o.end_date
                  ? dt(o.end_date, true)
                  : "Akhir rentang belum tersedia"}
              </strong>
              <span>Cum-date → payment +2 hari bursa</span>
              <span>Payment {dt(o.payment_date, true)}</span>
            </div>
            {!o.complete && (
              <p className="notice">
                Data pengamatan parsial
                {o.available_end_date
                  ? `, tersedia sampai ${dt(o.available_end_date, true)}`
                  : ""}
                . Nilai tertinggi dan terendah hanya berdasarkan data yang
                tersedia.
              </p>
            )}
            {points.length ? (
              <>
                <div className="chart-legend observation-legend">
                  <span>
                    <i style={{ background: "#FF4713" }} />
                    Penutupan
                  </span>
                  <span>
                    <i style={{ background: "#397d60" }} />
                    Tertinggi harian
                  </span>
                  <span>
                    <i style={{ background: "#66B2BF" }} />
                    Terendah harian
                  </span>
                </div>
                <Chart
                  label={`Pergerakan harga ${t.symbol} dari cum-date hingga dua hari bursa setelah payment`}
                  height={280}
                  option={option}
                />
                <div className="observation-extremes">
                  {(
                    [
                      ["Nilai posisi tertinggi", o.highest],
                      ["Nilai posisi terendah", o.lowest],
                    ] as const
                  ).map(([label, extreme]) => (
                    <div key={label}>
                      <span>{label}</span>
                      <strong>
                        {extreme
                          ? money(extreme.total_value)
                          : "Belum tersedia"}
                      </strong>
                      {extreme && (
                        <>
                          <p>
                            {dt(extreme.date, true)} · harga{" "}
                            {money(extreme.price)} / saham
                          </p>
                          <p
                            className={
                              extreme.pnl >= 0 ? "positive" : "negative"
                            }
                          >
                            Laba/rugi {money(extreme.pnl)} (
                            {pct(extreme.return_pct)})
                          </p>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="muted">
                Harga harian untuk rentang ini belum tersedia.
              </p>
            )}
            <p className="small muted observation-basis">
              Nilai posisi = jumlah saham × harga tertinggi/terendah harian +
              dividen {money(o.dividend_amount)}. Mengasumsikan posisi tetap
              dipegang hingga berhak menerima dividen; sebelum payment, dividen
              belum berupa kas. Tidak termasuk sisa kas di luar posisi. Harga
              ekstrem historis bukan jaminan harga transaksi.{" "}
              {averageEntry
                ? "Harga masuk adalah referensi rata-rata 5 close, bukan harga transaksi pada satu tanggal."
                : "Harga tertinggi pada cum-date dapat terjadi sebelum harga masuk penutupan."}
            </p>
            <p className="small muted">
              Di luar biaya transaksi, pajak, dan slippage.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
