export type TimelinePoint = {
  date: string;
  day: number;
  close: number;
  change_pct: number | null;
};
export type TimelinePhase = {
  key: string;
  label: string;
  date: string | null;
  day: number | null;
  status: "recorded" | "unavailable";
};
export type TimelinePeriod = {
  id: string;
  year: number;
  ex_date: string;
  dps: number | null;
  cum_close: number | null;
  cycle: string;
  points: TimelinePoint[];
  phases: TimelinePhase[];
  sources: string[];
  actual_through: string | null;
  issues: string[];
  eligible: boolean;
};
export type TimelineCatalog = {
  history_years: number[];
  current_year: number;
  companies: { symbol: string; name: string }[];
  preview_symbols: string[];
  calendar_candidates: number;
  audited_symbols: number;
  source: string;
  reason: string;
};
export type TimelineDetail = {
  symbol: string;
  name: string;
  history: TimelinePeriod[];
  current: TimelinePeriod[];
  eligible: boolean;
  preview: boolean;
  history_years: number[];
  current_year: number;
  axis_unit: "calendar_days";
  source: string;
  issues: string[];
  forecast: {
    status: "not_available";
    points: TimelinePoint[];
    message: string;
  };
};
