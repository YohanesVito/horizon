"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowUpRight,
  Database,
  FlaskConical,
  Save,
  SlidersHorizontal,
} from "lucide-react";
import type { EChartsOption } from "echarts";
import { api, dt, money, pct, tradingDayText } from "@/lib/api";
import type {
  Evidence,
  FinancialLogic,
  IntelligenceData,
  ScenarioInput,
  ScenarioRun,
} from "@/lib/intelligence-types";
import Chart from "./chart";
import MoneyInput from "./money-input";

const sessions = (value: number | null) =>
  value === null ? "Belum tercapai" : `${value} hari bursa`;
const interval = (value: [number, number] | null) =>
  value ? `${pct(value[0])} – ${pct(value[1])}` : "Belum tersedia";

export default function Intelligence({
  initialSymbol = "BBCA",
  onPlan,
}: {
  initialSymbol?: string;
  onPlan?: () => void;
}) {
  const client = useQueryClient();
  const [symbol, setSymbol] = useState(initialSymbol);
  const [tab, setTab] = useState<"evidence" | "scenario">("evidence");
  const [message, setMessage] = useState("");
  const query = useQuery({
    queryKey: ["intelligence"],
    queryFn: () => api<IntelligenceData>("/intelligence"),
  });
  const save = useMutation({
    mutationFn: (rules: FinancialLogic) =>
      api<IntelligenceData>("/intelligence/rules", {
        method: "PUT",
        body: JSON.stringify(rules),
      }),
    onSuccess: (value) => {
      client.setQueryData(["intelligence"], value);
      setMessage(
        "Logika tersimpan. Ranking dan statistik sudah dihitung ulang.",
      );
    },
  });
  const data = query.data;
  if (!data)
    return (
      <div
        className="glass intelligence-panel"
        role={query.isError ? "alert" : "status"}
      >
        {query.isError
          ? query.error.message
          : "Membaca histori dan menghitung bukti…"}
        {query.isError && (
          <button className="btn subtle" onClick={() => query.refetch()}>
            Coba lagi
          </button>
        )}
      </div>
    );
  const company =
    data.companies.find((c) => c.symbol === symbol) ?? data.companies[0];
  return (
    <div className="intelligence">
      <div className="intelligence-tabs" aria-label="Area Intelligence">
        <button
          className={`btn ${tab === "evidence" ? "primary" : "subtle"}`}
          aria-pressed={tab === "evidence"}
          onClick={() => setTab("evidence")}
        >
          <Database size={15} /> Bukti & ranking
        </button>
        <button
          className={`btn ${tab === "scenario" ? "primary" : "subtle"}`}
          aria-pressed={tab === "scenario"}
          onClick={() => setTab("scenario")}
        >
          <FlaskConical size={15} /> Skenario modal
        </button>
        <span className="badge">Eksploratif · 2022–2025</span>
        {onPlan && (
          <button className="btn subtle" onClick={onPlan}>
            Rencanakan dengan logika ini <ArrowUpRight size={15} />
          </button>
        )}
      </div>
      {tab === "evidence" ? (
        <>
          <section className="metrics" aria-label="Cakupan data">
            {[
              [
                "Event ditemukan",
                data.audit.events,
                `${data.audit.symbols} emiten terpilih`,
              ],
              [
                "Pengamatan lengkap",
                data.audit.complete,
                `Entry −${data.entry_offset} cum · t${data.horizon} setelah ex`,
              ],
              [
                "Dikarantina",
                data.audit.excluded,
                "Alasan per event bisa ditelusuri",
              ],
              [
                "Tersensor lebih awal",
                data.audit.eligible - data.audit.complete,
                "Belum mencapai horizon observasi",
              ],
            ].map(([label, value, note]) => (
              <div className="metric glass" key={String(label)}>
                <span className="muted tiny">{label}</span>
                <strong>{value}</strong>
                <small>{note}</small>
              </div>
            ))}
          </section>
          <details className="glass intelligence-panel logic-editor">
            <summary>
              <SlidersHorizontal size={17} /> Logika finansial tim{" "}
              <span className="muted">{data.rules.name}</span>
            </summary>
            <form
              key={data.rules.saved_at ?? "initial"}
              onSubmit={(e) => {
                e.preventDefault();
                setMessage("");
                const f = new FormData(e.currentTarget);
                save.mutate({
                  name: String(f.get("name")),
                  entry_offset: Number(
                    f.get("entry_offset"),
                  ) as FinancialLogic["entry_offset"],
                  horizon: Number(
                    f.get("horizon"),
                  ) as FinancialLogic["horizon"],
                  objective: String(
                    f.get("objective"),
                  ) as FinancialLogic["objective"],
                  minimum_samples: Number(f.get("minimum_samples")),
                  maximum_loss_upper_pct: Number(
                    f.get("maximum_loss_upper_pct"),
                  ),
                  minimum_median_return_pct: Number(
                    f.get("minimum_median_return_pct"),
                  ),
                });
              }}
            >
              <div className="form-grid">
                <label>
                  Nama logika
                  <input
                    name="name"
                    defaultValue={data.rules.name}
                    maxLength={80}
                    required
                  />
                </label>
                <label>
                  Prioritas ranking
                  <select name="objective" defaultValue={data.rules.objective}>
                    <option value="return">Median return tertinggi</option>
                    <option value="worst_return">
                      Return terburuk paling tinggi
                    </option>
                    <option value="risk">Frekuensi rugi terendah</option>
                    <option value="recovery">Median BEP harga tercepat</option>
                  </select>
                </label>
                <label>
                  Entry sebelum cum (hari bursa)
                  <select
                    name="entry_offset"
                    defaultValue={data.rules.entry_offset}
                  >
                    {[0, 5, 10].map((n) => (
                      <option key={n} value={n}>
                        {n} hari bursa
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Horizon setelah ex (hari bursa)
                  <select name="horizon" defaultValue={data.rules.horizon}>
                    {[5, 10, 20].map((n) => (
                      <option key={n} value={n}>
                        {n} hari bursa
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Minimum event lengkap
                  <input
                    name="minimum_samples"
                    type="number"
                    min={1}
                    max={100}
                    required
                    defaultValue={data.rules.minimum_samples}
                  />
                </label>
                <label>
                  Batas atas interval risiko rugi maksimum (%)
                  <input
                    name="maximum_loss_upper_pct"
                    type="number"
                    min={0}
                    max={100}
                    step="any"
                    required
                    defaultValue={data.rules.maximum_loss_upper_pct}
                  />
                </label>
                <label>
                  Median return minimum (%)
                  <input
                    name="minimum_median_return_pct"
                    type="number"
                    min={-100}
                    max={1000}
                    step="any"
                    required
                    defaultValue={data.rules.minimum_median_return_pct}
                  />
                </label>
              </div>
              <p className="muted tiny">
                Filter memakai batas atas Wilson 95%. Minimum sampel adalah
                aturan tim; lolos filter tidak berarti model prediksi
                tervalidasi.
              </p>
              <button className="btn primary" disabled={save.isPending}>
                <Save size={15} />{" "}
                {save.isPending ? "Menghitung…" : "Simpan & hitung ulang"}
              </button>
            </form>
          </details>
          {save.isError && (
            <div className="notice error" role="alert">
              {save.error.message}
            </div>
          )}
          {message && (
            <div className="notice success" role="status">
              {message}
            </div>
          )}
          <section className="glass intelligence-panel">
            <div className="section-head">
              <div>
                <h2>Ranking berdasarkan aturanmu</h2>
              </div>
              <span className="badge">{data.ranking.ranked.length} lolos</span>
            </div>
            <p className="muted tiny">
              Return = perubahan harga + satu dividen, di luar
              biaya/pajak/slippage. Urutan ini merangkum sampel historis, bukan
              prediksi keuntungan.
            </p>
            {data.ranking.ranked.length ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Emiten</th>
                      <th>n lengkap</th>
                      <th>Median return</th>
                      <th>Return terburuk</th>
                      <th>Rugi / interval 95%</th>
                      <th>Median BEP harga</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.ranking.ranked.map((row) => (
                      <tr
                        key={row.symbol}
                        className={
                          symbol === row.symbol ? "evidence-selected" : ""
                        }
                      >
                        <td>
                          <button
                            className="text-button"
                            onClick={() => setSymbol(row.symbol)}
                            aria-label={`Lihat bukti ${row.symbol}`}
                          >
                            <span className="muted">{row.rank}.</span>{" "}
                            {row.symbol}
                          </button>
                        </td>
                        <td>{row.complete_events}</td>
                        <td>{pct(row.median_return_pct)}</td>
                        <td>{pct(row.worst_return_pct)}</td>
                        <td>
                          {pct(row.trap_pct)}
                          <small className="cell-note">
                            {interval(row.trap_interval)}
                          </small>
                        </td>
                        <td>{sessions(row.median_recovery_sessions)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty">
                <h3>Tidak ada emiten yang lolos</h3>
                <p>
                  Periksa alasan di bawah atau ubah aturan tim. Hasil kosong
                  tetap merupakan hasil screening.
                </p>
              </div>
            )}
            <details className="audit-details">
              <summary>
                {data.ranking.excluded.length} emiten di luar aturan
              </summary>
              <ul>
                {data.ranking.excluded.map((row) => (
                  <li key={row.symbol}>
                    <button
                      className="text-button"
                      onClick={() => setSymbol(row.symbol)}
                    >
                      {row.symbol}
                    </button>{" "}
                    — {tradingDayText(row.reasons.join("; "))}
                  </li>
                ))}
              </ul>
            </details>
          </section>
          <section className="glass intelligence-panel">
            <div className="section-head">
              <div>
                <h2>Bukti per emiten</h2>
              </div>
              <label className="issuer-select">
                Emiten
                <select
                  aria-label="Emiten untuk bukti historis"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                >
                  {data.companies.map((c) => (
                    <option key={c.symbol}>{c.symbol}</option>
                  ))}
                </select>
              </label>
            </div>
            <EvidencePanel company={company} horizon={data.horizon} />
            <button className="btn subtle" onClick={() => setTab("scenario")}>
              Uji skenario {company.symbol} <ArrowUpRight size={15} />
            </button>
          </section>
          <details className="glass intelligence-panel audit-details">
            <summary>Metode, batas data & provenance</summary>
            <ul>
              {data.limitations.map((s) => (
                <li key={s}>{tradingDayText(s)}</li>
              ))}
            </ul>
            <p className="muted tiny">
              Metode:{" "}
              <a
                className="text-button"
                href="https://itl.nist.gov/div898/handbook/apr/section2/apr215.htm"
                target="_blank"
                rel="noreferrer"
              >
                NIST Kaplan–Meier
              </a>{" "}
              ·{" "}
              <a
                className="text-button"
                href="https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html"
                target="_blank"
                rel="noreferrer"
              >
                Wilson score interval
              </a>
            </p>
            <p className="tiny break-anywhere">
              {data.version} · {data.dataset_version}
            </p>
            <div className="table-scroll source-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Snapshot Sectors</th>
                    <th>Diambil</th>
                    <th>Tool</th>
                  </tr>
                </thead>
                <tbody>
                  {data.sources.map((s) => (
                    <tr key={s.file}>
                      <td>
                        {s.file}
                        <small className="cell-note" title={s.sha256}>
                          SHA256 {s.sha256.slice(0, 16)}…
                        </small>
                      </td>
                      <td>{dt(s.retrieved_at, true)}</td>
                      <td>{s.tool}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      ) : (
        <ScenarioPanel data={data} initialSymbol={symbol} />
      )}
    </div>
  );
}

function EvidencePanel({
  company: c,
  horizon,
}: {
  company: Evidence;
  horizon: number;
}) {
  const option: EChartsOption = {
    animationDuration: 250,
    textStyle: { fontFamily: "Manrope", color: "#bdaebe" },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#271d29",
      textStyle: { color: "#fff" },
      valueFormatter: (v) => pct(Number(v)),
    },
    legend: { bottom: 0, textStyle: { color: "#bdaebe" } },
    grid: { left: 50, right: 18, top: 22, bottom: 60 },
    xAxis: {
      type: "category",
      data: c.price_recovery.curve.map((r) => `t${r.session}`),
      axisLabel: { color: "#a89aad" },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLabel: { formatter: "{value}%", color: "#b1a3b6" },
      splitLine: { lineStyle: { color: "#ffffff0b" } },
    },
    series: [
      {
        name: "BEP harga",
        data: c.price_recovery.curve.map((r) => r.recovery_pct),
        color: "#d69abb",
      },
      {
        name: "BEP total",
        data: c.total_recovery.curve.map((r) => r.recovery_pct),
        color: "#8cbaaf",
      },
    ].map((s) => ({
      name: s.name,
      type: "line",
      step: "end",
      data: s.data,
      showSymbol: false,
      lineStyle: { color: s.color },
      itemStyle: { color: s.color },
    })),
  };
  return (
    <>
      <p className="muted tiny">
        {c.symbol} ·{" "}
        {c.period
          ? `${dt(c.period[0], true)} – ${dt(c.period[1], true)}`
          : "Belum ada event layak"}{" "}
        · {c.eligible_events} event layak · {c.excluded_events} dikarantina
      </p>
      <div className="detail-stats evidence-stats">
        <div>
          <small>Rugi total pada t{horizon}</small>
          <strong>{pct(c.trap_pct)}</strong>
          <span>
            {c.losses} / {c.complete_events} event lengkap
          </span>
          <p className="tiny muted">Wilson 95%: {interval(c.trap_interval)}</p>
        </div>
        <div>
          <small>Median mencapai BEP harga</small>
          <strong>{sessions(c.price_recovery.median_sessions)}</strong>
          <span>{c.price_unrecovered} belum pulih saat observasi berakhir</span>
        </div>
        <div>
          <small>Median mencapai BEP total</small>
          <strong>{sessions(c.total_recovery.median_sessions)}</strong>
          <span>Harga + dividen mencapai nilai entry</span>
        </div>
      </div>
      <p className="notice">
        Belum ada probabilitas prediksi tervalidasi. Penurunan harga disebut
        trap di sini jika kerugian harga masih lebih besar daripada dividen pada
        t{horizon}. BEP yang pernah tersentuh dapat turun kembali.
      </p>
      <Chart
        option={option}
        label={`Kurva pemulihan Kaplan–Meier ${c.symbol}; BEP harga dan total dalam ${horizon} hari bursa`}
        height={255}
      />
      <p className="muted tiny">
        t0 = ex-date. Kurva = proporsi pemulihan KM; median kosong bila belum
        mencapai 50%. {c.early_censored} event berhenti sebelum t{horizon}.
        Belum pulih tetap masuk perhitungan.
      </p>
      <div className="temporal-grid">
        {c.temporal.map((t) => (
          <div key={t.period}>
            <small>{t.period}</small>
            <strong>{pct(t.trap_pct)}</strong>
            <span>rugi · n={t.n}</span>
          </div>
        ))}
        <p className="muted tiny">
          Perbandingan periode untuk diagnosis. Tahun 2025 sudah pernah dilihat
          dalam riset; ini bukan holdout bersih.
        </p>
      </div>
      <details className="audit-details">
        <summary>
          Telusuri {c.total_events} event dan alasan pengecualian
        </summary>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Ex-date</th>
                <th>Entry / DPS</th>
                <th>Return t{horizon}</th>
                <th>BEP harga / total</th>
                <th>Status & sumber</th>
              </tr>
            </thead>
            <tbody>
              {c.events.map((e) => (
                <tr key={e.id}>
                  <td>{dt(e.ex_date, true)}</td>
                  <td>
                    {money(e.entry_price)}
                    <small className="cell-note">DPS {money(e.dps)}</small>
                  </td>
                  <td>{pct(e.gross_return_pct)}</td>
                  <td>
                    {e.eligible
                      ? `${sessions(e.price_bep_session ?? null)} / ${sessions(e.total_bep_session ?? null)}`
                      : "—"}
                  </td>
                  <td className="audit-cell">
                    {!e.eligible
                      ? tradingDayText(e.reasons.join("; "))
                      : e.complete
                        ? "Lengkap"
                        : `Tersensor pada t${e.observed_sessions}`}
                    {e.warnings.map((w) => (
                      <small className="cell-note" key={w}>
                        {tradingDayText(w)}
                      </small>
                    ))}
                    <details>
                      <summary>Sumber</summary>
                      {e.sources.map((s) => (
                        <small className="cell-note" key={s}>
                          {s}
                        </small>
                      ))}
                    </details>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </>
  );
}

function ScenarioPanel({
  data,
  initialSymbol,
}: {
  data: IntelligenceData;
  initialSymbol: string;
}) {
  const client = useQueryClient();
  const [active, setActive] = useState<ScenarioRun | null>(null);
  const history = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => api<ScenarioRun[]>("/scenarios"),
  });
  const create = useMutation({
    mutationFn: (input: ScenarioInput) =>
      api<ScenarioRun>("/scenarios", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: (run) => {
      setActive(run);
      client.invalidateQueries({ queryKey: ["scenarios"] });
    },
  });
  return (
    <>
      <div className="notice">
        Stress test satu posisi dengan analog harga historis. Semua nominal dan
        tanggal di bawah adalah asumsi pengguna. Untuk rotasi, all-in, dan split
        dengan ledger kas/T+2, gunakan menu Simulator.
      </div>
      <div className="intelligence-scenario-grid">
        <section className="glass intelligence-panel">
          <h2>Input skenario</h2>
          <p className="muted tiny">
            Nilai awal hanya contoh hipotetis. Horizon analog: entry −
            {data.entry_offset} sebelum cum, valuasi t{data.horizon} setelah ex.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              const s = (key: string) => String(f.get(key));
              create.mutate({
                symbol: s("symbol"),
                capital: s("capital"),
                entry_price: s("entry_price"),
                dps: s("dps"),
                entry_date: s("entry_date"),
                cum_date: s("cum_date"),
                ex_date: s("ex_date"),
                recording_date: s("recording_date"),
                payment_date: s("payment_date"),
                valuation_date: s("valuation_date"),
                entry_offset: data.entry_offset,
                horizon: data.horizon,
              });
            }}
          >
            <div className="form-grid">
              <label>
                Emiten skenario
                <select name="symbol" defaultValue={initialSymbol}>
                  {data.companies.map((c) => (
                    <option key={c.symbol}>{c.symbol}</option>
                  ))}
                </select>
              </label>
              <label>
                Modal (Rp)
                <MoneyInput
                  name="capital"
                  min="1"
                  max="1000000000000"
                  step="any"
                  defaultValue="100000000"
                  required
                />
              </label>
              <label>
                Asumsi harga entry (Rp)
                <MoneyInput
                  name="entry_price"
                  min="0.0001"
                  max="10000000"
                  step="any"
                  defaultValue="10000"
                  required
                />
              </label>
              <label>
                Asumsi DPS (Rp)
                <MoneyInput
                  name="dps"
                  min="0"
                  max="10000000"
                  step="any"
                  defaultValue="250"
                  required
                />
              </label>
              {[
                ["entry_date", "Tanggal masuk asumsi", "2026-11-02"],
                ["cum_date", "Cum date asumsi", "2026-11-09"],
                ["ex_date", "Ex-date asumsi", "2026-11-10"],
                ["recording_date", "Recording asumsi", "2026-11-11"],
                ["payment_date", "Payment asumsi", "2026-12-10"],
                [
                  "valuation_date",
                  `Tanggal valuasi t${data.horizon} asumsi`,
                  "2026-12-08",
                ],
              ].map(([name, label, value]) => (
                <label key={name}>
                  {label}
                  <input
                    name={name}
                    type="date"
                    defaultValue={value}
                    required
                  />
                </label>
              ))}
            </div>
            <p className="muted tiny">
              Declaration belum tersedia. Tanggal valuasi mengasumsikan horizon
              hari bursa di atas; kalender bursa belum diverifikasi. Analisis
              hanya memakai analog yang berakhir sebelum tanggal masuk. Desimal
              memakai koma, misalnya 0,125.
            </p>
            <button className="btn primary" disabled={create.isPending}>
              <FlaskConical size={16} />{" "}
              {create.isPending ? "Menghitung…" : "Hitung skenario"}
            </button>
          </form>
          {create.isError && (
            <div className="notice error" role="alert">
              {create.error.message}
            </div>
          )}
        </section>
        <section className="glass intelligence-panel scenario-history">
          <h2>Skenario tersimpan</h2>
          <p className="muted tiny">
            Input dan hasil lama tetap disimpan dengan versinya.
          </p>
          {history.isPending && <p role="status">Memuat riwayat…</p>}
          {history.isError && (
            <p role="alert" className="notice error">
              {history.error.message}
            </p>
          )}
          {!history.isPending && !history.data?.length && !history.isError && (
            <p className="muted">Belum ada skenario.</p>
          )}
          {history.data?.map((run) => (
            <button
              className={`scenario-history-row ${active?.id === run.id ? "selected" : ""}`}
              key={run.id}
              onClick={() => setActive(run)}
            >
              <span>
                <strong>{run.input.symbol}</strong>
                <small>
                  {money(Number(run.input.capital), true)} · t
                  {run.input.horizon}
                </small>
              </span>
              <span>
                {money(run.result.pnl.median, true)}
                <small>median PnL sampel</small>
              </span>
            </button>
          ))}
        </section>
      </div>
      {active && <ScenarioResult run={active} />}
    </>
  );
}

function ScenarioResult({ run }: { run: ScenarioRun }) {
  const r = run.result;
  const trajectory: EChartsOption = {
    textStyle: { fontFamily: "Manrope", color: "#bdaebe" },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#271d29",
      textStyle: { color: "#fff" },
      valueFormatter: (v) => money(Number(v)),
    },
    legend: { bottom: 0, textStyle: { color: "#bdaebe" } },
    grid: { left: 68, right: 18, top: 20, bottom: 60 },
    xAxis: {
      type: "category",
      data: r.trajectory.map((t) => `t${t.session}`),
      axisLabel: { color: "#b1a3b6" },
    },
    yAxis: {
      type: "value",
      axisLabel: { formatter: (v: number) => money(v, true), color: "#b1a3b6" },
      splitLine: { lineStyle: { color: "#ffffff0b" } },
    },
    series: [
      { name: "P10", key: "p10", color: "#986e88" },
      { name: "Median", key: "median", color: "#e6afce" },
      { name: "P90", key: "p90", color: "#8cbaaf" },
    ].map((s) => ({
      name: s.name,
      type: "line",
      data: r.trajectory.map((t) => t[s.key as "p10" | "median" | "p90"]),
      showSymbol: false,
      lineStyle: { color: s.color },
      itemStyle: { color: s.color },
    })),
  };
  return (
    <section className="glass intelligence-panel" aria-label="Hasil skenario">
      <div className="section-head">
        <div>
          <h2>
            {r.symbol} · {r.analog_count} skenario harga
          </h2>
        </div>
        <span className="badge">Gross · bukan forecast</span>
      </div>
      <p className="muted tiny">
        Hasil tersimpan untuk modal {money(Number(run.input.capital))}, entry{" "}
        {money(Number(run.input.entry_price))}, DPS{" "}
        {money(Number(run.input.dps))}. {r.shares.toLocaleString("id-ID")} saham
        · sisa kas {money(r.uninvested_cash)}.
      </p>
      <div className="result-metrics">
        <div>
          <small>PnL terburuk dalam sampel</small>
          <strong>{money(r.pnl.worst, true)}</strong>
          <span>Bukan batas maksimum kerugian masa depan</span>
        </div>
        <div>
          <small>Median PnL sampel</small>
          <strong>{money(r.pnl.median, true)}</strong>
          <span>
            {r.loss_scenarios} dari {r.analog_count} skenario rugi
          </span>
        </div>
        <div>
          <small>P10 – P90 PnL sampel</small>
          <strong className="range-value">
            {money(r.pnl.p10, true)}
            <br />
            {money(r.pnl.p90, true)}
          </strong>
          <span>Kuantil analog, bukan interval prediksi</span>
        </div>
      </div>
      <div className="notice">
        Dividen tunai: {money(r.dividend_cash)} · piutang dividen:{" "}
        {money(r.dividend_receivable)}. BEP harga {money(r.price_bep)}; BEP
        total {money(r.total_bep)}. Nilai posisi belum menjadi kas siap rotasi.
      </div>
      <div className="scenario-dates">
        {[
          ["Masuk", run.input.entry_date],
          ["Cum", run.input.cum_date],
          ["Ex", run.input.ex_date],
          ["Recording", run.input.recording_date],
          ["Payment", run.input.payment_date],
          ["Valuasi", run.input.valuation_date],
        ].map(([label, value]) => (
          <span key={label}>
            <small>{label} asumsi</small>
            <strong>{dt(value, true)}</strong>
          </span>
        ))}
      </div>
      <h3>Perjalanan PnL skenario setelah ex</h3>
      <Chart
        option={trajectory}
        label={`Kuantil PnL sampel analog ${r.symbol} dari ex sampai t${run.input.horizon}`}
        height={270}
      />
      <p className="muted tiny">
        Kuantil per hari bursa, bukan jalur satu event atau interval prediksi.
        PnL terendah yang teramati sepanjang seluruh analog:{" "}
        {money(r.worst_observed_pnl)}.
      </p>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Analog ex-date</th>
              <th>Harga valuasi</th>
              <th>Perubahan modal</th>
              <th>Hak dividen</th>
              <th>PnL gross</th>
              <th>Nilai akhir</th>
            </tr>
          </thead>
          <tbody>
            {r.rows.map((row) => (
              <tr key={row.event_id}>
                <td>{dt(row.ex_date, true)}</td>
                <td>{money(row.exit_price)}</td>
                <td>{money(row.capital_gain)}</td>
                <td>{money(row.dividend)}</td>
                <td>
                  {money(row.gross_pnl)}
                  <small className="cell-note">
                    {pct(row.gross_return_pct)}
                  </small>
                </td>
                <td>{money(row.ending_value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <details className="audit-details">
        <summary>Asumsi dan versi hasil</summary>
        <ul>
          {r.assumptions.map((s) => (
            <li key={s}>{tradingDayText(s)}</li>
          ))}
        </ul>
        <p className="tiny break-anywhere">
          Run {run.id} · {r.version} · {r.dataset_version}
        </p>
      </details>
    </section>
  );
}
