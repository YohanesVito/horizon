"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  GitBranch,
  History,
  Play,
  SlidersHorizontal,
} from "lucide-react";
import { api, dt, money, pct, tradingDayText } from "@/lib/api";
import type { Catalog, Allocation } from "@/lib/types";
import type {
  FinancialLogic,
  IntelligenceData,
} from "@/lib/intelligence-types";
import type {
  Candidate,
  RotationInput,
  RotationPlan,
  RotationRun,
} from "@/lib/rotation-types";
import { ResultView } from "./simulator";
import MoneyInput from "./money-input";

const allocations: Record<Allocation, string> = {
  single: "All-in pertama",
  equal: "Bagi rata per event",
  rotation: "Rotasi kas",
};
const objectives: Record<FinancialLogic["objective"], string> = {
  return: "Median return tertinggi",
  worst_return: "Return terburuk paling baik",
  risk: "Frekuensi rugi terendah",
  recovery: "Median pulih tercepat",
};

export default function RotationPlanner({
  catalog,
  initialSymbols,
}: {
  catalog: Catalog;
  initialSymbols?: string[];
}) {
  const logic = useQuery({
    queryKey: ["intelligence"],
    queryFn: () => api<IntelligenceData>("/intelligence"),
  });
  if (!logic.data)
    return (
      <div className="glass pad" role={logic.isError ? "alert" : "status"}>
        {logic.isError ? logic.error.message : "Memuat logika finansial tim…"}
        {logic.isError && (
          <button className="btn subtle" onClick={() => logic.refetch()}>
            Coba lagi
          </button>
        )}
      </div>
    );
  return (
    <Planner
      catalog={catalog}
      initialSymbols={initialSymbols}
      logic={logic.data.rules}
    />
  );
}

