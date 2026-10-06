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
): EChartsOption {
  return {
    animationDuration: 300,
    textStyle: { fontFamily: "Manrope", color: "#bdb0be" },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#271d29",
      borderColor: "#5d3a50",
      textStyle: { color: "#fff" },
      valueFormatter: (v) =>
        new Intl.NumberFormat("id-ID", { maximumFractionDigits: 0 }).format(
          Number(v),
        ),
    },
    grid: { left: 60, right: 18, top: 24, bottom: 30 },
    xAxis: {
      type: "category",
      data: dates.map((d) =>
        new Date(`${d}T12:00:00`).toLocaleDateString("id-ID", {
          day: "numeric",
          month: "short",
        }),
      ),
      axisLine: { lineStyle: { color: "#ffffff12" } },
      axisTick: { show: false },
      axisLabel: { color: "#9e929f", hideOverlap: true },
    },
    yAxis: {
      type: "value",
      scale: true,
      splitNumber: 4,
      axisLabel: {
        color: "#9e929f",
        formatter: (v: number) =>
          currency && Math.abs(v) >= 1e6
            ? `${(v / 1e6).toFixed(1)} jt`
            : new Intl.NumberFormat("id-ID").format(v),
      },
      splitLine: { lineStyle: { color: "#ffffff0a", type: "dashed" } },
    },
    series: series.map((s, i) => ({
      name: s.name,
      type: "line",
      data: s.values,
      showSymbol: false,
      smooth: false,
      lineStyle: { width: i === 0 ? 2.5 : 1.7, color: s.color },
      itemStyle: { color: s.color },
      areaStyle:
        series.length === 1
          ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "#a64d7940" },
                { offset: 1, color: "#a64d7900" },
              ]),
            }
          : undefined,
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
      aria-label="Tren 24 sesi historis terakhir"
    >
      <polyline
        fill="none"
        stroke="#c886aa"
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
