export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(
      typeof body?.detail === "string"
        ? body.detail
        : Array.isArray(body?.detail)
          ? body.detail
              .slice(0, 3)
              .map(
                (issue: { msg?: string }) => issue.msg ?? "Input tidak valid",
              )
              .join(". ")
          : `Permintaan gagal (${response.status}). Periksa input atau coba lagi.`,
    );
  }
  return response.json();
}
export const money = (value: number | null | undefined, compact = false) =>
  value == null
    ? "—"
    : new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0,
        maximumFractionDigits: compact ? 1 : 4,
        ...(compact ? { notation: "compact" as const } : {}),
      }).format(value);
export const pct = (value: number | null | undefined) =>
  value == null
    ? "—"
    : `${new Intl.NumberFormat("id-ID", { maximumFractionDigits: 2 }).format(value)}%`;
export const dt = (value: string | null | undefined, year = false) =>
  value
    ? new Date(`${value.slice(0, 10)}T12:00:00`).toLocaleDateString("id-ID", {
        day: "numeric",
        month: "short",
        ...(year ? { year: "numeric" } : {}),
      })
    : "Belum tersedia";
