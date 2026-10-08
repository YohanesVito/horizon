"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { api, money, pct } from "@/lib/api";

type Inputs = {
  capital_idr: string;
  entry_price: string;
  dps: string;
  assumed_ex_price: string;
};

type ScenarioResult = {
  status: "scenario";
  lots: number;
  shares: number;
  invested_idr: number;
  remaining_cash_idr: number;
  capital_pnl_idr: number;
  dividend_idr: number;
  gross_pnl_idr: number;
  gross_return_pct: number;
  price_bep_idr: number;
  total_bep_idr: number;
  total_bep_reached: boolean;
  label: string;
};

const INITIAL: Inputs = {
  capital_idr: "",
  entry_price: "",
  dps: "",
  assumed_ex_price: "",
};

export default function ExDateScenario({ symbol }: { symbol: string }) {
  const [values, setValues] = useState<Inputs>(INITIAL);
  const run = useMutation({
    mutationFn: (input: Record<keyof Inputs, number>) =>
      api<ScenarioResult>("/ex-date/scenario", {
        method: "POST",
        body: JSON.stringify(input),
      }),
  });

  const update = (key: keyof Inputs, value: string) => {
    setValues((current) => ({ ...current, [key]: value }));
    run.reset();
  };
  const fillFullDps = () => {
    const entry = Number(values.entry_price);
    const dps = Number(values.dps);
    if (entry > dps && dps > 0) update("assumed_ex_price", String(entry - dps));
  };
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    run.mutate({
      capital_idr: Number(values.capital_idr),
      entry_price: Number(values.entry_price),
      dps: Number(values.dps),
      assumed_ex_price: Number(values.assumed_ex_price),
    });
  };

  return (
    <section className="glass ex-date-scenario" aria-labelledby="ex-scenario-title">
      <div className="ex-date-scenario-heading">
        <div>
          <p className="eyebrow">03 / SKENARIO EX-DATE · {symbol}</p>
          <h3 id="ex-scenario-title">Uji asumsi harga dan dividenmu.</h3>
        </div>
        <span className="badge">Skenario · bukan prediksi</span>
      </div>
      <p className="muted">
        Masukkan angka sendiri. Grafik di atas adalah snapshot historis dan tidak
        mengisi harga atau DPS periode mendatang. Simulasi menganggap kamu membeli
        sebelum cum-date, berhak atas dividen, lalu menjual pada harga ex-date asumsi.
      </p>
      <form onSubmit={submit}>
        <div className="ex-date-scenario-inputs">
          {([
            ["capital_idr", "Modal (Rp)"],
            ["entry_price", "Harga beli per saham (Rp)"],
            ["dps", "Dividen per saham / DPS (Rp)"],
            ["assumed_ex_price", "Harga jual ex-date asumsi (Rp)"],
          ] as const).map(([key, label]) => (
            <label key={key}>
              <span>{label}</span>
              <input
                type="number"
                inputMode="decimal"
                min="0.01"
                step="0.01"
                required
                value={values[key]}
                onChange={(event) => update(key, event.target.value)}
                placeholder="Isi asumsi"
              />
            </label>
          ))}
        </div>
        <div className="ex-date-scenario-actions">
          <button type="button" className="btn subtle" onClick={fillFullDps}
            disabled={!(Number(values.entry_price) > Number(values.dps) && Number(values.dps) > 0)}>
            Isi contoh harga beli − DPS
          </button>
          <button type="submit" className="btn primary" disabled={run.isPending}>
            {run.isPending ? "Menghitung…" : "Hitung skenario"}
          </button>
        </div>
      </form>
      {run.isError && <p className="notice error" role="alert">{run.error.message}</p>}
      {run.data && (
        <div className="ex-date-scenario-results" aria-live="polite">
          <dl>
            <div><dt>Saham yang dapat dibeli</dt><dd>{run.data.shares.toLocaleString("id-ID")} ({run.data.lots} lot)</dd></div>
            <div><dt>Modal terpakai / sisa</dt><dd>{money(run.data.invested_idr)} / {money(run.data.remaining_cash_idr)}</dd></div>
            <div><dt>Perubahan harga</dt><dd>{money(run.data.capital_pnl_idr)}</dd></div>
            <div><dt>Dividen bruto</dt><dd>{money(run.data.dividend_idr)}</dd></div>
            <div className="ex-date-scenario-total"><dt>Hasil gross</dt><dd>{money(run.data.gross_pnl_idr)} · {pct(run.data.gross_return_pct)}</dd></div>
            <div><dt>BEP harga / BEP total</dt><dd>{money(run.data.price_bep_idr)} / {money(run.data.total_bep_idr)}</dd></div>
          </dl>
          <p>{run.data.label}</p>
        </div>
      )}
    </section>
  );
}
