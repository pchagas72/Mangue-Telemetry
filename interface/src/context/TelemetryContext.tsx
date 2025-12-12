import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import type { TelemetriaData } from "../types/TelemetriaData";

// Define the shape of your context
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

        timestamps: number[];
        path: [number, number][];
    };
    connectedIp: string | null;
    startFinishLine?: { lat: number; lon: number } | null; // NEW FIELD
}

const TelemetryContext = createContext<TelemetryContextType | null>(null);

export function useTelemetryData() {
    const context = useContext(TelemetryContext);
    // Return a safe default if used outside the provider
    if (!context) {
        return {
            latestData: null,
            history: { timestamps: [], speeds: [], rpms: [] },
            connectedIp: null,
            startFinishLine: null
        };
    }
    return context;
}

export const TelemetryProvider = ({ children, value }: { children: ReactNode, value: TelemetryContextType }) => (
    <TelemetryContext.Provider value={value}>
        {children}
    </TelemetryContext.Provider>
);
