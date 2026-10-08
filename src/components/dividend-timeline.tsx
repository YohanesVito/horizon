"use client";

import { useEffect, useRef, useState } from "react";
import type { MouseEvent, PointerEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowUpRight,
  CheckCheck,
  FlaskConical,
  LockKeyhole,
} from "lucide-react";
import { api, dt, money, pct, tradingDayText } from "@/lib/api";
import { cumExMovement, phaseLabel } from "@/lib/timeline-chart";
import type {
  TimelineCatalog,
  TimelineDetail,
  TimelinePeriod,
  TimelinePoint,
} from "@/lib/timeline-types";

const COLORS = [
  "#A7B9C8",
  "#D9AF59",
  "#66B2BF",
  "#9BAF83",
  "#FF7853",
  "#E3D9CE",
];
const color = (year: number) =>
  COLORS[(((year - 2021) % COLORS.length) + COLORS.length) % COLORS.length];
type Units = "percent" | "price";
type Hover = { period: TimelinePeriod; point: TimelinePoint };
const dayLabel = (day: number) =>
  day === 0 ? "Ex · H0" : `H${day > 0 ? "+" : "−"}${Math.abs(day)}`;

export default function DividendTimeline() {
  const [chosenSelection, setChosenSelection] = useState<{
    symbol: string;
    preview: boolean;
  } | null>(null);
  const [selectionTouched, setSelectionTouched] = useState(false);
  const catalog = useQuery({
    queryKey: ["timeline-catalog"],
    queryFn: () => api<TimelineCatalog>("/timeline"),
  });
  // LPPF langsung terbuka untuk demo; versi terverifikasi didahulukan bila tersedia.
  const defaultSelection = catalog.data?.companies.some(
    (c) => c.symbol === "LPPF",
  )
    ? { symbol: "LPPF", preview: false }
    : catalog.data?.preview_symbols.includes("LPPF")
      ? { symbol: "LPPF", preview: true }
      : catalog.data?.companies[0]
        ? { symbol: catalog.data.companies[0].symbol, preview: false }
        : null;
  const selection = selectionTouched ? chosenSelection : defaultSelection;
  const chooseSelection = (next: typeof chosenSelection) => {
    setSelectionTouched(true);
    setChosenSelection(next);
  };
  const detail = useQuery({
    queryKey: ["timeline", selection?.symbol, selection?.preview],
    queryFn: () =>
      api<TimelineDetail>(
        `/timeline/${selection!.symbol}?preview=${selection!.preview}`,
      ),
    enabled: selection !== null,
  });
  if (catalog.isPending)
    return <div className="loading glass">Memeriksa histori lima tahun…</div>;
  if (catalog.isError)
    return (
      <div className="notice error" role="alert">
        {catalog.error.message}{" "}
        <button className="text-button" onClick={() => catalog.refetch()}>
          Coba lagi
        </button>
      </div>
    );
  const data = catalog.data;
  return (
    <div className="timeline-workspace">
      <section className="glass timeline-catalog" aria-label="Pilih emiten">
        <div className="timeline-catalog-title">
          <div>
            <p className="eyebrow">EMITEN</p>
            <h2>Pilih saham untuk dianalisis</h2>
          </div>
        </div>
        {data.companies.length || data.preview_symbols.length ? (
          <label className="timeline-picker">
            <span className="sr-only">Emiten</span>
            <select
              value={
                selection
                  ? `${selection.preview ? "preview" : "verified"}:${selection.symbol}`
                  : ""
              }
              onChange={(e) => {
                const [kind, symbol] = e.target.value.split(":");
                chooseSelection(
                  symbol ? { symbol, preview: kind === "preview" } : null,
                );
              }}
            >
              <option value="">Pilih emiten</option>
              {data.companies.map((c) => (
                <option key={c.symbol} value={`verified:${c.symbol}`}>
                  {c.symbol} — {c.name}
                </option>
              ))}
              {data.preview_symbols.map((symbol) => (
                <option key={`preview:${symbol}`} value={`preview:${symbol}`}>
                  {symbol} — pratinjau
                </option>
              ))}
            </select>
          </label>
        ) : (
          <p className="small muted">
            {data.calendar_candidates} kandidat kalender ditemukan. Tanggal
            declaration dan kelengkapan histori masih diverifikasi.
          </p>
        )}
      </section>
      {!selection && (
        <section className="glass timeline-empty">
          <div className="timeline-empty-icon">
            <LayersGlyph />
          </div>
          <p className="eyebrow">FIVE YEARS. ONE PERSPECTIVE.</p>
          <h2>Kenali pola di sekitar dividen.</h2>
          <p>
            Bandingkan harga sebelum dan sesudah ex-date, lalu telusuri setiap
            fase sampai payment.
          </p>
          {!data.companies.length && (
            <span className="badge">
              <LockKeyhole size={12} /> Katalog menunggu data lengkap
            </span>
          )}
          {data.preview_symbols.includes("LPPF") && (
            <button
              className="btn primary"
              onClick={() => chooseSelection({ symbol: "LPPF", preview: true })}
            >
              Buka pratinjau LPPF <ArrowUpRight size={16} />
            </button>
          )}
          <small className="muted">
            Pratinjau memakai harga historis nyata; kelengkapan timeline belum
            disahkan.
          </small>
        </section>
      )}
      {selection && (
        <>
          {detail.isPending && (
            <div className="loading glass">
              Memuat periode {selection.symbol}…
            </div>
          )}
          {detail.isError && (
            <div className="notice error" role="alert">
              {detail.error.message}{" "}
              <button className="text-button" onClick={() => detail.refetch()}>
                Coba lagi
              </button>
              <button
                className="text-button"
                onClick={() => chooseSelection(null)}
              >
                Kembali
              </button>
            </div>
          )}
          {detail.data && (
            <TimelineExplorer
              key={`${selection.symbol}-${selection.preview}`}
              data={detail.data}
            />
          )}
        </>
      )}
    </div>
  );
}

