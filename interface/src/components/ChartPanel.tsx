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
    // 1. Get viewMode from context
    const { history, viewMode } = useTelemetryData();
    
    const title = props.params.title as string || "Chart";
    const lines = props.params.lines as Array<{ dataKey: string, label: string, color: string }>;
    
    const dataKey = props.params.dataKey as string;
    const color = props.params.color as string || MOTEC_COLORS.cyan;
    
    // Custom X-Axis Key (overrides global viewMode if set, e.g. for scatter plots)
    const customXAxisKey = props.params.xAxisKey as string;
    
    // 2. Select X-Axis Data
    let xData: number[] = [];
    let xAxisLabel = "TIME";

    if (customXAxisKey) {
        // Scatter plot logic (e.g. RPM vs Torque)
        xData = (history as any)[customXAxisKey] || [];
        xAxisLabel = props.params.xAxisLabel || customXAxisKey.toUpperCase();
    } else {
        // Standard Rolling Chart Logic
        if (viewMode === "dist") {
            // We use Total Distance for the X-axis because it is monotonic (always increases).
            xData = history.total_distance; 
            xAxisLabel = "DIST (m)";
        } else {
            xData = history.timestamps;
            xAxisLabel = "TIME";
        }
    }

    let seriesData: { label: string, valores: number[], cor: string }[] = [];
    let isScatter = !!customXAxisKey;

    let yDefinitions = lines;
    if (!yDefinitions && dataKey) {
        yDefinitions = [{ dataKey, label: title, color }];
    }
    if (!yDefinitions) yDefinitions = [];

    // Data Alignment Logic
    // If it's a Scatter plot (Custom X), we need to zip and sort to ensure X is ascending
    if (isScatter) {
        const combined = xData.map((xVal, i) => {
            const yVals = yDefinitions.map(def => ((history as any)[def.dataKey] || [])[i] || 0);
            return { x: xVal, ys: yVals };
        });
        
        // uPlot requires X to be sorted
        combined.sort((a, b) => a.x - b.x);

        xData = combined.map(c => c.x);
        seriesData = yDefinitions.map((def, idx) => ({
            label: def.label,
            cor: def.color,
            valores: combined.map(c => c.ys[idx])
        }));
    } else {
        // Standard Time/Dist mode (Data is already sorted by nature of arrival)
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
            xAxisLabel={xAxisLabel}
            isScatter={isScatter}
        />
    );
};
