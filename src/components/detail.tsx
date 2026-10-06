"use client";
import { useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, CalendarDays, X } from "lucide-react";
import { api, dt, money, pct } from "@/lib/api";
import type { CompanyDetail, DividendEvent } from "@/lib/types";
import Chart, { lineOption } from "./chart";
export default function CompanyDialog({
  symbol,
  onClose,
  onSimulate,
  onIntelligence,
}: {
  symbol: string;
  onClose: () => void;
  onSimulate: (eventId: string) => void;
  onIntelligence: () => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const q = useQuery({
    queryKey: ["company", symbol],
    queryFn: () => api<CompanyDetail>(`/companies/${symbol}`),
  });
  useEffect(() => {
    ref.current?.showModal();
  }, []);
  const c = q.data;
  return (
    <dialog
      ref={ref}
      className="detail-dialog"
      aria-labelledby="detail-title"
      onClose={onClose}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="dialog-inner">
        <div className="section-head">
          <div>
            <p className="eyebrow">COMPANY RESEARCH</p>
            <h2 id="detail-title">
              {symbol} <span className="muted">/ Dividen & harga</span>
            </h2>
          </div>
          <button
            autoFocus
            className="icon-btn"
            onClick={onClose}
            aria-label="Tutup detail"
          >
            <X size={22} />
          </button>
        </div>
        {q.isPending && <div className="loading">Memuat emiten…</div>}
        {q.isError && (
          <div className="notice error" role="alert">
            {q.error.message}
          </div>
        )}
        {c && (
          <>
            <p className="muted">{c.name}</p>
            <div className="detail-stats">
              <div>
                <small>Yield tahunan 2025</small>
                <strong>{pct(c.annual_yield_pct)}</strong>
              </div>
              <div>
                <small>Total dividen / saham</small>
                <strong>{money(c.annual_dps)}</strong>
              </div>
              <div>
                <small>Frekuensi 2025</small>
                <strong>{c.frequency} kali</strong>
              </div>
            </div>
            <p className="tiny muted">
              Yield dan DPS tahunan mengikuti agregat Sectors. Keduanya bukan
              proyeksi keuntungan strategi.
            </p>
            <h3>Jejak harga historis</h3>
            {c.prices.length ? (
              <Chart
                label={`Harga penutupan historis ${symbol}`}
                option={lineOption(
                  c.prices.map((b) => b.date),
                  [
                    {
                      name: symbol,
                      values: c.prices.map((b) => b.close),
                      color: "#ca82a8",
                    },
                  ],
                )}
              />
            ) : (
              <div className="notice">
                Harga historis emiten ini belum dimuat. Timeline dan dividen
                tetap dapat ditinjau.
              </div>
            )}
            <div className="section-head">
              <h3>Timeline dividen 2025</h3>
              <CalendarDays size={18} />
            </div>
            {c.events.map((e) => (
              <div className="event-timeline" key={e.id}>
                <div className="spread">
                  <strong>
                    {money(e.dps)}{" "}
                    <span className="muted small">per saham</span>
                  </strong>
                  <span className={`badge ${e.replay_available ? "good" : ""}`}>
                    {e.replay_available
                      ? "Data replay tersedia"
                      : "Jadwal / harga belum lengkap"}
                  </span>
                </div>
                <Timeline event={e} />
                <button
                  className="btn subtle"
                  disabled={!e.replay_available}
                  onClick={() => onSimulate(e.id)}
                  aria-label={`Simulasikan ${symbol}, ex-date ${dt(e.ex_date, true)}`}
                >
                  Simulasikan event ini <ArrowUpRight size={15} />
                </button>
                <small className="muted source-line">
                  Sumber: Sectors · {e.source}
                </small>
              </div>
            ))}
            <h3>Riwayat pembagian</h3>
            <p className="tiny muted">
              Tahun 2022–2025. DPS mengikuti basis tahun sumber; seri ini belum
              disesuaikan untuk seluruh stock split.
            </p>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Tahun</th>
                    <th>DPS</th>
                    <th>Yield sumber</th>
                    <th>Frekuensi</th>
                  </tr>
                </thead>
                <tbody>
                  {c.history
                    .filter((h) => h.year >= 2022 && h.year <= 2025)
                    .slice(-6)
                    .reverse()
                    .map((h) => (
                      <tr key={h.year}>
                        <td>{h.year}</td>
                        <td>{money(h.dps)}</td>
                        <td>{pct(h.yield_pct)}</td>
                        <td>{h.frequency}×</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            {c.research ? (
              <div className="research-block">
                <p className="eyebrow">RECOVERY STUDY / BBCA</p>
                <h3>Harga pulih tidak selalu berarti modal bebas risiko.</h3>
                <div className="detail-stats">
                  <div>
                    <small>Event diteliti</small>
                    <strong>{c.research.n_events}</strong>
                  </div>
                  <div>
                    <small>Pulih ≤20 sesi</small>
                    <strong>
                      {c.research.price_bep_recovered_by_t20} /{" "}
                      {c.research.n_events}
                    </strong>
                  </div>
                  <div>
                    <small>Belum pulih ≤20 sesi</small>
                    <strong>
                      {c.research.price_bep_censored_at_t20} /{" "}
                      {c.research.n_events}
                    </strong>
                  </div>
                </div>
                <p className="small muted">
                  Entry pada close cum-date. Pemulihan memakai close ≥ harga
                  entry. {c.research.ex_gross_negative_count} dari{" "}
                  {c.research.n_events} event masih rugi setelah memasukkan hak
                  dividen pada close ex-date. Sampel 2022–2025; bukan
                  probabilitas masa depan.
                </p>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Ex-date</th>
                        <th>BEP harga</th>
                        <th>BEP total</th>
                        <th>Return total t+20</th>
                      </tr>
                    </thead>
                    <tbody>
                      {c.research.events.map((e, i) => (
                        <tr key={i}>
                          <td>{dt(String(e.ex_date), true)}</td>
                          <td>
                            {e.price_bep_offset == null
                              ? "Belum pulih"
                              : `${e.price_bep_offset} sesi`}
                          </td>
                          <td>
                            {e.gross_total_bep_offset == null
                              ? "Belum pulih"
                              : `${e.gross_total_bep_offset} sesi`}
                          </td>
                          <td>{pct(Number(e.t20_gross_total_return) * 100)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="notice">
                  Event yang belum pulih tetap masuk perhitungan. Median{" "}
                  {c.research.median_recovery_offset_among_recovered_only} sesi
                  hanya untuk event yang sudah pulih; bukan estimasi waktu
                  tunggu semua posisi.
                </div>
              </div>
            ) : (
              <div className="notice">
                Statistik sampel, audit kelayakan, dan pemulihan {symbol}{" "}
                tersedia di Intelligence. Probabilitas prediksi terkalibrasi
                belum tersedia.
              </div>
            )}
            <button className="btn subtle full" onClick={onIntelligence}>
              Buka Intelligence {symbol} <ArrowUpRight size={17} />
            </button>
          </>
        )}
      </div>
    </dialog>
  );
}
function Timeline({ event: e }: { event: DividendEvent }) {
  return (
    <ol className="timeline">
      {[
        { name: "Declaration", value: e.declaration_date },
        { name: "Cum date", value: e.cum_date },
        { name: "Ex-date", value: e.ex_date },
        { name: "Recording", value: e.recording_date },
        { name: "Payment", value: e.payment_date },
      ].map((s, i) => (
        <li className={!s.value ? "unknown" : ""} key={s.name}>
          <span className="timeline-dot">{i + 1}</span>
          <strong>{s.name}</strong>
          <small>{dt(s.value, true)}</small>
        </li>
      ))}
    </ol>
  );
}