function LayersGlyph() {
  return (
    <svg width="66" height="44" viewBox="0 0 66 44" aria-hidden="true">
      <path d="M2 31L17 23 31 28 46 9 64 18V42H2Z" fill="#64acff22" />
      <path
        d="M2 31L17 23 31 28 46 9 64 18"
        fill="none"
        stroke="#64acff"
        strokeWidth="2"
      />
      <path d="M2 38L17 32 31 13 46 23 64 21V42H2Z" fill="#50d5b020" />
      <path
        d="M2 38L17 32 31 13 46 23 64 21"
        fill="none"
        stroke="#50d5b0"
        strokeWidth="2"
      />
    </svg>
  );
}

function TimelineExplorer({ data }: { data: TimelineDetail }) {
  const [mode, setMode] = useState<"history" | "current">("history");
  const [units, setUnits] = useState<Units>("percent");
  return (
    <>
      <section className="glass timeline-panel">
        <header className="timeline-company-head timeline-editorial-head">
          <div className="timeline-company">
            <div>
              <p className="eyebrow">ANALISIS EMITEN / {data.symbol}</p>
              <h2>{data.symbol}</h2>
              <p className="timeline-company-name">{data.name}</p>
            </div>
          </div>
          <div className="timeline-company-provenance">
            <span className="badge">Sumber: {data.source}</span>
            {data.preview && (
              <div className="timeline-preview-banner" role="note">
                <FlaskConical size={15} aria-hidden="true" />
                <p>
                  <strong>Pratinjau.</strong> Kelengkapan dan basis harga belum
                  terverifikasi.
                </p>
              </div>
            )}
          </div>
        </header>
        <div className="timeline-editorial-copy">
          <p className="eyebrow">01 / LINTASAN HARGA</p>
          <h3>Harga di sekitar ex-date.</h3>
          <p>
            Bandingkan peristiwa dividen pada garis waktu yang sama. Pilih tahun
            untuk membaca detailnya.
          </p>
        </div>
        <TimelinePlot
          periods={mode === "history" ? data.history : data.current}
          units={units}
          setUnits={setUnits}
          mode={mode}
          setMode={setMode}
          currentYear={data.current_year}
          symbol={data.symbol}
          current={mode === "current"}
        />
        {mode === "current" && (
          <div className="timeline-forecast">
            <div>
              <p className="eyebrow">PERIODE BERJALAN / DATA AKTUAL</p>
              <h3>Grafik berhenti di harga terakhir.</h3>
              <p>Belum ada proyeksi untuk pergerakan setelah titik tersebut.</p>
            </div>
          </div>
        )}
      </section>
      <details className="glass timeline-audit">
        <summary>
          <CheckCheck size={17} /> Sumber & kelengkapan data{" "}
          <span className="muted">
            {data.preview ? "Perlu verifikasi" : "Lengkap"}
          </span>
        </summary>
        <div className="timeline-audit-body">
          <ul>
            {data.issues.map((issue) => (
              <li key={issue}>{tradingDayText(issue)}</li>
            ))}
          </ul>
          <p>
            Harga ditampilkan sesuai snapshot Sectors. Normalisasi terhadap
            cum-date membantu membandingkan pola; tidak membuktikan basis stock
            split sudah sama. Tahun mengikuti ex-date, bukan tahun buku. Grafik
            ini bukan proyeksi keuntungan strategi.
          </p>
          <p>
            Setiap seri mewakili satu pembayaran tercatat; klasifikasi
            final/interim belum disahkan. RUPS dan declaration yang belum
            tersedia tidak diganti dengan tanggal lain.
          </p>
          <p className="tiny muted">
            Referensi snapshot:{" "}
            {[
              ...new Set(
                [...data.history, ...data.current].flatMap((p) => p.sources),
              ),
            ].join(" · ")}
          </p>
        </div>
      </details>
    </>
  );
}