function Planner({
  catalog,
  initialSymbols,
  logic,
}: {
  catalog: Catalog;
  initialSymbols?: string[];
  logic: FinancialLogic;
}) {
  const client = useQueryClient();
  const [input, setInput] = useState<RotationInput>({
    capital: 100000000,
    start_date: "2025-03-01",
    end_date: "2025-06-30",
    symbols: initialSymbols ?? catalog.companies.map((c) => c.symbol),
    rules: logic,
    exit_rule: "price_bep",
    max_holding_sessions: 20,
    max_events: 5,
    allow_calendar_assumption: true,
  });
  const [plan, setPlan] = useState<RotationPlan | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [routeId, setRouteId] = useState("");
  const [allocation, setAllocation] = useState<Allocation>("rotation");
  const plans = useQuery({
    queryKey: ["rotation-plans"],
    queryFn: () => api<RotationPlan[]>("/rotation-plans"),
  });
  const job = useQuery({
    queryKey: ["rotation-run", jobId],
    queryFn: () => api<RotationRun>(`/rotation-runs/${jobId}`),
    enabled: !!jobId,
    refetchInterval: (q) =>
      q.state.status === "error" ||
      (q.state.data && ["completed", "failed"].includes(q.state.data.status))
        ? false
        : 500,
  });
  const runs = useQuery({
    queryKey: ["rotation-runs"],
    queryFn: () => api<RotationRun[]>("/rotation-runs"),
    refetchInterval: (q) =>
      q.state.data?.some((r) => r.status === "running" || r.status === "queued")
        ? 1500
        : false,
  });
  const create = useMutation({
    mutationFn: (body: RotationInput) =>
      api<RotationPlan>("/rotation-plans", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    onSuccess: (p) => {
      setPlan(p);
      setJobId(null);
      setRouteId(p.routes[0]?.id ?? "");
      client.invalidateQueries({ queryKey: ["rotation-plans"] });
    },
  });
  const replay = useMutation({
    mutationFn: (id: string) =>
      api<RotationRun>(`/rotation-plans/${id}/replay`, { method: "POST" }),
    onSuccess: (r) => {
      setJobId(r.id);
      client.invalidateQueries({ queryKey: ["rotation-runs"] });
    },
  });
  const openHistory = useMutation({
    mutationFn: async (r: RotationRun) => ({
      run: r,
      plan: await api<RotationPlan>(`/rotation-plans/${r.plan_id}`),
    }),
    onSuccess: ({ run, plan: p }) => {
      setPlan(p);
      setInput(p.input);
      setJobId(run.id);
      setRouteId(p.routes[0]?.id ?? "");
    },
  });
  const set = <K extends keyof RotationInput>(
    key: K,
    value: RotationInput[K],
  ) => setInput((p) => ({ ...p, [key]: value }));
  const rule = <K extends keyof FinancialLogic>(
    key: K,
    value: FinancialLogic[K],
  ) => setInput((p) => ({ ...p, rules: { ...p.rules, [key]: value } }));
  const busy =
    replay.isPending ||
    (!!jobId &&
      !job.isError &&
      (!job.data || ["queued", "running"].includes(job.data.status)));
  const result = job.data?.result;
  const chosenRoute =
    result?.routes.find((r) => r.route_id === routeId) ?? result?.routes[0];
  const chosenReplay = chosenRoute?.comparison.alternatives.find(
    (r) => r.allocation === allocation,
  );
  const error =
    create.error ??
    replay.error ??
    openHistory.error ??
    job.error ??
    plans.error ??
    runs.error;
  return (
    <div className="rotation-workspace">
      <div className="rotation-intro glass pad">
        <div>
          <h2>Rute berdasarkan aturan tim</h2>
          <p className="muted small">
            Pilih periode historis. Screening hanya memakai pengamatan sebelum
            awal periode. Hasil replay dihitung setelah rute dibekukan.
          </p>
        </div>
        <span className="badge">Riset bersyarat · 2025</span>
      </div>
      <section className="glass pad">
        <div className="section-head">
          <div>
            <h2>Modal, waktu, dan aturan tim</h2>
          </div>
          <GitBranch className="accent" size={22} />
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const form = new FormData(e.currentTarget);
            const next = {
              ...input,
              capital: String(form.get("rotation-capital")),
              start_date: String(form.get("start_date")),
              end_date: String(form.get("end_date")),
            };
            setInput(next);
            create.mutate(next);
          }}
        >
          <div className="rotation-form-grid">
            <label>
              Modal awal (Rp)
              <MoneyInput
                name="rotation-capital"
                min="1"
                max="1000000000000"
                required
                value={input.capital}
                onValueChange={(value) => set("capital", value)}
              />
            </label>
            <label>
              Awal periode / tanggal keputusan
              <input
                type="date"
                name="start_date"
                min="2025-01-01"
                max="2025-12-30"
                required
                value={input.start_date}
                onInput={(e) => set("start_date", e.currentTarget.value)}
                onChange={(e) => set("start_date", e.target.value)}
              />
            </label>
            <label>
              Akhir periode
              <input
                type="date"
                name="end_date"
                min={input.start_date}
                max="2025-12-31"
                required
                value={input.end_date}
                onInput={(e) => set("end_date", e.currentTarget.value)}
                onChange={(e) => set("end_date", e.target.value)}
              />
            </label>
            <label>
              Aturan keluar
              <select
                value={input.exit_rule}
                onChange={(e) =>
                  set("exit_rule", e.target.value as RotationInput["exit_rule"])
                }
              >
                <option value="price_bep">Sinyal BEP → open berikutnya</option>
                <option value="ex_close">Close ex-date</option>
                <option value="payment_close">
                  Close payment / batas waktu
                </option>
                <option value="holding_period">
                  Batas hari bursa pengamatan
                </option>
              </select>
            </label>
            <label>
              Batas hari bursa setelah ex-date
              <input
                type="number"
                min="1"
                max="60"
                required
                value={input.max_holding_sessions}
                onChange={(e) =>
                  set("max_holding_sessions", Number(e.target.value))
                }
              />
            </label>
            <label>
              Maksimum event per rute
              <input
                type="number"
                min="1"
                max="10"
                required
                value={input.max_events}
                onChange={(e) => set("max_events", Number(e.target.value))}
              />
            </label>
          </div>
          <fieldset className="rotation-universe">
            <legend>Cakupan emiten · {input.symbols.length} dipilih</legend>
            <div className="rotation-chips">
              {catalog.companies.map((c) => (
                <label
                  className={`rotation-chip ${input.symbols.includes(c.symbol) ? "selected" : ""}`}
                  key={c.symbol}
                >
                  <input
                    type="checkbox"
                    checked={input.symbols.includes(c.symbol)}
                    onChange={() =>
                      set(
                        "symbols",
                        input.symbols.includes(c.symbol)
                          ? input.symbols.filter((s) => s !== c.symbol)
                          : [...input.symbols, c.symbol],
                      )
                    }
                  />
                  {c.symbol}
                </label>
              ))}
            </div>
            <p className="tiny muted">
              Pilihan emiten adalah input pengguna. Yield tahunan 2025 di
              Peluang tidak dipakai untuk menghitung ranking pada tanggal
              keputusan.
            </p>
          </fieldset>
          <details className="rotation-logic" open>
            <summary>
              <SlidersHorizontal size={16} /> Logika finansial rencana · salinan
              aturan Intelligence
            </summary>
            <div className="rotation-form-grid">
              <label>
                Prioritas ranking
                <select
                  value={input.rules.objective}
                  onChange={(e) =>
                    rule(
                      "objective",
                      e.target.value as FinancialLogic["objective"],
                    )
                  }
                >
                  {Object.entries(objectives).map(([k, v]) => (
                    <option key={k} value={k}>
                      {v}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Entry sebelum cum
                <select
                  value={input.rules.entry_offset}
                  onChange={(e) =>
                    rule(
                      "entry_offset",
                      Number(e.target.value) as FinancialLogic["entry_offset"],
                    )
                  }
                >
                  {[0, 5, 10].map((n) => (
                    <option key={n} value={n}>
                      {n} hari bursa
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Horizon statistik historis
                <select
                  value={input.rules.horizon}
                  onChange={(e) =>
                    rule(
                      "horizon",
                      Number(e.target.value) as FinancialLogic["horizon"],
                    )
                  }
                >
                  {[5, 10, 20].map((n) => (
                    <option key={n} value={n}>
                      t{n} setelah ex-date
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Sampel lengkap minimum
                <input
                  type="number"
                  min="1"
                  max="100"
                  required
                  value={input.rules.minimum_samples}
                  onChange={(e) =>
                    rule("minimum_samples", Number(e.target.value))
                  }
                />
              </label>
              <label>
                Batas atas Wilson rugi maks. (%)
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="any"
                  required
                  value={input.rules.maximum_loss_upper_pct}
                  onChange={(e) =>
                    rule("maximum_loss_upper_pct", Number(e.target.value))
                  }
                />
              </label>
              <label>
                Median return minimum (%)
                <input
                  type="number"
                  min="-100"
                  max="1000"
                  step="any"
                  required
                  value={input.rules.minimum_median_return_pct}
                  onChange={(e) =>
                    rule("minimum_median_return_pct", Number(e.target.value))
                  }
                />
              </label>
            </div>
            <p className="tiny muted">
              Statistik return memakai horizon di atas. Exit replay dapat
              berbeda. Mengubah aturan di sini hanya memengaruhi rencana baru.
            </p>
          </details>
          <label className="rotation-assumption">
            <input
              type="checkbox"
              checked={input.allow_calendar_assumption}
              onChange={(e) =>
                set("allow_calendar_assumption", e.target.checked)
              }
            />
            <span>
              Izinkan asumsi jadwal sudah diketahui
              <small>
                Timestamp pengumuman belum tersedia. Jika dimatikan, event tanpa
                bukti pengumuman dikeluarkan.
              </small>
            </span>
          </label>
          <div className="rotation-form-footer">
            <p className="tiny muted">
              Di luar biaya transaksi, pajak, dan slippage. Tidak mengeksekusi
              order.
            </p>
            <button
              className="btn primary"
              disabled={create.isPending || !input.symbols.length}
              type="submit"
            >
              {create.isPending ? "Menyusun kandidat…" : "Susun kandidat rute"}
              <ArrowRight size={16} />
            </button>
          </div>
        </form>
      </section>
      {error && (
        <div role="alert" className="notice error">
          {error.message}
        </div>
      )}
      {plan && (
        <>
          <section className="rotation-snapshot glass pad">
            <div className="section-head">
              <div>
                <h2>{plan.routes.length} kandidat rute</h2>
              </div>
              <span className="badge">
                {plan.candidates.length} event lolos · {plan.excluded.length}{" "}
                dikeluarkan
              </span>
            </div>
            <p className="small">
              Snapshot rencana:{" "}
              <strong>{money(Number(plan.input.capital))}</strong> ·{" "}
              {dt(plan.input.start_date, true)} –{" "}
              {dt(plan.input.end_date, true)}. Bukti hanya sebelum{" "}
              <strong>{dt(plan.decision_date, true)}</strong>.
            </p>
            <p className="tiny muted">
              Perubahan form tidak mengubah snapshot ini. Urutan rute ditentukan
              aturan, belum memakai hasil keuntungan replay.
            </p>
            {!plan.routes.length && (
              <div className="empty">
                <h3>Belum ada rute yang lolos</h3>
                <p>
                  Telusuri alasan di bawah, lalu ubah periode, cakupan emiten,
                  atau aturan.
                </p>
              </div>
            )}
            <div className="rotation-route-grid">
              {plan.routes.map((r, i) => (
                <article className="rotation-route" key={r.id}>
                  <div className="spread">
                    <span className="eyebrow">RUTE 0{i + 1}</span>
                    <span className="badge mini">{r.steps.length} event</span>
                  </div>
                  <h3>{r.name}</h3>
                  <ol>
                    {r.steps.map((s) => (
                      <li key={s.event_id}>
                        <div className="spread">
                          <strong>{s.symbol}</strong>
                          <span className="tiny">{dt(s.entry_date)}</span>
                        </div>
                        <p className="tiny muted">
                          Ex {dt(s.ex_date)} · batas kas model*{" "}
                          {dt(s.planned_cash_release)}
                        </p>
                      </li>
                    ))}
                  </ol>
                  <p className="tiny muted">
                    {r.omitted.length} kandidat tidak dimasukkan
                    {r.also_matches.length
                      ? ` · juga memenuhi: ${r.also_matches.join(", ")}`
                      : ""}
                  </p>
                  {!!r.omitted.length && (
                    <details>
                      <summary className="tiny">
                        Alasan tidak dimasukkan
                      </summary>
                      {r.omitted.map((o) => (
                        <p className="tiny muted" key={o.event_id}>
                          {o.event_id}: {tradingDayText(o.reason)}
                        </p>
                      ))}
                    </details>
                  )}
                </article>
              ))}
            </div>
            <p className="tiny muted">
              *Batas model dari ex + holding limit + T+2, atau exit terjadwal.
              Bukan ramalan kapan harga BEP. Rute “semua peluang” dapat memuat
              jadwal bertumpuk; kas yang tidak cukup menyebabkan event terlewat.
            </p>
            <details className="rotation-audit">
              <summary>Bukti pemilihan dan alasan pengecualian</summary>
              <CandidateTable rows={[...plan.candidates, ...plan.excluded]} />
            </details>
            <details className="rotation-audit">
              <summary>Aturan, sumber, dan batas rencana</summary>
              <p className="small">
                {objectives[plan.input.rules.objective]} · minimum{" "}
                {plan.input.rules.minimum_samples} event · entry −
                {plan.input.rules.entry_offset} cum · statistik t
                {plan.input.rules.horizon} · holding{" "}
                {plan.input.max_holding_sessions} hari bursa
              </p>
              <ul>
                {plan.assumptions.map((a) => (
                  <li className="small muted" key={a}>
                    {tradingDayText(a)}
                  </li>
                ))}
              </ul>
              <p className="tiny muted rotation-hash">
                {plan.version} · {plan.dataset_version} ·{" "}
                {plan.evidence_dataset_version} · ID {plan.id}
              </p>
            </details>
            <button
              className="btn primary"
              disabled={!plan.routes.length || busy}
              onClick={() => replay.mutate(plan.id)}
            >
              <Play size={16} />
              {busy
                ? "Menghitung seluruh perbandingan…"
                : "Uji semua rute × 3 strategi modal"}
            </button>
          </section>
        </>
      )}
      {job.data?.status === "failed" && (
        <div role="alert" className="notice error">
          {tradingDayText(job.data.error ?? "")}
        </div>
      )}
      {busy && (
        <div role="status" className="notice">
          Replay sedang berjalan. Snapshot input sudah disimpan.
        </div>
      )}
      {result && chosenRoute && chosenReplay && (
        <section className="rotation-results">
          <div className="glass pad">
            <h2>Hasil aktual pada replay historis</h2>
            <p className="small muted">
              {money(result.cash_baseline.capital)} ·{" "}
              {dt(result.cash_baseline.start_date, true)} –{" "}
              {dt(result.cash_baseline.end_date, true)}. Baseline tanpa
              transaksi: {money(result.cash_baseline.ending_nav)}, PnL Rp0,
              tanpa bunga.
            </p>
            <div className="table-scroll">
              <table className="rotation-comparison">
                <thead>
                  <tr>
                    <th>Rute / strategi</th>
                    <th>PnL gross</th>
                    <th>Drawdown</th>
                    <th>Modal tertahan*</th>
                    <th>Posisi terbuka / di bawah entry</th>
                    <th>Terlewat</th>
                    <th>Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {result.routes.flatMap((r) =>
                    r.comparison.alternatives.map((a) => (
                      <tr
                        key={`${r.route_id}-${a.allocation}`}
                        className={
                          r.route_id === chosenRoute.route_id &&
                          a.allocation === allocation
                            ? "selected-row"
                            : ""
                        }
                      >
                        <td>
                          <strong>{r.name}</strong>
                          <small>{allocations[a.allocation]}</small>
                        </td>
                        <td
                          className={a.gross_pnl >= 0 ? "positive" : "negative"}
                        >
                          {money(a.gross_pnl)}
                          <small>{pct(a.return_pct)}</small>
                        </td>
                        <td>{pct(a.max_drawdown_pct)}</td>
                        <td>
                          {Math.max(0, ...a.trades.map((t) => t.capital_days))}{" "}
                          hari
                        </td>
                        <td>
                          {
                            a.trades.filter((t) => t.status === "holding")
                              .length
                          }{" "}
                          / {a.open_below_entry ?? "—"}
                        </td>
                        <td>{a.missed_events?.length ?? 0}</td>
                        <td>
                          <button
                            className="btn subtle"
                            aria-label={`Lihat ${r.name}, ${allocations[a.allocation]}`}
                            onClick={() => {
                              setRouteId(r.route_id);
                              setAllocation(a.allocation);
                            }}
                          >
                            Lihat
                          </button>
                        </td>
                      </tr>
                    )),
                  )}
                </tbody>
              </table>
            </div>
            <p className="tiny muted">
              *Durasi terlama satu lot dari entry sampai kas hasil jual
              tersedia, atau akhir pengamatan bila belum tersedia. “Terlewat”
              berarti kas tidak cukup; all-in pertama sengaja hanya membeli
              event pertama. Posisi yang ditutup rugi sudah masuk PnL, bukan
              hitungan posisi terbuka.
            </p>
          </div>
          <div className="rotation-selected">
            <span className="badge">Detail dipilih</span>
            <h3>
              {chosenRoute.name} · {allocations[chosenReplay.allocation]}
            </h3>
          </div>
          <ResultView
            key={`${chosenRoute.route_id}-${allocation}-${jobId}`}
            replay={chosenReplay}
            alternatives={chosenRoute.comparison.alternatives}
          />
        </section>
      )}
      <details className="glass pad rotation-history">
        <summary>
          <History size={16} /> Rencana & replay tersimpan
        </summary>
        <div className="rotation-history-grid">
          <div>
            <h3>Rencana terakhir</h3>
            {plans.data?.length === 0 && (
              <p className="small muted">Belum ada rencana.</p>
            )}
            {plans.data?.slice(0, 8).map((p) => (
              <button
                className="scenario-history-row"
                key={p.id}
                onClick={() => {
                  setPlan(p);
                  setInput(p.input);
                  setJobId(null);
                  setRouteId(p.routes[0]?.id ?? "");
                }}
              >
                <span>
                  {money(Number(p.input.capital))} · {p.routes.length} rute
                  <small>
                    {dt(p.input.start_date)} – {dt(p.input.end_date)} ·{" "}
                    {p.id.slice(0, 8)}
                  </small>
                </span>
                <ArrowRight size={16} />
              </button>
            ))}
          </div>
          <div>
            <h3>Replay terakhir</h3>
            {runs.data?.length === 0 && (
              <p className="small muted">Belum ada replay.</p>
            )}
            {runs.data?.slice(0, 8).map((r) => (
              <button
                className="scenario-history-row"
                key={r.id}
                disabled={openHistory.isPending}
                onClick={() => openHistory.mutate(r)}
              >
                <span>
                  {money(Number(r.input.capital))} · {r.status}
                  <small>
                    {dt(r.input.start_date)} – {dt(r.input.end_date)} ·{" "}
                    {r.id.slice(0, 8)}
                  </small>
                </span>
                <ArrowRight size={16} />
              </button>
            ))}
          </div>
        </div>
      </details>
    </div>
  );
}

function CandidateTable({ rows }: { rows: Candidate[] }) {
  if (!rows.length)
    return (
      <p className="small muted">
        Tidak ada event untuk emiten dan periode ini.
      </p>
    );
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Event</th>
            <th>Hasil screening</th>
            <th>Sampel sebelum keputusan</th>
            <th>Median return</th>
            <th>Rugi historis / Wilson 95%</th>
            <th>Audit bukti</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.event_id}>
              <td>
                <strong>{c.symbol}</strong>
                <small>Ex {dt(c.ex_date)}</small>
                <small>
                  Jadwal{" "}
                  {c.calendar_status === "assumed"
                    ? "diasumsikan diketahui"
                    : c.calendar_status === "verified"
                      ? "terverifikasi"
                      : "belum terverifikasi"}
                </small>
              </td>
              <td className="rotation-reason">
                {c.reasons.length
                  ? tradingDayText(c.reasons.join(" · "))
                  : `Lolos · ranking ${c.evidence?.rank}`}
              </td>
              <td>
                {c.evidence?.complete_events ?? c.evidence_event_ids.length}
              </td>
              <td>{pct(c.evidence?.median_return_pct)}</td>
              <td>
                {pct(c.evidence?.trap_pct)}
                <small>
                  {c.evidence?.trap_interval?.map((v) => pct(v)).join(" – ") ??
                    "—"}
                </small>
              </td>
              <td>
                <details>
                  <summary>Telusuri</summary>
                  <p className="tiny">
                    Observasi terakhir {dt(c.evidence_latest_observation, true)}
                  </p>
                  {c.evidence_event_ids.map((id) => (
                    <p className="tiny" key={id}>
                      {id}
                    </p>
                  ))}
                </details>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
