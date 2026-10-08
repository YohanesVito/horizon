"use client";
import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import type { EChartsOption } from "echarts";
export default function Chart({
  option,
  label,
  height = 270,
}: {
  option: EChartsOption;
  label: string;
  height?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const el = ref.current;
    const chart = echarts.init(el, undefined, { renderer: "svg" });
    chart.setOption({
      ...option,
      animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    });
    const resize = new ResizeObserver(() => chart.resize());
    resize.observe(el);
    return () => {
      resize.disconnect();
      chart.dispose();
    };
  }, [option]);
  return (
    <div
      ref={ref}
      role="img"
      aria-label={label}
      style={{ height, width: "100%" }}
    />
  );
}
export function lineOption(
  dates: string[],
  series: { name: string; values: number[]; color: string }[],
  currency = true,
  markers: { date: string; label: string; color: string }[] = [],
): EChartsOption {
  const visibleMarkers = markers.flatMap((marker) => {
    const index = dates.indexOf(marker.date);
    return index < 0
      ? []
      : [{
          xAxis: index,
          lineStyle: { color: marker.color, type: "dashed" as const, width: 1.5 },
          label: {
            show: true,
            formatter: marker.label,
            position: "insideEndTop" as const,
            rotate: 0,
            offset: [marker.label === "Cum date" ? 25 : 0, marker.label === "Ex date" ? 26 : 0],
            color: "#131e29",
            backgroundColor: "#f7f7f3",
            borderColor: marker.color,
            borderWidth: 1,
            borderRadius: 4,
            padding: [3, 6],
            fontSize: 11,
            fontWeight: 600,
          },
        }];
  });
  return {
    animationDuration: 300,
    textStyle: { fontFamily: "Manrope", color: "#c4d0d5", fontSize: 13 },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#f7f7f3",
      borderColor: "#ff4713",
      textStyle: { color: "#131e29", fontSize: 13 },
      valueFormatter: (v) =>
        new Intl.NumberFormat("id-ID", { maximumFractionDigits: 0 }).format(
          Number(v),
        ),
    },
    grid: { left: 60, right: 18, top: visibleMarkers.length ? 44 : 24, bottom: 30 },
    xAxis: {
      type: "category",
      data: dates.map((d) =>
        new Date(`${d}T12:00:00`).toLocaleDateString("id-ID", {
          day: "numeric",
          month: "short",
        }),
      ),
      axisLine: { lineStyle: { color: "#ffffff2a" } },
      axisTick: { show: false },
      axisLabel: { color: "#b9c6cb", fontSize: 12, hideOverlap: true },
    },
    yAxis: {
      type: "value",
      scale: true,
      splitNumber: 4,
      axisLabel: {
        color: "#b9c6cb",
        fontSize: 12,
        formatter: (v: number) =>
          currency && Math.abs(v) >= 1e6
            ? `${(v / 1e6).toFixed(1)} jt`
            : new Intl.NumberFormat("id-ID").format(v),
      },
      splitLine: { lineStyle: { color: "#ffffff20", type: "dashed" } },
    },
    series: series.map((s, i) => ({
      name: s.name,
      type: "line",
      data: s.values,
      showSymbol: false,
      smooth: false,
      lineStyle: { width: i === 0 ? 2.5 : 1.7, color: s.color },
      itemStyle: { color: s.color },
      areaStyle: series.length === 1 ? { color: "#ff471326" } : undefined,
      ...(i === 0 && visibleMarkers.length
        ? {
            markLine: {
              silent: true,
              symbol: "none" as const,
              data: visibleMarkers,
            },
          }
        : {}),
    })),
  };
}
export function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2)
    return <span className="muted tiny">Harga belum dimuat</span>;
  const low = Math.min(...values),
    range = Math.max(...values) - low || 1;
  return (
    <svg
      width="96"
      height="30"
      viewBox="0 0 96 30"
      role="img"
      aria-label="Tren 24 hari bursa historis terakhir"
    >
      <polyline
        fill="none"
        stroke="#ff4713"
        strokeWidth="1.6"
        points={values
          .map(
            (v, i) =>
              `${(i / (values.length - 1)) * 96},${26 - ((v - low) / range) * 22}`,
          )
          .join(" ")}
      />
    </svg>
  );
}
