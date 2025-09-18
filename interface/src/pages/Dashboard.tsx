import "./style.css";
import { ChartGrafico } from "../components/ChartGrafico";
import { Mapa } from "../components/Mapa";
import { Bateria } from "../components/Bateria";
import { Serial } from "../components/Serial";
import { useTelemetry } from "../hooks/useTelemetry";
import { useEffect, useState } from "react";
import { CarModel } from "../components/CarModel";
import type { TelemetriaData } from "../types/TelemetriaData";

// Helper to safely format numbers, providing a fallback for null/undefined data
const formatNumber = (value: number | undefined | null, digits = 2): string => {
    if (typeof value !== 'number' || isNaN(value)) {
        return 'N/A';
    }
    return value.toFixed(digits);
};


export default function Dashboard() {
    const data = useTelemetry();
    const [layout, setLayout] = useState<"pista" | "dados" | "graficos">("pista");

    // State for chart data
    const [timestamps, setTimestamps] = useState<number[]>([]);
    const [velocidades, setVelocidades] = useState<number[]>([]);
    const [rpms, setRpms] = useState<number[]>([]);
    const [temps_motor, setTemps_motor] = useState<number[]>([]);
    const [temps_cvt, setTemps_cvt] = useState<number[]>([]);
    const [aceleracoesX, setAceleracoesX] = useState<number[]>([]);
    const [aceleracoesY, setAceleracoesY] = useState<number[]>([]);
    const [aceleracoesZ, setAceleracoesZ] = useState<number[]>([]);
    const [caminho, setCaminho] = useState<[number, number][]>([]);

    useEffect(() => {
        if (data) {
            const timestamp = data.timestamp; // Use timestamp from data if available
            let novoDado = false;

            // --- FIXES APPLIED HERE ---
            if (typeof data.speed === "number") {
                setVelocidades((prev) => [...prev.slice(-99), data.speed]);
                novoDado = true;
            }
            if (typeof data.rpm === "number") {
                setRpms((prev) => [...prev.slice(-99), data.rpm]);
                novoDado = true;
            }
            if (typeof data.temperature === "number") {
                setTemps_motor((prev) => [...prev.slice(-99), data.temperature]);
                novoDado = true;
            }
            if (typeof data.temp_cvt === "number") {
                setTemps_cvt((prev) => [...prev.slice(-99), data.temp_cvt]);
                novoDado = true;
            }
            if (typeof data.acc_x === "number") {
                setAceleracoesX((prev) => [...prev.slice(-99), data.acc_x]);
                novoDado = true;
            }
            if (typeof data.acc_y === "number") {
                setAceleracoesY((prev) => [...prev.slice(-99), data.acc_y]);
                novoDado = true;
            }
            if (typeof data.acc_z === "number") {
                setAceleracoesZ((prev) => [...prev.slice(-99), data.acc_z]);
                novoDado = true;
            }
            // --- END OF FIXES ---


            if (novoDado) {
                setTimestamps((prev) => [...prev.slice(-99), timestamp]);
            }
            if (typeof data.latitude === 'number' && typeof data.longitude === 'number' && !isNaN(data.latitude) && !isNaN(data.longitude)) {
                const pos: [number, number] = [data.latitude, data.longitude];
                const last = caminho.at(-1);
                const tol = 1e-5; // Tolerance for position change
                if (
                    !last ||
                    Math.abs(last[0] - pos[0]) > tol ||
                    Math.abs(last[1] - pos[1]) > tol
                ) {
                    setCaminho((prev) => [...prev, pos]);
                }
            }
        }
    }, [data]);

    // Create a default data object for initial render to avoid errors
    const displayData: TelemetriaData = data || {
        speed: 0, rpm: 0, temperature: 0, temp_cvt: 0, soc: 0, volt: 0, current: 0,
        acc_x: 0, acc_y: 0, acc_z: 0, dps_x: 0, dps_y: 0, dps_z: 0,
        roll: 0, pitch: 0, latitude: 0, longitude: 0, timestamp: 0, flags: 0,
    };


    return (
        <div className="dashboard">
            <div className="sideBar">
                <img className="mangue_logo" src="/mangue_logo_white.avif" alt="Mangue Baja Logo" />
                <button onClick={() => setLayout("pista")}>Pista</button>
                <button onClick={() => setLayout("dados")}>Dados</button>
                <button onClick={() => setLayout("graficos")}>Gráficos</button>
            </div>
            <main className="main_window">
                {layout === "pista" && (
                    <div className="dashboard-grid dashboard-mapa">
                        <div className="map-panel chart-container">
                            <Mapa latitude={displayData.latitude} longitude={displayData.longitude} caminho={caminho} />
                        </div>
                        <div className="data-panel-large">
                             {/* --- FIXES APPLIED HERE --- */}
                            <div className="databox">
                                <h3>Velocidade</h3>
                                <p>{formatNumber(displayData.speed, 1)} km/h</p>
                            </div>
                            <div className="databox">
                                <h3>RPM</h3>
                                <p>{formatNumber(displayData.rpm, 0)}</p>
                            </div>
                            <div className="databox">
                                <h3>Temp. Motor</h3>
                                <p>{formatNumber(displayData.temperature, 1)} ºC</p>
                            </div>
                            <div className="databox">
                                <h3>Temp. CVT</h3>
                                <p>{formatNumber(displayData.temp_cvt, 1)} ºC</p>
                            </div>
                            <div className="databox">
                                <h3>Roll</h3>
                                <p>{formatNumber(displayData.roll, 2)}°</p>
                            </div>
                            <div className="databox">
                                <h3>Pitch</h3>
                                <p>{formatNumber(displayData.pitch, 2)}°</p>
                            </div>
                        </div>
                        <div className="serial-panel">
                            <Serial data={displayData} />
                            <CarModel roll={displayData.roll} pitch={displayData.pitch} />
                            <Bateria soc={displayData.soc} tensao={displayData.volt} corrente={displayData.current} />
                        </div>
                    </div>
                )}
                {layout === "dados" && (
                    <div className="dashboard-grid dashboard-dados">
                        <div className="data-panel-large">
                             {/* --- FIXES APPLIED HERE --- */}
                            <div className="databox">
                                <h3>Velocidade</h3>
                                <p>{formatNumber(displayData.speed, 1)} km/h</p>
                            </div>
                            <div className="databox">
                                <h3>RPM</h3>
                                <p>{formatNumber(displayData.rpm, 0)}</p>
                            </div>
                            <div className="databox">
                                <h3>Temp. Motor</h3>
                                <p>{formatNumber(displayData.temperature, 1)} ºC</p>
                            </div>
                            <div className="databox">
                                <h3>Temp. CVT</h3>
                                <p>{formatNumber(displayData.temp_cvt, 1)} ºC</p>
                            </div>
                            <div className="databox">
                                <h3>Aceleração X</h3>
                                <p>{formatNumber(displayData.acc_x, 3)}</p>
                            </div>
                            <div className="databox">
                                <h3>Aceleração Y</h3>
                                <p>{formatNumber(displayData.acc_y, 3)}</p>
                            </div>
                            <div className="databox">
                                <h3>Aceleração Z</h3>
                                <p>{formatNumber(displayData.acc_z, 3)}</p>
                            </div>
                            <div className="databox">
                                <h3>GPS</h3>
                                <p>Lat: {formatNumber(displayData.latitude, 4)}</p>
                                <p>Lon: {formatNumber(displayData.longitude, 4)}</p>
                            </div>
                            <div className="databox">
                                <h3>Roll</h3>
                                <p>{formatNumber(displayData.roll, 2)}°</p>
                            </div>
                            <div className="databox">
                                <h3>Pitch</h3>
                                <p>{formatNumber(displayData.pitch, 2)}°</p>
                            </div>
                        </div>
                        <div className="serial-panel">
                            <Serial data={displayData} />
                            <CarModel roll={displayData.roll} pitch={displayData.pitch} />
                            <Bateria soc={displayData.soc} tensao={displayData.volt} corrente={displayData.current} />
                        </div>
                    </div>
                )}
                {layout === "graficos" && (
                    <div className="graficos_dashboard">
                        <div className="left_panel">
                             {/* --- FIXES APPLIED HERE --- */}
                            <ChartGrafico
                                titulo="Velocidade"
                                timestamps={timestamps}
                                series={[
                                    { label: "Velocidade", valores: velocidades, cor: "#a6e3a1" },
                                ]}
                            />
                            <ChartGrafico
                                titulo="RPM"
                                timestamps={timestamps}
                                series={[
                                    { label: "RPM", valores: rpms, cor: "#f9e2af" },
                                ]}
                            />
                            <div className="graficos_temperatura">
                                <ChartGrafico
                                    titulo="Temperatura Motor (ºC)"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "Temp. Motor", valores: temps_motor, cor: "#f38ba8" },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Temperatura CVT (ºC)"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "Temp. CVT", valores: temps_cvt, cor: "#fab387" },
                                    ]}
                                />
                            </div>
                            <div className="graficos_acc">
                                <ChartGrafico
                                    titulo="Aceleração X"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "accX", valores: aceleracoesX, cor: "#74c7ec" },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Aceleração Y"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "accY", valores: aceleracoesY, cor: "#89b4fa" },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Aceleração Z"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "accZ", valores: aceleracoesZ, cor: "#b4befe" },
                                    ]}
                                />
                            </div>
                        </div>
                        <div className="right_panel">
                            <Mapa latitude={displayData.latitude} longitude={displayData.longitude} caminho={caminho} />
                            <CarModel roll={displayData.roll} pitch={displayData.pitch} />
                            <Serial data={displayData} />
                            <Bateria soc={displayData.soc} tensao={displayData.volt} corrente={displayData.current} />
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
