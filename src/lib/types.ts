export interface DividendEvent {
  id: string;
  symbol: string;
  declaration_date: string | null;
  cum_date: string | null;
  ex_date: string;
  recording_date: string | null;
  payment_date: string | null;
  dps: number | null;
  source_yield_pct: number | null;
  entry_reference: number | null;
  replay_available: boolean;
  quality: string;
  source: string;
}
export interface Company {
  symbol: string;
  name: string;
  annual_yield_pct: number | null;
  annual_dps: number | null;
  frequency: number;
  year: number;
  history: {
    year: number;
    dps: number | null;
    yield_pct: number | null;
    frequency: number;
  }[];
  events: DividendEvent[];
  replay_available: boolean;
  price: number | null;
  price_date: string | null;
  sparkline: number[];
}
export interface Bar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
export interface Study {
  n_events: number;
  price_bep_recovered_by_t20: number;
  price_bep_censored_at_t20: number;
  ex_gross_negative_count: number;
  median_recovery_offset_among_recovered_only: number;
  events: Record<string, unknown>[];
}
export interface CompanyDetail extends Company {
  prices: Bar[];
  research: Study | null;
}
export interface Catalog {
  companies: Company[];
  events: DividendEvent[];
  meta: {
    provider: string;
    mode: string;
    year: number;
    retrieved_at: string;
    price_window: string[];
    yield_basis: string;
    cost_label: string;
    dataset_version: string;
    replay_start?: string;
    replay_end?: string;
    session_repairs?: string[];
  };
}
export interface Rules {
  name: string;
  minimum_yield: number;
  minimum_frequency: number;
  require_replay: boolean;
  sort_by: "yield" | "frequency" | "symbol";
  version?: string;
}
export type Allocation = "rotation" | "equal" | "single";
export interface SimInput {
  timing_mode?: "custom" | "payment_plus_2";
  capital: number;
  event_ids: string[];
  allocation: Allocation;
  entry_sessions_before_cum: number;
  exit_rule: "ex_close" | "payment_close" | "price_bep" | "holding_period";
  max_holding_sessions: number;
  end_date: string;
  start_date?: string;
  compare: boolean;
}
export interface PositionExtreme {
  date: string;
  price: number;
  position_value: number;
  total_value: number;
  pnl: number;
  return_pct: number;
}
export interface PositionObservation {
  cum_date: string | null;
  ex_date: string;
  payment_date: string | null;
  end_date: string | null;
  available_end_date: string | null;
  horizon_sessions: number;
  complete: boolean;
  gaps: string[];
  invested: number;
  shares: number;
  dividend_amount: number;
  dividend_per_share: number;
  points: {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    dividend_entitled: number;
    dividend_paid: number;
    position_value: number;
    total_value: number;
  }[];
  highest: PositionExtreme | null;
  lowest: PositionExtreme | null;
}
export interface Trade {
  event_id: string;
  symbol: string;
  status: string;
  shares: number;
  entry_date: string;
  entry_price: number;
  entry_price_basis?: "prior5_close_mean";
  entry_reference_dates?: string[];
  exit_date: string | null;
  exit_price: number | null;
  settlement_date: string | null;
  payment_date: string | null;
  dividend: number;
  capital_pnl: number;
  gross_pnl: number;
  reason: string;
  signal_date: string | null;
  capital_days: number;
  observation?: PositionObservation;
  residual_cash?: number;
  end_valuation?: {
    date: string;
    position_value: number;
    dividend_entitled: number;
    dividend_paid: number;
    total_value: number;
    pnl: number;
    return_pct: number;
  };
}
export interface Replay {
  analysis_mode?: "independent_events";
  allocation: Allocation;
  capital: number;
  start_date: string;
  end_date: string;
  ending_nav: number;
  ending_cash: number;
  remaining_positions: number;
  pending_sales: number;
  pending_dividends: number;
  gross_pnl: number;
  return_pct: number;
  dividends: number;
  max_drawdown_pct: number;
  trades: Trade[];
  ledger: {
    date: string;
    kind: string;
    symbol: string;
    amount: number;
    detail: string;
  }[];
  curve: {
    date: string;
    nav: number;
    cash: number;
    positions: number;
    sale_receivable: number;
    dividend_receivable: number;
  }[];
  assumptions: string[];
  rules_version: string;
  dataset_version?: string;
  open_below_entry?: number;
  missed_events?: { event_id: string; reason: string }[];
  omitted_by_plan?: { event_id: string; reason: string }[];
}
export interface Run {
  id: string;
  status: "queued" | "running" | "completed" | "failed";
  created_at: string;
  dataset_version?: string;
  input: SimInput;
  error?: string;
  result?: { primary: Replay; alternatives: Replay[]; input: SimInput };
}
