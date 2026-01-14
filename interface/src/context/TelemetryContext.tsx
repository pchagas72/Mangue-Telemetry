import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import type { TelemetriaData } from "../types/TelemetriaData";

// The context must hold all displayed data
interface TelemetryContextType {
    latestData: TelemetriaData | null;
    history: {
        speeds: number[];
        rpms: number[];
        temperatures_motor: number[];
        temperatures_cvt: number[];
        soc: number[];
        volt: number[];
        current: number[];

        acc_x: number[];
        acc_y: number[];
        acc_z: number[];

        dps_x: number[];
        dps_y: number[];
        dps_z: number[];

        roll: number[];
        pitch: number[];
        latitude: number[];
        longitude: number[];
        
        total_distance: number[];
        lap_distance: number[];

        timestamps: number[];
        path: [number, number][];
    };
    connectedIp: string | null;
    startFinishLine?: { lat: number; lon: number } | null;
}

const TelemetryContext = createContext<TelemetryContextType | null>(null);

export function useTelemetryData() {
    const context = useContext(TelemetryContext);
        // This is a safe return in case of no provider (server)
    if (!context) {
        return {
            latestData: null,
            history: { 
                timestamps: [], speeds: [], rpms: [], 
                temperatures_motor: [], temperatures_cvt: [], soc: [], volt: [], current: [],
                acc_x: [], acc_y: [], acc_z: [], dps_x: [], dps_y: [], dps_z: [],
                roll: [], pitch: [], latitude: [], longitude: [],
                total_distance: [], lap_distance: [], path: []
            },
            connectedIp: null,
            startFinishLine: null
        };
    }
    return context;
}

// Think of this as a context wrapper
export const TelemetryProvider = ({ children, value }: { children: ReactNode, value: TelemetryContextType }) => (
    <TelemetryContext.Provider value={value}>
        {children}
    </TelemetryContext.Provider>
);
