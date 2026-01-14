// src/components/ChartGrafico.tsx
import { useEffect, useRef, useMemo } from "react";
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
  xAxisLabel?: string;
  isScatter?: boolean;
}

export function ChartGrafico({ 
    titulo, 
    timestamps, 
    series, 
    xAxisLabel = "TIME", 
    isScatter = false 
}: ChartMultivariavelProps) {
  
  const chartRef = useRef<HTMLDivElement>(null);
  const uplotRef = useRef<uPlot | null>(null);

  const data = useMemo(() => {
    return [
      timestamps,
      ...series.map((s) => s.valores),
    ] as uPlot.AlignedData;
  }, [timestamps, series]);

  useEffect(() => {
    if (!chartRef.current) return;

    if (uplotRef.current) {
      uplotRef.current.destroy();
    }

    const initWidth = chartRef.current.clientWidth;
    const initHeight = chartRef.current.clientHeight;

    const opts: uPlot.Options = {
      title: "",
      width: initWidth,
      height: initHeight,
      series: [
        {
          label: xAxisLabel,
          value: (_u, v) => {
              if (v == null) return "--";
              
              if (isScatter) return v.toFixed(2);

              // Heuristic: If label says "TIME", treat as date. 
              // Otherwise treat as Distance (or other unit).
              if (xAxisLabel.includes("TIME")) {
                 const d = new Date(v);
                 return d.toLocaleTimeString('en-US', { hour12: false });
              }
              
              // Distance formatting
              return v.toFixed(0) + "m";
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
          label: xAxisLabel,
          labelSize: 20,
          labelFont: "12px 'Consolas', monospace",
          font: "10px 'Consolas', monospace",
          grid: { show: true, stroke: "#333", width: 1 },
          stroke: "#888",
          gap: 5,
          values: (_u, vals) => vals.map(v => {
              if (isScatter) return v >= 1000 ? (v/1000).toFixed(1) + "k" : v.toFixed(0);
              
              if (xAxisLabel.includes("TIME")) {
                  return new Date(v).toLocaleTimeString('en-US', { hour12: false, hour: "2-digit", minute:"2-digit", second:"2-digit" });
              }
              
              // Distance formatting for Axis
              return v.toFixed(0);
          }),
        },
        {
          // Y-Axis
          label: titulo.toUpperCase(),
          labelSize: 20,
          labelFont: "12px 'Consolas', monospace",
          font: "10px 'Consolas', monospace",
          grid: { show: true, stroke: "#333", width: 1 },
          stroke: "#888",
          gap: 5,
        }
      ],
      cursor: {
          drag: { x: true, y: true },
          points: { show: false },
      },
      legend: {
          show: true,
      },
    };

    const u = new uPlot(opts, data, chartRef.current);
    uplotRef.current = u;
    
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
      u.destroy();
      uplotRef.current = null;
    };
    
  }, [xAxisLabel, isScatter, titulo, series.length]); 

  useEffect(() => {
    if (uplotRef.current) {
        uplotRef.current.setData(data);
    }
  }, [data]);

  return (
    <div className="grafico_multivariavel" style={{ width: "100%", height: "100%" }}>
      <div ref={chartRef} style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
