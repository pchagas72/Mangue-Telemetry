// src/components/ChartPanel.tsx
import type { IDockviewPanelProps } from "dockview";
import { useTelemetryData } from "../context/TelemetryContext";
import { ChartGrafico } from "./ChartGrafico";

// MoTeC Standard Colors
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
    
    // Fallback/Legacy support
    const dataKey = props.params.dataKey as string;
    // Default to Cyan if no color provided
    const color = props.params.color as string || MOTEC_COLORS.cyan;

    let seriesData: { label: string, valores: number[], cor: string }[] = [];

    if (lines && lines.length > 0) {
        seriesData = lines.map(line => ({
            label: line.label,
            valores: (history as any)[line.dataKey] || [],
            cor: line.color
        }));
    } else if (dataKey) {
        seriesData = [{ 
            label: title, 
            valores: (history as any)[dataKey] || [], 
            cor: color 
        }];
    }

    return (
        <ChartGrafico 
            titulo={title}
            timestamps={history.timestamps}
            series={seriesData}
        />
    );
};
