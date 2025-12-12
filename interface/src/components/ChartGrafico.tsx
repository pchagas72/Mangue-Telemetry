import { useEffect, useRef } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";

interface ChartMultivariavelProps {
  titulo: string;
  timestamps: number[];
  series: {
    label: string;
    valores: number[];
    cor?: string;
  }[];
}

export function ChartGrafico({ titulo, timestamps, series }: ChartMultivariavelProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const uplotRef = useRef<uPlot | null>(null);

  const data: (number[] | undefined)[] = [
    timestamps,
    ...series.map((s) => s.valores),
  ];

  useEffect(() => {
    if (!chartRef.current) return;

    const initWidth = chartRef.current.clientWidth;
    const initHeight = chartRef.current.clientHeight;

    const opts: uPlot.Options = {
      title: "", 
      width: initWidth,
      height: initHeight,
      series: [
        {
          label: "Time",
          // Safety Check: if 'v' isn't a valid timestamp, just show it as a number
          value: (_u, v) => {
              if (v == null) return "--";
              const d = new Date(v);
              // If invalid date OR small number (likely relative seconds, < 1973), format as float
              if (isNaN(d.getTime()) || v < 100000000000) return v.toFixed(2) + "s";
              return d.toLocaleTimeString('en-US', { hour12: false });
          },
        },
        ...series.map((s) => ({
          label: s.label,
          stroke: s.cor || "#00ADB5",
          width: 2,
          points: { show: false }, 
        })),
      ],
      axes: [
        {
          label: "TIME",
          labelSize: 20,
          labelFont: "10px 'Consolas'",
          grid: { show: true, stroke: "#222", width: 1 },
          stroke: "#888",
          font: "10px 'Consolas'",
          gap: 5,
          // Safety Check for Axis Ticks
          values: (_u, vals) => vals.map(v => {
              const d = new Date(v);
              // Fallback to number formatting if date is invalid or looks like relative seconds
              if (isNaN(d.getTime()) || v < 100000000000) return v.toFixed(1);
              return d.toLocaleTimeString('en-US', { hour12: false, hour: "2-digit", minute:"2-digit", second:"2-digit" });
          }),
        },
        {
          label: titulo.toUpperCase(),
          labelSize: 20,
          labelFont: "10px 'Consolas'",
          grid: { show: true, stroke: "#222", width: 1 },
          stroke: "#888",
          font: "10px 'Consolas'",
          gap: 5,
        }
      ],
      cursor: {
          drag: { x: true, y: true },
          points: { show: false },
      },
      legend: {
          show: true,
      }
    };

    uplotRef.current = new uPlot(opts, data as uPlot.AlignedData, chartRef.current);

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (uplotRef.current) {
          const { width, height } = entry.contentRect;
          uplotRef.current.setSize({ width, height });
        }
      }
    });

    observer.observe(chartRef.current);

    return () => {
      observer.disconnect();
      uplotRef.current?.destroy();
      uplotRef.current = null;
    };
  }, []);

  useEffect(() => {
    uplotRef.current?.setData(data as uPlot.AlignedData);
  }, [timestamps, series]);

  return (
    <div className="grafico_multivariavel">
      <div ref={chartRef} style={{ width: "100%", height: "100%", minHeight: "0" }} />
    </div>
  );
}
