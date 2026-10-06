import type { FinancialLogic, RankingRow } from "./intelligence-types";
import type { Replay, SimInput } from "./types";

export interface RotationInput {
  capital: number | string;
  start_date: string;
  end_date: string;
  symbols: string[];
  rules: FinancialLogic;
  exit_rule: SimInput["exit_rule"];
  max_holding_sessions: number;
  max_events: number;
  allow_calendar_assumption: boolean;
}
export interface Candidate {
  event_id: string;
  symbol: string;
  entry_date: string | null;
  cum_date: string;
  ex_date: string;
  payment_date: string;
  dps: number;
  calendar_status: "verified" | "assumed" | "unknown";
  planned_exit_bound: string | null;
  planned_cash_release: string | null;
  reasons: string[];
  evidence: RankingRow | null;
  evidence_event_ids: string[];
  evidence_latest_observation: string | null;
}
export interface RotationPlan {
  id: string;
  created_at: string;
  version: string;
  dataset_version: string;
  evidence_dataset_version: string;
  decision_date: string;
  input: RotationInput;
  ranking: { ranked: RankingRow[]; excluded: RankingRow[] };
  candidates: Candidate[];
  excluded: Candidate[];
  routes: {
    id: string;
    name: string;
    event_ids: string[];
    steps: Candidate[];
    omitted: { event_id: string; reason: string }[];
    also_matches: string[];
    method: string;
  }[];
  assumptions: string[];
}
export interface RotationRun {
  id: string;
  plan_id: string;
  status: "queued" | "running" | "completed" | "failed";
  created_at: string;
  input: RotationInput;
  error?: string;
  result?: {
    routes: {
      route_id: string;
      name: string;
      comparison: { primary: Replay; alternatives: Replay[] };
    }[];
    cash_baseline: {
      capital: number;
      ending_nav: number;
      gross_pnl: number;
      start_date: string;
      end_date: string;
    };
    assumptions: string[];
    dataset_version: string;
  };
}
