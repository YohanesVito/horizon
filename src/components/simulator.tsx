"use client";
import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  Clock3,
  Copy,
  History,
  Play,
  Route,
} from "lucide-react";
import { api, dt, money, pct } from "@/lib/api";
import type { Allocation, Catalog, Replay, Run, SimInput } from "@/lib/types";
import Chart, { lineOption } from "./chart";
const labels: Record<Allocation, string> = {
  single: "All-in pertama",
  equal: "Bagi rata",
  rotation: "Rotasi modal",
};
const exitLabels: Record<SimInput["exit_rule"], string> = {
  price_bep: "Setelah sinyal BEP harga",
  ex_close: "Close ex-date",
  payment_close: "Close payment date",
  holding_period: "Batas sesi pengamatan",
};
function inputSignature(input: SimInput, startDate?: string) {
  return JSON.stringify([
    Number(input.capital),
    [...input.event_ids].sort(),
    input.allocation,
    input.entry_sessions_before_cum,
    input.exit_rule,
    input.max_holding_sessions,
    input.start_date ?? startDate,
    input.end_date,
    input.compare,
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
  const [input, setInput] = useState<SimInput>({
    capital: 100000000,
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
  const submit = useMutation({
    mutationFn: (body: SimInput) =>
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
  const set = <K extends keyof SimInput>(key: K, value: SimInput[K]) =>
    setInput({ ...input, [key]: value });
  const toggle = (id: string) =>
    set(
      "event_ids",
      input.event_ids.includes(id)
        ? input.event_ids.filter((e) => e !== id)
        : [...input.event_ids, id],
    );
  return (
    <div className="simulator">
      <div className="sim-setup">
        <section className="glass pad">
          <div className="section-head">
            <div>
              <p className="eyebrow">01 / BUILD YOUR STRATEGY</p>
              <h2>Atur perjalanan modal</h2>
            </div>
            <Route size={21} className="accent" />
          </div>
          {initialEvent && (
            <p className="notice">
              Pilihan dari detail:{" "}
              <strong>
                {initialEvent.symbol} · ex {dt(initialEvent.ex_date, true)}
              </strong>
              . Periode awal mencakup tahun 2025; sesuaikan sebelum menjalankan
              simulasi.
            </p>
          )}
          {copiedFrom && (
            <p className="notice" role="status">
              Draf dari hasil {copiedFrom.slice(0, 8)}. Ubah aturan lalu
              jalankan untuk menyimpan hasil baru. Hasil asal tetap tersimpan.
            </p>
          )}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const form = new FormData(e.currentTarget);
              const next = {
                ...input,
                end_date: String(form.get("end_date")),
                start_date: String(form.get("start_date")),
                capital: Number(form.get("capital")),
                max_holding_sessions: Number(form.get("max_holding_sessions")),
              };
              setInput(next);
              submit.mutate(next);
            }}
          >
            <div className="form-grid">
              <label>
                Modal awal (Rp)
                <input
                  ref={capitalField}
                  type="number"
                  name="capital"
                  required
                  min="1"
                  max="1000000000000"
                  step="1"
                  value={input.capital}
                  onChange={(e) => set("capital", Number(e.target.value))}
                />
              </label>
              <label>
                Strategi utama
                <select
                  value={input.allocation}
                  onChange={(e) =>
                    set("allocation", e.target.value as Allocation)
                  }
                >
                  {Object.entries(labels).map(([key, name]) => (
                    <option key={key} value={key}>
                      {name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <fieldset>
              <legend>
                Event dalam rute (maks. 10){" "}
                <span className="muted">
                  · {input.event_ids.length} dipilih
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
            <div className="form-grid">
              <label>
                Masuk sebelum cum date
                <select
                  value={input.entry_sessions_before_cum}
                  onChange={(e) =>
                    set("entry_sessions_before_cum", Number(e.target.value))
                  }
                >
                  <option value={0}>Close pada cum date</option>
                  <option value={5}>5 sesi sebelumnya</option>
                  <option value={10}>10 sesi sebelumnya</option>
                </select>
              </label>
              <label>
                Aturan keluar
                <select
                  value={input.exit_rule}
                  onChange={(e) =>
                    set("exit_rule", e.target.value as SimInput["exit_rule"])
                  }
                >
                  <option value="price_bep">Setelah sinyal BEP harga</option>
                  <option value="ex_close">Close ex-date</option>
                  <option value="payment_close">Close payment date</option>
                  <option value="holding_period">Batas sesi pengamatan</option>
                </select>
              </label>
              <label>
                Batas sesi setelah ex-date
                <input
                  type="number"
                  name="max_holding_sessions"
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
                Awal replay
                <input
                  type="date"
                  name="start_date"
                  min="2025-01-01"
                  max={input.end_date}
                  required
                  value={input.start_date}
                  onInput={(e) => set("start_date", e.currentTarget.value)}
                  onChange={(e) => set("start_date", e.target.value)}
                />
              </label>
              <label>
                Akhir replay
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
            </div>
            <p className="tiny muted">
              Batas sesi berlaku untuk BEP, payment, dan pengamatan. Bagi rata
              membagi anggaran per event. Entry memakai close; sinyal BEP pada
              close dieksekusi pada open sesi berikutnya.
            </p>
            <div className="notice">
              Replay historis · Lot 100 saham · Dana jual T+2 sesi dataset ·
              Dividen tersedia pada payment date.
            </div>
            <button
              className="btn primary full"
              disabled={busy || !input.event_ids.length}
              type="submit"
            >
              {busy ? (
                <>
                  <span className="spinner" /> Menghitung perjalanan modal…
                </>
              ) : (
                <>
                  <Play size={16} /> Jalankan & bandingkan strategi
                </>
              )}
            </button>
            <p className="tiny muted center">
              Di luar biaya transaksi, pajak, dan slippage.
            </p>
          </form>
        </section>
        <aside className="glass pad history-panel">
          <p className="eyebrow">SAVED RESEARCH</p>
          <h2>
            <History size={18} /> Riwayat simulasi
          </h2>
          <p className="small muted">
            Input dan hasil tersimpan sebagai run terpisah.
          </p>
          {history.isError ? (
            <div className="notice error">Riwayat belum dapat dimuat.</div>
          ) : history.isPending ? (
            <p className="muted">Memuat…</p>
          ) : !history.data?.length ? (
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
              {(showAllHistory ? history.data : history.data.slice(0, 6)).map(
                (r) => (
                  <button
                    className={jobId === r.id ? "active" : ""}
                    key={r.id}
                    aria-label={`Buka hasil ${r.id.slice(0, 8)}`}
                    aria-pressed={jobId === r.id}
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
                ),
              )}
            </div>
          )}
          {!!history.data && history.data.length > 6 && (
            <button
              className="btn subtle full"
              aria-expanded={showAllHistory}
              onClick={() => setShowAllHistory(!showAllHistory)}
            >
              {showAllHistory
                ? "Tampilkan 6 terbaru"
                : `Lihat semua (${history.data.length})`}
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
          {submit.error?.message ?? run.error?.message ?? run.data?.error}
        </div>
      )}
      {selected && result && (
        <section className="results">
          <div className="section-head">
            <div>
              <p className="eyebrow">02 / FOLLOW THE MONEY</p>
              <h2>Hasil replay strategi</h2>
              <p className="small muted">
                {dt(result.primary.start_date, true)} –{" "}
                {dt(result.input.end_date, true)} · ID{" "}
                {run.data?.id.slice(0, 8)}
              </p>
            </div>
            <span className="badge">Historis · gross</span>
          </div>
          <section
            className="glass pad run-snapshot"
            aria-label="Input asli hasil"
          >
            <div className="section-head">
              <div>
                <h3>Input asli hasil ini</h3>
                <p className="small muted">
                  {draftDiffers
                    ? "Form saat ini berbeda. Angka di bawah tetap memakai input tersimpan ini."
                    : "Form sesuai input hasil ini. Mengubah form tidak menghitung ulang hasil."}
                </p>
              </div>
              <button
                className="btn subtle"
                disabled={busy || unavailableEvents.length > 0}
                onClick={() => {
                  setInput({
                    ...result.input,
                    capital: Number(result.input.capital),
                    event_ids: [...result.input.event_ids],
                    start_date:
                      result.input.start_date ?? result.primary.start_date,
                  });
                  setCopiedFrom(run.data!.id);
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
                  {result.input.entry_sessions_before_cum === 0
                    ? "Close pada cum date"
                    : `${result.input.entry_sessions_before_cum} sesi sebelum cum date`}
                </dd>
              </div>
              <div>
                <dt>Aturan keluar</dt>
                <dd>{exitLabels[result.input.exit_rule]}</dd>
              </div>
              <div>
                <dt>Batas setelah ex-date</dt>
                <dd>{result.input.max_holding_sessions} sesi</dd>
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
          </section>
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
                    {r.trades.filter((t) => t.shares > 0).length} posisi dibeli
                  </span>
                </div>
              </button>
            ))}
          </div>
          <ResultView replay={selected} alternatives={result.alternatives} />
        </section>
      )}
      {!selected && !busy && (
        <div className="glass sim-empty">
          <div className="orbit-visual">
            <Route size={32} />
          </div>
          <div>
            <p className="eyebrow">FROM ASSUMPTIONS TO EVIDENCE</p>
            <h2>Setiap rute punya konsekuensi.</h2>
            <p className="muted">
              Jalankan replay untuk melihat hasil, penurunan nilai,
              <br />
              dan berapa lama modal menunggu.
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
}: {
  replay: Replay;
  alternatives: Replay[];
}) {
  const [ledger, setLedger] = useState(false);
  const dates = [
    ...new Set(alternatives.flatMap((a) => a.curve.map((c) => c.date))),
  ].sort();
  const colors = ["#8b8096", "#e5bd98", "#d77da9"];
  return (
    <>
      <div className="glass pad result-chart">
        <div className="section-head">
          <div>
            <h3>Perjalanan nilai portofolio</h3>
            <p className="small muted">
              Kas + saham + piutang. Garis memakai jalur harga historis yang
              sama.
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
          height={290}
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
          <small>Nilai akhir portofolio</small>
          <strong>{money(r.ending_nav)}</strong>
          <span>Termasuk posisi & piutang</span>
        </div>
        <div className="glass pad">
          <small>Dividen menjadi hak</small>
          <strong>{money(r.dividends)}</strong>
          <span>Belum dibayar: {money(r.pending_dividends)}</span>
        </div>
        <div className="glass pad">
          <small>Kas tersedia di akhir</small>
          <strong>{money(r.ending_cash)}</strong>
          <span>Piutang jual: {money(r.pending_sales)}</span>
        </div>
      </div>
      <section className="glass pad">
        <div className="section-head">
          <div>
            <p className="eyebrow">CAPITAL ROUTE</p>
            <h3>{labels[r.allocation]} · jejak perpindahan</h3>
          </div>
          <span className="badge">{r.rules_version}</span>
        </div>
        <div className="route-list">
          {r.trades.map((t, i) => (
            <div className="route-step" key={t.event_id}>
              <div className="route-index">
                {String(i + 1).padStart(2, "0")}
              </div>
              <div className="route-body">
                <div className="spread">
                  <h3>
                    {t.symbol}{" "}
                    <span className="badge mini">
                      {t.status === "sold"
                        ? "Terjual"
                        : t.status === "holding"
                          ? "Masih dipegang"
                          : "Terlewat"}
                    </span>
                  </h3>
                  <strong
                    className={t.gross_pnl >= 0 ? "positive" : "negative"}
                  >
                    {money(t.gross_pnl)}
                  </strong>
                </div>
                <div className="route-dates">
                  <span>
                    Masuk <strong>{dt(t.entry_date, true)}</strong>
                    <small>
                      {money(t.entry_price)} ·{" "}
                      {t.shares.toLocaleString("id-ID")} saham
                    </small>
                  </span>
                  <ArrowRight size={17} />
                  <span>
                    Keluar{" "}
                    <strong>{t.exit_date ? dt(t.exit_date, true) : "—"}</strong>
                    <small>
                      {t.exit_price
                        ? money(t.exit_price)
                        : t.status === "holding"
                          ? "Dinilai dengan harga terakhir"
                          : "Tidak ada posisi"}
                    </small>
                  </span>
                  <ArrowRight size={17} />
                  <span>
                    Kas jual tersedia{" "}
                    <strong>
                      {t.settlement_date ? dt(t.settlement_date, true) : "—"}
                    </strong>
                    <small>
                      {t.capital_days} hari modal tertahan / diamati
                    </small>
                  </span>
                </div>
                <p className="small muted">{t.reason}</p>
                <div className="route-foot">
                  <span>Dividen {money(t.dividend)}</span>
                  <span>PnL saham {money(t.capital_pnl)}</span>
                  <span>Payment {dt(t.payment_date, true)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
      <section className="glass pad">
        <button
          className="section-toggle"
          onClick={() => setLedger(!ledger)}
          aria-expanded={ledger}
        >
          <h3>Ledger kas & hak dividen</h3>
          <span>
            {ledger ? "Tutup" : "Telusuri"} {r.ledger.length} aktivitas{" "}
            <ArrowUpRight size={15} />
          </span>
        </button>
        {ledger && (
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
                    <td className="ledger-detail">{l.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <details className="glass pad assumptions">
        <summary>Asumsi dan batas hasil ini</summary>
        <ul>
          {r.assumptions.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ul>
        <p>
          Angka kerugian historis bukan probabilitas trap. Strategi terbaik pada
          replay ini belum tentu terbaik di masa depan.
        </p>
      </details>
    </>
  );
}
