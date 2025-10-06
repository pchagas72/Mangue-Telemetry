import type { TelemetriaData } from "../types/TelemetriaData.ts";

export function Status({ data }: { data: TelemetriaData }) {
    const getStatus = (value: number, thresholds: { ok: number, warn: number, crit: number }) => {
        if (value < thresholds.ok) return 'OK';
        if (value < thresholds.warn) return 'Warning';
        return 'Critical';
    };

    const rpmStatus = getStatus(data.rpm, { ok: 4000, warn: 5000, crit: 5500 });
    const tempMotorStatus = getStatus(data.temperature, { ok: 100, warn: 120, crit: 140 });
    const tempCvtStatus = getStatus(data.temp_cvt, { ok: 80, warn: 100, crit: 120 });
    const socStatus = getStatus(100 - data.soc, { ok: 80, warn: 90, crit: 95 }); // Inverted logic for SOC

    const statusColors = {
        'OK': '#4caf50',
        'Warning': '#fdd835',
        'Critical': '#e53935'
    };

    return (
        <div className="bateria_container">
            <h3>System Status</h3>
            <div style={{ marginTop: '1rem' }}>
                <p>RPM: <span style={{ color: statusColors[rpmStatus] }}>{rpmStatus}</span></p>
                <p>Motor Temp: <span style={{ color: statusColors[tempMotorStatus] }}>{tempMotorStatus}</span></p>
                <p>CVT Temp: <span style={{ color: statusColors[tempCvtStatus] }}>{tempCvtStatus}</span></p>
                <p>Battery: <span style={{ color: statusColors[socStatus] }}>{socStatus}</span></p>
            </div>
        </div>
    );
}
