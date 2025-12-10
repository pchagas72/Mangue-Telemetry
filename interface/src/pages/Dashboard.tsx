import "./style.css";
import { ChartGrafico } from "../components/ChartGrafico";
import { Mapa } from "../components/Mapa";
import { Bateria } from "../components/Bateria";
import { Serial } from "../components/Serial";
import { useTelemetry } from "../hooks/useTelemetry";
import { useEffect, useState } from "react";
import { CarModel } from "../components/CarModel";
import { LapTimer } from "../components/LapTimer";
import { Status } from "../components/Status";
import type { TelemetriaData } from "../types/TelemetriaData";

const formatNumber = (value: number | undefined | null, digits = 2): string => {
    if (typeof value !== 'number' || isNaN(value)) {
        return 'N/A';
    }
    return value.toFixed(digits);
};

export default function Dashboard() {

    const [ipInput, setIpInput] = useState("localhost"); 
    const [connectedIp, setConnectedIp] = useState<string | null>(null);

    const data = useTelemetry(connectedIp); 

    const [layout, setLayout] = useState<"pista" | "dados" | "graficos">("pista");
    const [theme, setTheme] = useState<'dark' | 'light'>('dark');
    const [timestamps, setTimestamps] = useState<number[]>([]);
    const [velocidades, setVelocidades] = useState<number[]>([]);
    const [rpms, setRpms] = useState<number[]>([]);
    const [temps_motor, setTemps_motor] = useState<number[]>([]);
    const [temps_cvt, setTemps_cvt] = useState<number[]>([]);
    const [acc_xs, setAcc_xs] = useState<number[]>([]);
    const [acc_ys, setAcc_ys] = useState<number[]>([]);
    const [acc_zs, setAcc_zs] = useState<number[]>([]);
    const [caminho, setCaminho] = useState<[number, number][]>([]);

    useEffect(() => {
        if (data) {
            const timestamp = data.timestamp;
            if (typeof data.speed === "number") {
                setVelocidades((prev) => [...prev.slice(-99), data.speed]);
                setTimestamps((prev) => [...prev.slice(-99), timestamp]);
            }
            if (typeof data.rpm === "number") {
                setRpms((prev) => [...prev.slice(-99), data.rpm]);
            }
            if (typeof data.temperature === "number") {
                setTemps_motor((prev) => [...prev.slice(-99), data.temperature]);
            }
            if (typeof data.temp_cvt === "number") {
                setTemps_cvt((prev) => [...prev.slice(-99), data.temp_cvt]);
            }
            if (typeof data.acc_x === "number") {
                setAcc_xs((prev) => [...prev.slice(-99), data.acc_x]);
            }
            if (typeof data.acc_y === "number") {
                setAcc_ys((prev) => [...prev.slice(-99), data.acc_y]);
            }
            if (typeof data.acc_z === "number") {
                setAcc_zs((prev) => [...prev.slice(-99), data.acc_z]);
            }
            
            if (typeof data.latitude === 'number' && typeof data.longitude === 'number' && !isNaN(data.latitude) && !isNaN(data.longitude)) {
                const pos: [number, number] = [data.latitude, data.longitude];
                setCaminho((prev) => [...prev, pos]);
            }
        }
    }, [data]);

    useEffect(() => {
        document.body.classList.toggle('light-mode', theme === 'light');
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
    };
    
    const handleConnection = () => {
        if (connectedIp) {
            setConnectedIp(null);
        } else {
            setConnectedIp(ipInput);
        }
    };

    const connectionStatus = data !== null && connectedIp;

    const displayData: TelemetriaData = data || {
        speed: 0, rpm: 0, temperature: 0, temp_cvt: 0, soc: 0, volt: 0, current: 0,
        acc_x: 0, acc_y: 0, acc_z: 0, dps_x: 0, dps_y: 0, dps_z: 0,
        roll: 0, pitch: 0, latitude: 0, longitude: 0, timestamp: 0, flags: 0,
    };

    return (
        <div className="dashboard">
            <div className="sideBar">
                <img className="mangue_logo" src="/mangue_logo_white.avif" alt="Mangue Baja Logo" />
                
                <div className="connection-controls">
                    <label htmlFor="ip-input">Server IP:</label>
                    <input 
                        id="ip-input"
                        type="text"
                        value={ipInput}
                        onChange={(e) => setIpInput(e.target.value)}
                        disabled={!!connectedIp} // Disable input when connected
                    />
                    <button onClick={handleConnection} className={connectedIp ? 'stop' : 'start'}>
                        {connectedIp ? 'Disconnect' : 'Connect'}
                    </button>
                    <p className="connection-status">
                        Status: 
                        <span style={{ color: connectionStatus ? '#4caf50' : '#e53935' }}>
                            {connectionStatus ? ' Connected' : ' Disconnected'}
                        </span>
                    </p>
                </div>

                <button onClick={() => setLayout("pista")}>Pista</button>
                <button onClick={() => setLayout("dados")}>Dados</button>
                <button onClick={() => setLayout("graficos")}>Gráficos</button>
                <button onClick={toggleTheme}>
                    {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
                </button>
            </div>
            <main className="main_window">
                {layout === "pista" && (
                    <div className="dashboard-grid dashboard-pista">
                        <div className="map-panel">
                            <Mapa latitude={displayData.latitude} longitude={displayData.longitude} caminho={caminho} />
                        </div>
                        <div className="data-panel-large">
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
                        </div>
                        <div className="carmodel-panel">
                           <CarModel roll={displayData.roll} pitch={displayData.pitch} />
                        </div>
                        <div className="status-panel">
                            <Status data={displayData} />
                            <LapTimer />
                            <Bateria soc={displayData.soc} tensao={displayData.volt} corrente={displayData.current} />
                        </div>
                    </div>
                )}
                {layout === "dados" && (
                    <div className="dashboard-grid dashboard-dados">
                        <div className="data-panel-large">
                            <div className="databox"><h3>Velocidade</h3><p>{formatNumber(displayData.speed, 1)} km/h</p></div>
                            <div className="databox"><h3>RPM</h3><p>{formatNumber(displayData.rpm, 0)}</p></div>
                            <div className="databox"><h3>Temp. Motor</h3><p>{formatNumber(displayData.temperature, 1)} ºC</p></div>
                            <div className="databox"><h3>Temp. CVT</h3><p>{formatNumber(displayData.temp_cvt, 1)} ºC</p></div>
                            <div className="databox"><h3>SOC</h3><p>{formatNumber(displayData.soc, 0)}%</p></div>
                            <div className="databox"><h3>Tensão</h3><p>{formatNumber(displayData.volt, 2)} V</p></div>
                            <div className="databox"><h3>Corrente</h3><p>{formatNumber(displayData.current, 0)} mA</p></div>
                            <div className="databox"><h3>Acc X</h3><p>{formatNumber(displayData.acc_x, 2)} g</p></div>
                            <div className="databox"><h3>Acc Y</h3><p>{formatNumber(displayData.acc_y, 2)} g</p></div>
                            <div className="databox"><h3>Acc Z</h3><p>{formatNumber(displayData.acc_z, 2)} g</p></div>
                            <div className="databox"><h3>DPS X</h3><p>{formatNumber(displayData.dps_x, 2)} dps</p></div>
                            <div className="databox"><h3>DPS Y</h3><p>{formatNumber(displayData.dps_y, 2)} dps</p></div>
                            <div className="databox"><h3>DPS Z</h3><p>{formatNumber(displayData.dps_z, 2)} dps</p></div>
                            <div className="databox"><h3>Roll</h3><p>{formatNumber(displayData.roll, 2)}°</p></div>
                            <div className="databox"><h3>Pitch</h3><p>{formatNumber(displayData.pitch, 2)}°</p></div>
                        </div>
                        <div className="serial-panel">
                            <Serial data={displayData} />
                        </div>
                    </div>
                )}
                {layout === "graficos" && (
                    <div className="graficos_dashboard">
                        <div className="left_panel">
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
                            <div className="acceleration_charts">
                            <ChartGrafico
                                titulo="Temperatura do motor"
                                timestamps={timestamps}
                                series={[
                                    { label: "Temp. Motor", valores: temps_motor, cor: "#f38ba8" },
                                ]}
                            />
                            <ChartGrafico
                                titulo="Temperatura da CVT"
                                timestamps={timestamps}
                                series={[
                                    { label: "Temp. CVT", valores: temps_cvt, cor: "#fab387" },
                                ]}
                            />
                            </div>
                            <div className="acceleration_charts">
                                <ChartGrafico
                                    titulo="Aceleração X"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "Aceleração X", valores: acc_xs, cor: "#a28ba8" },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Aceleração Y"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "Aceleração Y", valores: acc_ys, cor: "#a28ba8" },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Aceleração Z"
                                    timestamps={timestamps}
                                    series={[
                                        { label: "Aceleração Z", valores: acc_zs, cor: "#a28ba8" },
                                    ]}
                                />
                            </div>
                        </div>
                        <div className="right_panel">
                            <CarModel roll={displayData.roll} pitch={displayData.pitch} />
                            <Bateria soc={displayData.soc} tensao={displayData.volt} corrente={displayData.current} />
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
