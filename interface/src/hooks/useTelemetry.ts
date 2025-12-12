// src/hooks/useTelemetry.ts
import { useEffect, useState } from "react";
import type { TelemetriaData } from "../types/TelemetriaData";

export function useTelemetry(serverIp: string | null) {
    const [data, setData] = useState<TelemetriaData | null>(null);

    useEffect(() => {
        // If the IP is null (e.g., "Disconnected"), clear data and do nothing
        if (!serverIp) {
            setData(null); 
            return;
        }

        const ws = new WebSocket(`ws://${serverIp}:8000/ws/telemetry`);

            ws.onopen = () => {
            console.log("WebSocket connected to", serverIp);
        };

        ws.onmessage = (event) => {
            try {
                const parsed = JSON.parse(event.data);
                setData(parsed);
            } catch (e) {
                console.error("Failed to parse WebSocket message:", e);
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            setData(null); // Clear data on error
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected");
            setData(null); // Clear data on close
        };

        // Cleanup function: This runs when the component unmounts
        // or when serverIp changes
        return () => {
            ws.close();
        };

    }, [serverIp]); // Rerun this effect whenever serverIp changes

    return data;
}