function TimelinePlot({
  periods,
  units,
  setUnits,
  mode,
  setMode,
  currentYear,
  symbol,
  current,
}: {
  periods: TimelinePeriod[];
  units: Units;
  setUnits: (u: Units) => void;
  mode: "history" | "current";
  setMode: (m: "history" | "current") => void;
  currentYear: number;
  symbol: string;
  current: boolean;
}) {
  const container = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(800);
  const [pinned, setPinned] = useState<number | null>(null);
  const [legendYear, setLegendYear] = useState<number | null>(null);
  const [hover, setHover] = useState<Hover | null>(null);
  useEffect(() => {
    const el = container.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) =>
      setWidth(Math.max(260, entries[0].contentRect.width)),
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  const available = periods.filter(
    (p) => p.points.length > 0 && (units === "price" || p.cum_close !== null),
  );
  const activeYear = pinned ?? legendYear ?? hover?.period.year ?? null;
  const active =
    available.find((p) => p.year === activeYear) ?? available.at(-1);
  const movement = cumExMovement(active);
  const left = width < 550 ? 58 : 72,
    right = width < 550 ? 18 : 28;
  const plotWidth = width - left - right;
  const value = (point: TimelinePoint) =>
    units === "price" ? point.close : point.change_pct;
  const allPoints = available.flatMap((p) => p.points);
  const values = allPoints.map(value).filter((v): v is number => v !== null);
  const minX = Math.min(-1, ...allPoints.map((p) => p.day));
  const maxX = Math.max(1, ...allPoints.map((p) => p.day));
  const low = Math.min(...values, ...(units === "percent" ? [0] : []));
  const high = Math.max(...values, ...(units === "percent" ? [0] : []));
  const padding = (high - low || Math.abs(high) * 0.05 || 1) * 0.14;
  const minY = low - padding,
    maxY = high + padding;
  const x = (day: number) => left + ((day - minX) / (maxX - minX)) * plotWidth;
  // Keep nearby dates at their true x positions; move only their labels into lanes.
  const phaseLayout = (period: TimelinePeriod | undefined) => {
    const laneEnds: number[] = [];
    return (period?.phases ?? [])
      .filter(
        (phase) => phase.day !== null && phase.day >= minX && phase.day <= maxX,
      )
      // On narrow screens the full chronology below keeps the other dates visible.
      .filter(
        (phase) =>
          width >= 550 ||
          phase.key === "cum_date" ||
          phase.key === "ex_date",
      )
      .toSorted((a, b) => a.day! - b.day!)
      .map((phase) => {
        const label = phaseLabel(phase.key, phase.label);
        const labelWidth = Math.max(84, label.length * 7.5 + 20);
        const labelX = Math.max(
          left,
          Math.min(width - right - labelWidth, x(phase.day!) - labelWidth / 2),
        );
        let lane = laneEnds.findIndex((end) => end + 10 <= labelX);
        if (lane === -1) lane = laneEnds.length;
        laneEnds[lane] = labelX + labelWidth;
        return { ...phase, label, labelX, labelWidth, labelY: 10 + lane * 34 };
      });
  };
  const annotations = phaseLayout(active);
  // Reserve the same label space for every year so hover cannot shift the plot.
  const top = Math.max(
    30,
    ...available.flatMap((period) =>
      phaseLayout(period).map((label) => label.labelY + 44),
    ),
  );
  const height = (width < 550 ? 430 : 540) + top - 30;
  const bottom = height - 54;
  const y = (v: number) =>
    bottom - ((v - minY) / (maxY - minY)) * (bottom - top);
  const line = (p: TimelinePeriod) =>
    p.points
      .filter((point) => value(point) !== null)
      .map(
        (point, i) =>
          `${i ? "L" : "M"}${x(point.day).toFixed(2)},${y(value(point)!).toFixed(2)}`,
      )
      .join(" ");
  const reset = () => {
    setPinned(null);
    setLegendYear(null);
    setHover(null);
  };
  const switchMode = (next: "history" | "current") => {
    if (next === mode) return;
    reset();
    setMode(next);
  };
  function closestAt(
    event: PointerEvent<SVGSVGElement> | MouseEvent<SVGSVGElement>,
  ): Hover | null {
    const rect = event.currentTarget.getBoundingClientRect();
    const pointerX = ((event.clientX - rect.left) * width) / rect.width;
    const pointerY = ((event.clientY - rect.top) * height) / rect.height;
    if (
      pointerX < left ||
      pointerX > width - right ||
      pointerY < top ||
      pointerY > bottom
    ) {
      return null;
    }
    let closest: Hover | null = null;
    let distance = Infinity;
    for (const period of available) {
      if (pinned !== null && period.year !== pinned) continue;
      const point = period.points.reduce((a, b) =>
        Math.abs(x(a.day) - pointerX) < Math.abs(x(b.day) - pointerX) ? a : b,
      );
      const v = value(point);
      if (v === null) continue;
      const d = Math.hypot(x(point.day) - pointerX, y(v) - pointerY);
      if (d < distance) {
        distance = d;
        closest = { period, point };
      }
    }
    return closest;
  }
  function onPointerMove(event: PointerEvent<SVGSVGElement>) {
    const closest = closestAt(event);
    if (closest) setLegendYear(null);
    setHover(closest);
  }
  function onChartClick(event: MouseEvent<SVGSVGElement>) {
    const closest = closestAt(event);
    if (!closest) return;
    if (pinned !== null) {
      reset();
      return;
    }
    setPinned(closest.period.year);
    setLegendYear(null);
    setHover(closest);
  }
  const observed =
    hover && (pinned === null || hover.period.year === pinned) ? hover : null;
  const tooltipLeft = observed
    ? Math.min(
        Math.max(0, x(observed.point.day) - 90),
        Math.max(0, width - 200),
      )
    : 0;
  const years = available.map((p) => p.year);
  const ticks = Array.from(
    new Set([
      minX,
      ...Array.from({ length: width < 550 ? 3 : 5 }, (_, i) =>
        Math.round(minX + ((maxX - minX) * (i + 1)) / (width < 550 ? 4 : 6)),
      ),
      0,
      maxX,
    ]),
  )
    .sort((a, b) => a - b)
    .filter(
      (v, i, a) =>
        v === 0 ||
        !a.some(
          (other, j) =>
            j !== i && other === 0 && Math.abs(x(v) - x(other)) < 35,
        ),
    );
  return (
    <>
      <div className="timeline-chart-stage">
        <div className="timeline-toolbar">
          <div className="timeline-controls">
            <div
              className="timeline-segment"
              role="group"
              aria-label="Rentang timeline"
            >
              <button
                aria-pressed={mode === "history"}
                onClick={() => switchMode("history")}
              >
                Histori 2021–2025
              </button>
              <button
                aria-pressed={mode === "current"}
                onClick={() => switchMode("current")}
              >
                {currentYear} <span>Aktual</span>
              </button>
            </div>
            <div
              className="timeline-segment compact"
              role="group"
              aria-label="Satuan harga"
            >
              <button
                aria-pressed={units === "percent"}
                onClick={() => setUnits("percent")}
              >
                Perubahan %
              </button>
              <button
                aria-pressed={units === "price"}
                onClick={() => setUnits("price")}
              >
                Harga Rp
              </button>
            </div>
          </div>
          <div className="timeline-legend" aria-label="Fokus periode">
            <div>
              {years.map((year) => (
                <button
                  key={year}
                  style={{ "--year-color": color(year) } as React.CSSProperties}
                  className={activeYear === year ? "focused" : ""}
                  aria-pressed={pinned === year}
                  aria-label={`Fokus tahun ${year}`}
                  onMouseEnter={() => setLegendYear(year)}
                  onMouseLeave={() => setLegendYear(null)}
                  onFocus={() => setLegendYear(year)}
                  onBlur={() => setLegendYear(null)}
                  onClick={() => {
                    setPinned(pinned === year ? null : year);
                    setHover(null);
                  }}
                >
                  <i />
                  {year}
                  {pinned === year && <LockKeyhole size={13} />}
                </button>
              ))}
            </div>
            {pinned !== null && (
              <button className="text-button small" onClick={reset}>
                Bandingkan semua
              </button>
            )}
          </div>
        </div>
        <div className="timeline-status-bar timeline-insight-grid">
          {active ? (
            <div
              className="timeline-cum-ex"
              data-direction={movement?.direction ?? "unavailable"}
              style={{ color: movement?.color }}
            >
              <span className="timeline-range-key" aria-hidden="true" />
              <span>Cum → Ex · {active.year}</span>
              <strong>
                {movement
                  ? `${movement.changePct > 0 ? "+" : ""}${pct(movement.changePct)}`
                  : "Harga belum lengkap"}
              </strong>
              <span className="muted">perubahan harga penutupan</span>
            </div>
          ) : (
            <div />
          )}
          <div className="timeline-chart-meta">
            <span>
              {units === "price"
                ? "Harga penutupan (Rp) · basis sumber"
                : "Perubahan harga dari close cum-date (%)"}
            </span>
            <span>
              {pinned
                ? `Fokus ${pinned} terkunci · pilih lagi untuk melepas`
                : "Pilih tahun atau titik grafik untuk fokus"}
            </span>
          </div>
        </div>
        <div ref={container} className="timeline-chart-wrap">
          {available.length ? (
            <>
              <svg
                width="100%"
                height={height}
                viewBox={`0 0 ${width} ${height}`}
                role="img"
                aria-label={`Overlay harga ${symbol}, ${years.join(", ")}; ${units === "price" ? "rupiah" : "perubahan persen"}; hari kalender relatif ex-date`}
                onPointerMove={onPointerMove}
                onClick={onChartClick}
                onPointerLeave={() => setHover(null)}
              >
                <title>Harga historis {symbol} pada periode dividen</title>
                <desc>
                  Klik garis atau area grafik, atau pilih tahun pada tombol
                  legenda, untuk mengunci fokus dan membaca timeline tanggal di
                  bawah grafik. Klik grafik lagi untuk melepas fokus.
                </desc>
                {[0, 1, 2, 3, 4].map((i) => {
                  const v = minY + ((maxY - minY) * i) / 4;
                  return (
                    <g key={i}>
                      <line
                        x1={left}
                        x2={width - right}
                        y1={y(v)}
                        y2={y(v)}
                        stroke="#ffffff24"
                      />
                      <text
                        x={left - 9}
                        y={y(v) + 4}
                        textAnchor="end"
                        fill="#B9C6CB"
                        fontSize="12"
                      >
                        {new Intl.NumberFormat("id-ID", {
                          maximumFractionDigits: units === "price" ? 0 : 1,
                        }).format(v)}
                        {units === "percent" ? "%" : ""}
                      </text>
                    </g>
                  );
                })}
                {units === "percent" && (
                  <line
                    x1={left}
                    x2={width - right}
                    y1={y(0)}
                    y2={y(0)}
                    stroke="#F7F7F355"
                    strokeDasharray="3 4"
                  />
                )}
                {[...available]
                  .sort(
                    (a, b) =>
                      Number(a.year === activeYear) -
                      Number(b.year === activeYear),
                  )
                  .map((period) => {
                    const points = period.points.filter(
                      (p) => value(p) !== null,
                    );
                    const fade =
                      activeYear !== null && period.year !== activeYear;
                    return (
                      <g
                        key={period.id}
                        data-period={period.year}
                        opacity={fade ? 0.25 : 1}
                        className="timeline-series"
                      >
                        <path
                          d={`${line(period)} L${x(points.at(-1)!.day)},${bottom} L${x(points[0].day)},${bottom} Z`}
                          fill={color(period.year)}
                          fillOpacity={period.year === activeYear ? 0.06 : 0}
                        />
                        <path
                          d={line(period)}
                          stroke={color(period.year)}
                          strokeWidth={period.year === activeYear ? 3 : 2.1}
                          fill="none"
                          strokeLinejoin="round"
                        />
                      </g>
                    );
                  })}
                {movement &&
                  value(movement.cum) !== null &&
                  value(movement.ex) !== null && (
                    <g
                      data-cum-ex-area={movement.direction}
                      aria-label={`Area cum ke ex-date ${active?.year}: ${pct(movement.changePct)}`}
                    >
                      <rect
                        x={x(movement.cum.day)}
                        y={top}
                        width={x(movement.ex.day) - x(movement.cum.day)}
                        height={bottom - top}
                        fill={movement.color}
                        fillOpacity=".09"
                      />
                      <path
                        d={`${line({ ...active!, points: movement.points })} L${x(movement.ex.day)},${bottom} L${x(movement.cum.day)},${bottom} Z`}
                        fill={movement.color}
                        fillOpacity=".46"
                      />
                      <path
                        d={line({ ...active!, points: movement.points })}
                        fill="none"
                        stroke={movement.color}
                        strokeWidth="3"
                        strokeLinejoin="round"
                      />
                      {[movement.cum, movement.ex].map((point) => (
                        <circle
                          key={point.date}
                          cx={x(point.day)}
                          cy={y(value(point)!)}
                          r="3.3"
                          fill={movement.color}
                          stroke="#131E29"
                          strokeWidth="1.5"
                        />
                      ))}
                    </g>
                  )}
                {annotations.map((phase) => (
                  <path
                    key={phase.key}
                    d={`M${phase.labelX + phase.labelWidth / 2},${phase.labelY + 26} L${x(phase.day!)},${top - 5} V${bottom}`}
                    fill="none"
                    stroke={
                      phase.key === "ex_date" ? "#F7F7F3" : color(active!.year)
                    }
                    strokeOpacity={phase.key === "ex_date" ? 0.7 : 0.4}
                    strokeDasharray="3 4"
                  />
                ))}
                {annotations.map((phase) => (
                  <g key={phase.key} data-phase-label={phase.key}>
                    <title>
                      {phase.label} · {dt(phase.date, true)} · {active?.year}
                    </title>
                    <rect
                      x={phase.labelX}
                      y={phase.labelY}
                      width={phase.labelWidth}
                      height="26"
                      rx="3"
                      fill="#22303B"
                      stroke="#F7F7F344"
                    />
                    <text
                      x={phase.labelX + phase.labelWidth / 2}
                      y={phase.labelY + 18}
                      textAnchor="middle"
                      fill="#F7F7F3"
                      fontSize="12"
                    >
                      {phase.label}
                    </text>
                  </g>
                ))}
                {ticks.map((tick) => (
                  <text
                    key={tick}
                    x={x(tick)}
                    y={bottom + 23}
                    textAnchor="middle"
                    fill={tick === 0 ? "#F7F7F3" : "#B9C6CB"}
                    fontSize="12"
                  >
                    {dayLabel(tick)}
                  </text>
                ))}
                {observed && (
                  <g>
                    <line
                      x1={x(observed.point.day)}
                      x2={x(observed.point.day)}
                      y1={top}
                      y2={bottom}
                      stroke={color(observed.period.year)}
                      strokeDasharray="3 4"
                    />
                    <circle
                      cx={x(observed.point.day)}
                      cy={y(value(observed.point)!)}
                      r="4.5"
                      fill={color(observed.period.year)}
                      stroke="#131E29"
                      strokeWidth="2"
                    />
                  </g>
                )}
              </svg>
              {observed && (
                <div
                  role="status"
                  className="timeline-tooltip"
                  style={{
                    left: tooltipLeft,
                    top: top + 8,
                    borderColor: color(observed.period.year),
                  }}
                >
                  <strong>
                    <i style={{ background: color(observed.period.year) }} />
                    {observed.period.year} · {current ? "Aktual" : "Historis"}
                  </strong>
                  <span>
                    {dt(observed.point.date, true)} ·{" "}
                    {dayLabel(observed.point.day)}
                  </span>
                  <b>{money(observed.point.close)}</b>
                  <span>{pct(observed.point.change_pct)} dari cum-date</span>
                  <small>
                    {observed.period.phases
                      .filter((p) => p.date === observed.point.date)
                      .map((p) => phaseLabel(p.key, p.label))
                      .join(" · ") ||
                      (observed.point.day < 0
                        ? "Sebelum ex-date"
                        : "Setelah ex-date")}
                  </small>
                </div>
              )}
            </>
          ) : (
            <div className="empty">
              <h3>Harga periode ini belum tersedia</h3>
              <p>Grafik akan muncul setelah data aktual dimuat.</p>
            </div>
          )}
        </div>
        <p className="timeline-axis-note">
          Hari kalender relatif terhadap ex-date · H0 = ex-date · titik
          mengikuti harga penutupan yang tersedia
        </p>
      </div>
      {active && (
        <section
          className="timeline-chronology"
          aria-label={`Detail peristiwa ${active.year}`}
        >
          <div className="timeline-focus-heading">
            <p className="eyebrow">02 / DETAIL PERISTIWA</p>
            <h3>
              Jejak dividen{" "}
              <span style={{ color: color(active.year) }}>{active.year}</span>
            </h3>
            <span className="small muted">{active.cycle}</span>
          </div>
          <ol className="timeline-phase-track">
            {active.phases.map((phase) => (
              <li key={phase.key} className={phase.date ? "" : "unavailable"}>
                <span
                  className="phase-dot"
                  style={
                    phase.date ? { background: color(active.year) } : undefined
                  }
                />
                <strong>{phaseLabel(phase.key, phase.label)}</strong>
                <span>
                  {phase.date ? dt(phase.date, true) : "Belum tersedia"}
                </span>
                <small>
                  {phase.day !== null
                    ? dayLabel(phase.day)
                    : "Belum terverifikasi"}
                </small>
              </li>
            ))}
          </ol>
          <div className="timeline-readings">
            <div>
              <span>Dividen / saham</span>
              <strong>{money(active.dps)}</strong>
            </div>
            <div>
              <span>Close cum-date</span>
              <strong>{money(active.cum_close)}</strong>
            </div>
            <div>
              <span>Perubahan pada ex-date</span>
              <strong>
                {pct(active.points.find((p) => p.day === 0)?.change_pct)}
              </strong>
            </div>
            <div>
              <span>Data aktual terakhir</span>
              <strong>{dt(active.actual_through, true)}</strong>
            </div>
          </div>
          <details className="timeline-price-table">
            <summary>Lihat data harga {active.year}</summary>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Tanggal</th>
                    <th>Relatif ex</th>
                    <th>Close</th>
                    <th>Δ cum-date</th>
                  </tr>
                </thead>
                <tbody>
                  {active.points.map((point) => (
                    <tr key={point.date}>
                      <td>{dt(point.date, true)}</td>
                      <td>{dayLabel(point.day)}</td>
                      <td>{money(point.close)}</td>
                      <td>{pct(point.change_pct)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </section>
      )}
    </>
  );
}
