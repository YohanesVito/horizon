import type { TimelinePeriod } from "./timeline-types";

export function cumExMovement(period: TimelinePeriod | undefined) {
  if (!period) return null;
  const cumDate = period.phases.find((phase) => phase.key === "cum_date")?.date;
  const cum = period.points.find((point) => point.date === cumDate);
  const ex = period.points.find((point) => point.date === period.ex_date);
  if (
    !cum ||
    !ex ||
    !Number.isFinite(cum.close) ||
    !Number.isFinite(ex.close) ||
    cum.close <= 0 ||
    ex.close <= 0 ||
    cum.day >= ex.day
  )
    return null;
  const change = ex.close - cum.close;
  const direction = change < 0 ? "down" : change > 0 ? "up" : "flat";
  return {
    cum,
    ex,
    direction,
    changePct: (change / cum.close) * 100,
    color:
      direction === "down"
        ? "#f17786"
        : direction === "up"
          ? "#51d6a0"
          : "#b6a7ba",
    points: period.points.filter(
      (point) => point.day >= cum.day && point.day <= ex.day,
    ),
  };
}

export function phaseLabel(key: string, fallback: string) {
  return (
    (
      {
        cum_date: "Cum date",
        ex_date: "Ex date",
        recording_date: "Recording",
        payment_date: "Payment",
      } as Record<string, string>
    )[key] ?? fallback
  );
}
