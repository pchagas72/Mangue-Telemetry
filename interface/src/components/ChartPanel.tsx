// src/components/ChartPanel.tsx
import type { IDockviewPanelProps } from "dockview";
import { useTelemetryData } from "../context/TelemetryContext";
import { ChartGrafico } from "./ChartGrafico";

const MOTEC_COLORS = {
    cyan: "#00FFFF",
    red: "#FF0000",
    green: "#00FF00",
    yellow: "#FFFF00",
    magenta: "#FF00FF",
    white: "#FFFFFF",
    orange: "#FF8800"
};

export const ChartPanel = (props: IDockviewPanelProps) => {
    const { history } = useTelemetryData();
    
    const title = props.params.title as string || "Chart";
    const lines = props.params.lines as Array<{ dataKey: string, label: string, color: string }>;
    
    // Legacy support
    const dataKey = props.params.dataKey as string;
    const color = props.params.color as string || MOTEC_COLORS.cyan;
    
    // New Param: Custom X-Axis Key
    const xAxisKey = props.params.xAxisKey as string; // e.g., 'rpms' or 'speeds'
    const xAxisLabel = props.params.xAxisLabel as string; // e.g., 'RPM'

    let xData: number[] = history.timestamps;
    let seriesData: { label: string, valores: number[], cor: string }[] = [];
    let isScatter = false;

    // 1. Determine Y-Axis Data
    let yDefinitions = lines;
    if (!yDefinitions && dataKey) {
        yDefinitions = [{ dataKey, label: title, color }];
    }
    if (!yDefinitions) yDefinitions = [];

    // 2. Handle Custom X-Axis (XY Plot Logic)
    if (xAxisKey && xAxisKey !== 'timestamps' && (history as any)[xAxisKey]) {
        isScatter = true; // Custom X usually implies scatter/correlation
        
        const rawX = (history as any)[xAxisKey] as number[];
        
        // We must sort by X for uPlot to render correctly
        // Create a zipped array: [ [x1, y1a, y1b...], [x2, y2a, y2b...] ]
        const combined = rawX.map((xVal, i) => {
            const yVals = yDefinitions.map(def => ((history as any)[def.dataKey] || [])[i] || 0);
            return { x: xVal, ys: yVals };
        });

        // Sort by X (ascending)
        combined.sort((a, b) => a.x - b.x);

        // Unzip
        xData = combined.map(c => c.x);
        seriesData = yDefinitions.map((def, idx) => ({
            label: def.label,
            cor: def.color,
            valores: combined.map(c => c.ys[idx])
        }));

    } else {
        // Standard Time-Series Logic
        xData = history.timestamps;
        seriesData = yDefinitions.map(def => ({
            label: def.label,
            cor: def.color,
            valores: (history as any)[def.dataKey] || []
        }));
    }

    return (
        <ChartGrafico 
            titulo={title}
            timestamps={xData}
            series={seriesData}
            xAxisLabel={xAxisLabel || "Time"}
            isScatter={isScatter}
        />
    );
};
