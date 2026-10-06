export interface FinancialLogic {
  name: string;
  entry_offset: 0 | 5 | 10;
  horizon: 5 | 10 | 20;
  objective: "return" | "worst_return" | "risk" | "recovery";
  minimum_samples: number;
  maximum_loss_upper_pct: number;
  minimum_median_return_pct: number;
  saved_at?: string;
}
export interface Recovery {
  median_sessions: number | null;
  curve: {
    session: number;
    at_risk: number;
    recovered: number;
    censored: number;
    recovery_pct: number | null;
  }[];
}
export interface Observation {
  id: string;
  symbol: string;
  ex_date: string;
  cum_date: string | null;
  payment_date: string | null;
  dps: number;
  eligible: boolean;
  complete?: boolean;
  entry_date?: string;
  entry_price?: number;
  last_date?: string;
  gross_return_pct?: number | null;
  price_bep_session?: number | null;
  total_bep_session?: number | null;
  observed_sessions?: number;
  reasons: string[];
  warnings: string[];
  sources: string[];
}
export interface Evidence {
  symbol: string;
  total_events: number;
  eligible_events: number;
  complete_events: number;
  excluded_events: number;
  early_censored: number;
  price_unrecovered: number;
  total_unrecovered: number;
  losses: number;
  trap_pct: number | null;
  trap_interval: [number, number] | null;
  median_return_pct: number | null;
  worst_return_pct: number | null;
  price_recovery: Recovery;
  total_recovery: Recovery;
  temporal: { period: string; n: number; trap_pct: number | null }[];
  period: [string, string] | null;
  events: Observation[];
}
export interface RankingRow {
  symbol: string;
  rank?: number;
  complete_events: number;
  trap_pct: number | null;
  trap_interval: [number, number] | null;
  median_return_pct: number | null;
  worst_return_pct: number | null;
  median_recovery_sessions: number | null;
  reasons: string[];
}
export interface IntelligenceData {
  version: string;
  dataset_version: string;
  entry_offset: number;
  horizon: number;
  rules: FinancialLogic;
  ranking: { ranked: RankingRow[]; excluded: RankingRow[] };
  companies: Evidence[];
  audit: {
    symbols: number;
    events: number;
    eligible: number;
    complete: number;
    excluded: number;
  };
  limitations: string[];
  sources: {
    file: string;
    retrieved_at: string;
    tool: string;
    sha256: string;
  }[];
}
export interface ScenarioInput {
  symbol: string;
  capital: number | string;
  entry_price: number | string;
  dps: number | string;
  entry_date: string;
  cum_date: string;
  ex_date: string;
  recording_date: string;
  payment_date: string;
  valuation_date: string;
  entry_offset: number;
  horizon: number;
}
export interface ScenarioRun {
  id: string;
  created_at: string;
  input: ScenarioInput;
  result: {
    symbol: string;
    analog_count: number;
    shares: number;
    uninvested_cash: number;
    dividend_entitlement: number;
    dividend_cash: number;
    dividend_receivable: number;
    price_bep: number;
    total_bep: number;
    loss_scenarios: number;
    pnl: {
      worst: number;
      p10: number;
      median: number;
      p90: number;
      best: number;
    };
    trajectory: { session: number; p10: number; median: number; p90: number }[];
    worst_observed_pnl: number;
    dataset_version: string;
    version: string;
    assumptions: string[];
    rows: {
      event_id: string;
      ex_date: string;
      exit_price: number;
      capital_gain: number;
      dividend: number;
      gross_pnl: number;
      gross_return_pct: number;
      ending_value: number;
    }[];
  };
}
