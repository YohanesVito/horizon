"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowDown,
  ArrowDownWideNarrow,
  ArrowRight,
  ArrowUpRight,
  Bookmark,
  CalendarDays,
  ChartNoAxesCombined,
  ChevronLeft,
  ChevronRight,
  Layers3,
  Route,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import { api, dt, money, pct } from "@/lib/api";
import type {
  Catalog,
  Company,
  CompanyDetail,
  DividendEvent,
  Rules,
} from "@/lib/types";
import Chart, { lineOption, Sparkline } from "./chart";
import CompanyDialog from "./detail";
import Simulator from "./simulator";
import Intelligence from "./intelligence";
import RotationPlanner from "./rotation-planner";
const DividendTimeline = dynamic(() => import("./dividend-timeline"));
type View =
  | "Peluang"
  | "Kalender"
  | "Timeline"
  | "Simulator"
  | "Intelligence"
  | "Rencana rotasi"
  | "Watchlist"
  | "Metodologi";
const nav = [
  // Fitur lain tetap tersedia di kode, tetapi tidak mengalihkan alur demo.
  { name: "Timeline", label: "Analisis" },
  { name: "Simulator", label: "Simulasi" },
] as const;
export const defaults: Rules = {
  name: "Logika dividen saya",
  minimum_yield: 0,
  minimum_frequency: 0,
  require_replay: false,
  sort_by: "yield",
};
export function Notice({
  children,
  error = false,
}: {
  children: React.ReactNode;
  error?: boolean;
}) {
  return (
    <div
      role={error ? "alert" : undefined}
      className={`notice ${error ? "error" : ""}`}
    >
      {children}
    </div>
  );
}
export function Empty({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="empty">
      <Layers3 size={28} />
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}
export default function Dashboard() {
  const [view, setView] = useState<View>("Timeline"),
    [plannerSymbols, setPlannerSymbols] = useState<string[] | undefined>(),
    [simulationEvent, setSimulationEvent] = useState<string | undefined>(),
    [evidenceSymbol, setEvidenceSymbol] = useState("BBCA"),
    [detail, setDetail] = useState<string | null>(null),
    [query, setQuery] = useState(""),
    [replayOnly, setReplayOnly] = useState(false),
    [showRules, setShowRules] = useState(false),
    [draft, setDraft] = useState<Rules | null>(null),
    [message, setMessage] = useState("");
  const client = useQueryClient();
  const catalog = useQuery({
    queryKey: ["catalog"],
    queryFn: () => api<Catalog>("/catalog"),
  });
  const watches = useQuery({
    queryKey: ["watchlist"],
    queryFn: () => api<{ symbols: string[] }>("/watchlist"),
  });
  const rulesQuery = useQuery({
    queryKey: ["rules"],
    queryFn: () => api<Rules>("/rules"),
  });
  const rules = draft ?? rulesQuery.data ?? defaults;
  const watch = useMutation({
    mutationFn: ({ symbol, remove }: { symbol: string; remove: boolean }) =>
      api<{ symbols: string[] }>(`/watchlist${remove ? `/${symbol}` : ""}`, {
        method: remove ? "DELETE" : "POST",
        ...(remove ? {} : { body: JSON.stringify({ symbol }) }),
      }),
    onSuccess: (data) => client.setQueryData(["watchlist"], data),
  });
  const saveRules = useMutation({
    mutationFn: () =>
      api<Rules>("/rules", { method: "PUT", body: JSON.stringify(rules) }),
    onSuccess: (data) => {
      client.setQueryData(["rules"], data);
      setDraft(null);
      setMessage("Logika screening tersimpan.");
    },
  });
  const data = catalog.data;
  const [navVisible, setNavVisible] = useState(true);
  const lastScrollY = useRef(0);

  useEffect(() => {
    const threshold = 8;
    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      // Always show near top of page
      if (currentScrollY <= 60) {
        setNavVisible(true);
        lastScrollY.current = currentScrollY;
        return;
      }

      const delta = currentScrollY - lastScrollY.current;
      if (Math.abs(delta) < threshold) return;

      if (delta > 0) {
        // Scrolling down / baca konten ke bawah -> hide
        setNavVisible(false);
      } else {
        // Scrolling up / geser ke atas -> show
        setNavVisible(true);
      }
      lastScrollY.current = currentScrollY;
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const changeView = (next: View) => {
    setView(next);
    setMessage("");
    setNavVisible(true);
    window.scrollTo({ top: 0, behavior: "instant" });
  };
  const toggleWatch = (symbol: string) =>
    watch.mutate({ symbol, remove: !!watches.data?.symbols.includes(symbol) });
  const companies = (data?.companies ?? [])
    .filter(
      (c) =>
        (view !== "Watchlist" || watches.data?.symbols.includes(c.symbol)) &&
        `${c.symbol} ${c.name}`.toLowerCase().includes(query.toLowerCase()) &&
        (c.annual_yield_pct ?? 0) >= rules.minimum_yield &&
        c.frequency >= rules.minimum_frequency &&
        (!(replayOnly || rules.require_replay) || c.replay_available),
    )
    .sort((a, b) =>
      rules.sort_by === "symbol"
        ? a.symbol.localeCompare(b.symbol)
        : rules.sort_by === "frequency"
          ? b.frequency - a.frequency
          : (b.annual_yield_pct ?? 0) - (a.annual_yield_pct ?? 0),
    );
  return (
    <div className="app-shell editorial-app" data-view={view}>
      <a className="skip-link" href="#main">
        Ke konten utama
      </a>
      <header className={`site-header ${navVisible ? "" : "nav-hidden"}`}>
        <Link
          href="/"
          className="brand"
          aria-label="Dividen Lab — halaman utama"
        >
          <span className="brand-wordmark">
            DIVIDEN<span>LAB</span>
            <i aria-hidden="true">.</i>
          </span>
        </Link>
        <span className="site-header-divider" aria-hidden="true" />
        <nav aria-label="Navigasi utama">
          {nav.map(({ name, label }) => (
            <button
              key={name}
              aria-label={label}
              title={label}
              onClick={() => {
                if (name === "Simulator") setSimulationEvent(undefined);
                changeView(name);
              }}
              className={`nav-item ${view === name ? "active" : ""}`}
              aria-current={view === name ? "page" : undefined}
            >
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <span className="site-header-source">Powered by Sectors</span>
      </header>
      <main id="main" className="main">
        <div className="page-content">
          {view === "Timeline" || view === "Simulator" ? (
            <section
              className="page-heading editorial-hero"
              aria-label="Pengantar"
            >
              <h1>
                {view === "Timeline"
                  ? "Lihat harga di sekitar dividen."
                  : "Uji strategi. Baca konsekuensinya."}
              </h1>
              <p className="subtitle">
                {view === "Timeline"
                  ? "Bandingkan harga sebelum dan sesudah ex-date berdasarkan riwayat peristiwa dividen. Gunakan sebagai konteks untuk menilai skenario Anda."
                  : "Atur modal dan aturan keluar. Lihat hasil replay, risiko, dan kapan kas tersedia."}
              </p>
              <a
                href="#workspace-content"
                className="hero-scroll-btn"
              >
                {view === "Timeline" ? "Jelajahi data" : "Mulai simulasi"}
                <ArrowDown size={18} strokeWidth={2} aria-hidden="true" />
              </a>
            </section>
          ) : (
            <div className="page-heading">
              <div>
                <p className="eyebrow">{view.toUpperCase()}</p>
                <h1>{view}</h1>
              </div>
            </div>
          )}
          <div id="workspace-content" className="workspace-content">
            {catalog.isPending && (
              <div className="loading glass">Memuat workspace Sectors…</div>
            )}
            {catalog.isError && (
              <Notice error>
                {catalog.error.message}{" "}
                <button
                  className="text-button"
                  onClick={() => catalog.refetch()}
                >
                  Coba lagi
                </button>
              </Notice>
            )}
            {(watch.isError ||
              saveRules.isError ||
              watches.isError ||
              rulesQuery.isError) && (
              <Notice error>
                {watch.error?.message ??
                  saveRules.error?.message ??
                  watches.error?.message ??
                  rulesQuery.error?.message}
              </Notice>
            )}
            {message && (
              <div role="status" className="notice success">
                {message}
              </div>
            )}
            {view === "Timeline" && <DividendTimeline />}
            {data && (view === "Peluang" || view === "Watchlist") && (
              <>
                {view === "Peluang" && (
                  <>
                    <section className="metrics">
                      <Metric
                        label="Emiten dalam riset"
                        value={String(data.companies.length).padStart(2, "0")}
                        note="Sampel terpilih · bukan seluruh IDX"
                        icon={<Layers3 size={18} />}
                      />
                      <Metric
                        label="Yield tahunan tertinggi"
                        value={pct(
                          Math.max(
                            ...data.companies.map(
                              (c) => c.annual_yield_pct ?? 0,
                            ),
                          ),
                        )}
                        note="DMAS · historis 2025"
                        icon={<ChartNoAxesCombined size={18} />}
                      />
                      <Metric
                        label="Event dividen"
                        value={String(data.events.length)}
                        note="Jadwal dan histori tahun 2025"
                        icon={<CalendarDays size={18} />}
                      />
                      <Metric
                        label="Siap untuk replay"
                        value={String(
                          data.companies.filter((c) => c.replay_available)
                            .length,
                        ).padStart(2, "0")}
                        note="Emiten dengan harga dan jadwal"
                        icon={<Route size={18} />}
                      />
                    </section>
                    <div className="overview-grid">
                      <PricePanel onDetail={() => setDetail("BBCA")} />
                      <Season
                        events={data.events}
                        onView={() => changeView("Kalender")}
                      />
                    </div>
                  </>
                )}
                <section className="glass company-section">
                  <div className="section-head">
                    <div>
                      <p className="eyebrow">
                        {view === "Watchlist"
                          ? "YOUR COLLECTION"
                          : "DIVIDEND DISCOVERY"}
                      </p>
                      <h2>
                        {view === "Watchlist"
                          ? "Watchlist kamu"
                          : "Kandidat pilihan riset"}
                      </h2>
                    </div>
                    <button
                      className={`btn subtle ${showRules ? "selected" : ""}`}
                      onClick={() => setShowRules(!showRules)}
                      aria-expanded={showRules}
                    >
                      <SlidersHorizontal size={15} /> Logika screening
                    </button>
                  </div>
                  {showRules && (
                    <div className="rule-panel">
                      <div className="form-grid">
                        <label>
                          Nama logika
                          <input
                            value={rules.name}
                            maxLength={80}
                            onChange={(e) =>
                              setDraft({ ...rules, name: e.target.value })
                            }
                          />
                        </label>
                        <label>
                          Yield tahunan minimum (%)
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={rules.minimum_yield}
                            onChange={(e) =>
                              setDraft({
                                ...rules,
                                minimum_yield: Number(e.target.value),
                              })
                            }
                          />
                        </label>
                        <label>
                          Pembagian minimum / tahun
                          <input
                            type="number"
                            min="0"
                            max="12"
                            value={rules.minimum_frequency}
                            onChange={(e) =>
                              setDraft({
                                ...rules,
                                minimum_frequency: Number(e.target.value),
                              })
                            }
                          />
                        </label>
                      </div>
                      <div className="spread">
                        <label className="check-label">
                          <input
                            type="checkbox"
                            checked={rules.require_replay}
                            onChange={(e) =>
                              setDraft({
                                ...rules,
                                require_replay: e.target.checked,
                              })
                            }
                          />{" "}
                          Hanya emiten dengan data replay
                        </label>
                        <button
                          className="btn primary small"
                          disabled={saveRules.isPending || !rules.name.trim()}
                          onClick={() => saveRules.mutate()}
                        >
                          Simpan logika
                        </button>
                      </div>
                      <p className="tiny muted">
                        Filter ini memakai yield tahunan versi Sectors.
                        Urutannya bukan estimasi keuntungan strategi.
                      </p>
                    </div>
                  )}
                  <div className="table-controls">
                    <div className="segmented">
                      <button
                        className={!replayOnly ? "selected" : ""}
                        onClick={() => setReplayOnly(false)}
                      >
                        Semua emiten{" "}
                        <span>
                          {view === "Watchlist"
                            ? (watches.data?.symbols.length ?? 0)
                            : data.companies.length}
                        </span>
                      </button>
                      <button
                        className={replayOnly ? "selected" : ""}
                        onClick={() => setReplayOnly(true)}
                      >
                        Siap replay
                      </button>
                    </div>
                    <div className="search-sort">
                      <label className="search">
                        <Search size={16} />
                        <input
                          aria-label="Cari emiten"
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          placeholder="Cari nama atau kode…"
                        />
                      </label>
                      <label className="sort">
                        <ArrowDownWideNarrow size={15} />
                        <select
                          aria-label="Urutkan emiten"
                          value={rules.sort_by}
                          onChange={(e) =>
                            setDraft({
                              ...rules,
                              sort_by: e.target.value as Rules["sort_by"],
                            })
                          }
                        >
                          <option value="yield">Yield tertinggi</option>
                          <option value="frequency">Paling sering</option>
                          <option value="symbol">Kode A–Z</option>
                        </select>
                      </label>
                    </div>
                  </div>
                  {companies.length ? (
                    <div className="table-scroll">
                      <table className="company-table">
                        <thead>
                          <tr>
                            <th>Emiten</th>
                            <th>
                              Yield 2025 <span className="muted">↓</span>
                            </th>
                            <th>Dividen / saham</th>
                            <th>Frekuensi</th>
                            <th>Tren harga</th>
                            <th>Data replay</th>
                            <th>
                              <span className="sr-only">Aksi</span>
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {companies.map((c) => (
                            <CompanyRow
                              key={c.symbol}
                              company={c}
                              watched={
                                !!watches.data?.symbols.includes(c.symbol)
                              }
                              busy={watch.isPending}
                              onWatch={() => toggleWatch(c.symbol)}
                              onDetail={() => setDetail(c.symbol)}
                            />
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <Empty
                      title={
                        view === "Watchlist"
                          ? "Belum ada emiten yang tampil"
                          : "Belum ada yang sesuai"
                      }
                    >
                      {view === "Watchlist"
                        ? "Tambahkan emiten lewat ikon bookmark di Peluang, atau longgarkan filter."
                        : "Coba ubah kata pencarian atau logika screening."}
                    </Empty>
                  )}
                  <div className="table-footer">
                    <span>{companies.length} emiten ditampilkan</span>
                    <button
                      className="text-button"
                      disabled={!companies.length}
                      onClick={() => {
                        setPlannerSymbols(companies.map((c) => c.symbol));
                        changeView("Rencana rotasi");
                      }}
                    >
                      Gunakan emiten ini untuk rencana →
                    </button>
                    <span>
                      Yield historis dari Sectors · bukan proyeksi return
                    </span>
                  </div>
                </section>
              </>
            )}
            {data && view === "Kalender" && (
              <Calendar
                events={data.events}
                known={data.companies.map((c) => c.symbol)}
                onDetail={setDetail}
              />
            )}
            {data && view === "Simulator" && (
              <Simulator
                key={simulationEvent ?? "manual"}
                catalog={data}
                initialEventId={simulationEvent}
              />
            )}
            {data && view === "Intelligence" && (
              <Intelligence
                initialSymbol={evidenceSymbol}
                onPlan={() => {
                  setPlannerSymbols(undefined);
                  changeView("Rencana rotasi");
                }}
              />
            )}
            {data && view === "Rencana rotasi" && (
              <RotationPlanner catalog={data} initialSymbols={plannerSymbols} />
            )}
            {data && view === "Metodologi" && <Methodology catalog={data} />}
          </div>
          <footer className="footer">
            <span>Dividen Lab</span>
            <button
              className="text-button"
              onClick={() =>
                changeView(view === "Metodologi" ? "Timeline" : "Metodologi")
              }
            >
              {view === "Metodologi"
                ? "Kembali ke analisis"
                : "Sumber & metodologi"}
            </button>
            <span>
              Seluruh hasil di luar biaya transaksi, pajak, dan slippage.
            </span>
          </footer>
        </div>
      </main>
      {detail && (
        <CompanyDialog
          symbol={detail}
          onIntelligence={() => {
            setEvidenceSymbol(detail);
            setDetail(null);
            changeView("Intelligence");
          }}
          onClose={() => setDetail(null)}
          onSimulate={(eventId) => {
            setSimulationEvent(eventId);
            setDetail(null);
            changeView("Simulator");
          }}
        />
      )}
    </div>
  );
}
function Metric({
  label,
  value,
  note,
  icon,
}: {
  label: string;
  value: string;
  note: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="glass metric">
      <div className="spread">
        <span>{label}</span>
        <span className="metric-icon">{icon}</span>
      </div>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  );
}
function PricePanel({ onDetail }: { onDetail: () => void }) {
  const q = useQuery({
    queryKey: ["company", "BBCA"],
    queryFn: () => api<CompanyDetail>("/companies/BBCA"),
  });
  const bars = q.data?.prices ?? [];
  return (
    <section className="glass price-panel">
      <div className="section-head">
        <div>
          <h2>Harga historis BBCA</h2>
        </div>
        <button
          className="icon-btn"
          aria-label="Buka detail BBCA"
          onClick={onDetail}
        >
          <ArrowUpRight size={20} />
        </button>
      </div>
      <div className="chart-summary">
        <span className="ticker-logo">B</span>
        <div>
          <strong>BBCA</strong>
          <span className="muted">Bank Central Asia</span>
        </div>
        <div className="chart-price">
          <strong>{money(bars.at(-1)?.close)}</strong>
          <small>{dt(bars.at(-1)?.date, true)}</small>
        </div>
      </div>
      {q.isError ? (
        <Notice error>{q.error.message}</Notice>
      ) : bars.length ? (
        <Chart
          label="Grafik harga penutupan BBCA, tahun 2025"
          option={lineOption(
            bars.map((b) => b.date),
            [
              {
                name: "BBCA close",
                values: bars.map((b) => b.close),
                color: "#ca82a8",
              },
            ],
          )}
          height={205}
        />
      ) : (
        <div className="loading">Memuat harga…</div>
      )}
      <div className="chart-caption">
        <span>
          <i className="line-key" /> Harga penutupan harian · snapshot historis
        </span>
        <button className="text-button" onClick={onDetail}>
          Lihat timeline dividen <ArrowRight size={13} />
        </button>
      </div>
    </section>
  );
}
function Season({
  events,
  onView,
}: {
  events: DividendEvent[];
  onView: () => void;
}) {
  const selected = ["BBRI", "BMRI", "BBNI", "LPPF"]
    .map((s) =>
      events.find((e) => e.symbol === s && e.ex_date.startsWith("2025-04")),
    )
    .filter((e): e is DividendEvent => !!e);
  return (
    <section className="glass season">
      <div className="section-head">
        <div>
          <h2>Cuplikan dividen April 2025</h2>
        </div>
        <CalendarDays size={19} className="accent" />
      </div>
      <p className="muted small">Cuplikan ex-date · April 2025</p>
      <div className="season-events">
        {selected.map((e) => (
          <div className="season-event" key={e.id}>
            <div className="date-tile">
              <strong>{Number(e.ex_date.slice(-2))}</strong>
              <small>APR</small>
            </div>
            <div>
              <strong>{e.symbol}</strong>
              <small>{money(e.dps)} / saham</small>
            </div>
            <span className="badge mini">Ex-date</span>
          </div>
        ))}
      </div>
      <button className="btn ghost full" onClick={onView}>
        Jelajahi kalender <ArrowRight size={15} />
      </button>
    </section>
  );
}
function CompanyRow({
  company: c,
  watched,
  busy,
  onWatch,
  onDetail,
}: {
  company: Company;
  watched: boolean;
  busy: boolean;
  onWatch: () => void;
  onDetail: () => void;
}) {
  return (
    <tr>
      <td>
        <button className="company-name" onClick={onDetail}>
          <span className={`ticker-logo tone-${c.symbol.charCodeAt(0) % 3}`}>
            {c.symbol.slice(0, 1)}
          </span>
          <span>
            <strong>{c.symbol}</strong>
            <small title={c.name}>{c.name}</small>
          </span>
        </button>
      </td>
      <td>
        <strong className="yield">{pct(c.annual_yield_pct)}</strong>
      </td>
      <td>{money(c.annual_dps)}</td>
      <td>
        <span className="frequency">
          {c.frequency}× <span className="muted">/ tahun</span>
        </span>
      </td>
      <td>
        <Sparkline values={c.sparkline} />
      </td>
      <td>
        <span className={`status ${c.replay_available ? "ready" : ""}`}>
          <i />
          {c.replay_available ? "Tersedia" : "Belum lengkap"}
        </span>
      </td>
      <td>
        <div className="row-actions">
          <button
            className={`icon-btn ${watched ? "bookmarked" : ""}`}
            aria-label={`${watched ? "Hapus" : "Simpan"} ${c.symbol} ${watched ? "dari" : "ke"} watchlist`}
            aria-pressed={watched}
            disabled={busy}
            onClick={onWatch}
          >
            <Bookmark size={17} fill={watched ? "currentColor" : "none"} />
          </button>
          <button
            className="icon-btn"
            onClick={onDetail}
            aria-label={`Lihat detail ${c.symbol}`}
          >
            <ArrowUpRight size={17} />
          </button>
        </div>
      </td>
    </tr>
  );
}
function Calendar({
  events,
  known,
  onDetail,
}: {
  events: DividendEvent[];
  known: string[];
  onDetail: (s: string) => void;
}) {
  const [month, setMonth] = useState(3),
    [kind, setKind] = useState<"ex_date" | "cum_date" | "payment_date">(
      "ex_date",
    );
  const start = new Date(2025, month, 1),
    offset = (start.getDay() + 6) % 7,
    days = new Date(2025, month + 1, 0).getDate();
  const monthKey = `2025-${String(month + 1).padStart(2, "0")}`;
  const filtered = events.filter((e) => e[kind]?.startsWith(monthKey));
  return (
    <section className="glass calendar-panel">
      <div className="section-head">
        <div>
          <h2>
            {start.toLocaleDateString("id-ID", {
              month: "long",
              year: "numeric",
            })}
          </h2>
        </div>
        <div className="inline">
          <select
            aria-label="Jenis tanggal kalender"
            value={kind}
            onChange={(e) => setKind(e.target.value as typeof kind)}
          >
            <option value="ex_date">Ex-date</option>
            <option value="cum_date">Cum date</option>
            <option value="payment_date">Payment date</option>
          </select>
          <button
            className="icon-btn"
            aria-label="Bulan sebelumnya"
            disabled={month === 0}
            onClick={() => setMonth(month - 1)}
          >
            <ChevronLeft size={18} />
          </button>
          <button
            className="icon-btn"
            aria-label="Bulan berikutnya"
            disabled={month === 11}
            onClick={() => setMonth(month + 1)}
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
      <p className="muted small">
        {filtered.length} event dengan tanggal tersedia. Cakupan bulan tidak
        merata; kosong tidak berarti tidak ada dividen di pasar.
      </p>
      <div className="calendar-grid">
        {["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"].map((d) => (
          <div className="weekday" key={d}>
            {d}
          </div>
        ))}
        {Array.from({ length: offset }, (_, i) => (
          <div className="day blank" key={`blank${i}`} />
        ))}
        {Array.from({ length: days }, (_, i) => {
          const date = `${monthKey}-${String(i + 1).padStart(2, "0")}`;
          return (
            <div className="day" key={i}>
              <span className="day-number">{i + 1}</span>
              {filtered
                .filter((e) => e[kind] === date)
                .map((e) => (
                  <button
                    className="calendar-event"
                    key={e.id}
                    disabled={!known.includes(e.symbol)}
                    onClick={() => onDetail(e.symbol)}
                    title={`${e.symbol} · ${money(e.dps)} per saham${known.includes(e.symbol) ? "" : " · detail belum dimuat"}`}
                  >
                    <strong>{e.symbol}</strong>
                    <span>{money(e.dps)}</span>
                  </button>
                ))}
            </div>
          );
        })}
      </div>
      <Notice>
        Cum date, ex-date, recording date, dan payment date memiliki fungsi
        berbeda. Buka emiten untuk melihat lima tahap timeline; declaration date
        yang belum tersedia tetap ditandai kosong.
      </Notice>
    </section>
  );
}
function Methodology({ catalog }: { catalog: Catalog }) {
  return (
    <div className="method-grid">
      <section className="glass pad">
        <h2>Sumber dan cakupan data</h2>
        <p>
          Seluruh data finansial berasal dari Sectors. Workspace ini memuat{" "}
          {catalog.companies.length} emiten terpilih dan {catalog.events.length}{" "}
          event pada tahun 2025, dengan harga replay sepanjang tahun 2025.
        </p>
        <dl>
          <dt>Sumber</dt>
          <dd>Sectors MCP + Corporate Actions API</dd>
          <dt>Pengambilan harga terbaru</dt>
          <dd>{dt(catalog.meta.retrieved_at, true)}</dd>
          <dt>Yield</dt>
          <dd>
            Total yield tahunan versi Sectors, bukan return pembelian pada harga
            tertentu.
          </dd>
          <dt>Jadwal tidak lengkap</dt>
          <dd>
            Ditampilkan apa adanya. Event tanpa cum date atau harga yang sesuai
            tidak dapat direplay.
          </dd>
        </dl>
        <a
          className="text-button"
          href="https://docs.sectors.app/api-references"
          target="_blank"
          rel="noreferrer"
        >
          Dokumentasi sumber <ArrowUpRight size={14} />
        </a>
      </section>
      <section className="glass pad">
        <h2>Perhitungan modal dan dividen</h2>
        <p>
          Nilai portofolio = kas + nilai saham yang masih dipegang + piutang
          hasil jual + piutang dividen. Dividen baru bisa dipakai kembali pada
          payment date.
        </p>
        <p>
          Hasil jual tersedia setelah T+2 hari bursa yang diamati dalam dataset.
          Ini asumsi replay, bukan verifikasi kalender resmi bursa. Lot 100
          saham, tanpa margin.
        </p>
        <p>
          Gap hari bursa IHSG dilengkapi dari harga valid kesembilan emiten pada{" "}
          {catalog.meta.session_repairs?.map((d) => dt(d)).join(", ") || "—"}.
          Tanggal perbaikan dan versi dataset disimpan untuk audit.
        </p>
        <p>
          <strong>BEP harga</strong> berarti harga kembali ke harga beli.{" "}
          <strong>BEP total</strong> memperhitungkan hak dividen. Sinyal close
          BEP dieksekusi pada open hari bursa berikutnya; harga eksekusi bisa
          kembali turun.
        </p>
        <Notice>
          Biaya transaksi, pajak, dan slippage = 0 sesuai scope awal. Semua
          hasil adalah gross.
        </Notice>
      </section>
      <section className="glass pad">
        <h2>Risiko dan pemulihan</h2>
        <p>
          Pilot detail BBCA memakai entry close cum-date untuk 8 event. Menu
          Intelligence memperluas audit ke 48 event pada 9 emiten (2022–2025),
          dengan entry dan horizon yang bisa diubah. Event belum pulih tetap
          masuk kurva Kaplan–Meier; konflik dan basis split dikarantina.
        </p>
        <p>
          Frekuensi rugi memiliki interval Wilson 95% dan jumlah sampel.
          Skenario modal menggunakan analog harga historis dengan nominal serta
          tanggal asumsi pengguna. Belum ada model prediksi terkalibrasi;
          kuantil analog bukan interval prediksi.
        </p>
        <p>
          Kalender diketahui saat riset ini disusun. Karena timestamp pengumuman
          dan vintage laporan keuangan belum lengkap, replay belum membuktikan
          strategi bisa dipilih dengan informasi yang tersedia saat itu.
        </p>
      </section>
      <section className="glass pad">
        <h2>Data yang tersimpan</h2>
        <p>
          Watchlist, logika screening, input, dan hasil simulasi tersimpan di
          server lokal workspace ini. Belum ada akun terpisah atau sinkronisasi
          lintas pengguna.
        </p>
        <p>
          Rotasi memakai kas yang tersedia pada jadwal masuk. Split membagi
          anggaran awal secara merata. All-in memakai event pertama secara
          kronologis. Pembanding memakai modal dan tanggal akhir yang sama.
        </p>
        <p>
          Urutan ini belum mencari rute terbaik dari seluruh saham. Tidak ada
          order yang dikirim dari aplikasi.
        </p>
      </section>
    </div>
  );
}
