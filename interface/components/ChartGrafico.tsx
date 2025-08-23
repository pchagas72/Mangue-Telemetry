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
    if (!chartRef.current || uplotRef.current) return;

    const opts: uPlot.Options = {
      title: titulo,
      width: chartRef.current.clientWidth,
      height: 200,
      series: [
        {}, // eixo X
        ...series.map((s) => ({
          label: s.label,
          stroke: s.cor || "#00ADB5",
        })),
      ],
      axes: [{}, { stroke: "#cdd6f4" }],
    };

    uplotRef.current = new uPlot(opts, data as uPlot.AlignedData, chartRef.current);

    const resize = () => {
      uplotRef.current?.setSize({
        width: chartRef.current!.clientWidth,
        height: 200,
      });
    };

    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      uplotRef.current?.destroy();
      uplotRef.current = null;
    };
  }, []); // 🔒 só cria uma vez

  useEffect(() => {
    uplotRef.current?.setData(data as uPlot.AlignedData);
  }, [timestamps, series.map((s) => s.valores)]);

  return (
    <div className="grafico_multivariavel">
      <div ref={chartRef} style={{ height: "200px", overflow: "hidden" }} />
      <div className="chart_legend">
        {series.map((s, index) => (
          <div key={index} className="chart_legend_item">
            <span
              className="chart_legend_color"
              style={{ backgroundColor: s.cor || "#00ADB5" }}
            />
            <span>{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

