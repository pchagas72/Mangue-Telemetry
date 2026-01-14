// src/pages/Dashboard.tsx
import _React, { useEffect, useState } from "react";
import { DockviewReact, DockviewApi } from "dockview";
import type { IDockviewPanelProps } from "dockview";
import type { DockviewReadyEvent } from "dockview";
import "dockview/dist/styles/dockview.css";
import "./style.css";

import { useTelemetry } from "../hooks/useTelemetry";
import { ChartPanel } from "../components/ChartPanel";
import { TelemetryProvider, useTelemetryData } from "../context/TelemetryContext";
import type { TelemetriaData } from "../types/TelemetriaData";
import { Mapa } from "../components/Mapa";
import { CarModel } from "../components/CarModel";
import { LiveCarPanel } from "../components/LiveCarPanel";
import { GGDiagram } from "../components/CGDiagram";

// Definitions for available channels and colors
const AVAILABLE_CHANNELS = [
    { key: 'speeds', label: 'Speed', unit: 'km/h' },
    { key: 'rpms', label: 'RPM', unit: 'rpm' },
    { key: 'soc', label: 'SoC', unit: '%' },
    { key: 'volt', label: 'Battery', unit: 'V' },
    { key: 'current', label: 'Current', unit: 'A' },
    { key: 'temperatures_motor', label: 'Motor Temp', unit: '°C' },
    { key: 'temperatures_cvt', label: 'CVT Temp', unit: '°C' },
    { key: 'acc_x', label: 'G-Long', unit: 'g' },
    { key: 'acc_y', label: 'G-Lat', unit: 'g' },
    { key: 'acc_z', label: 'G-Vert', unit: 'g' },
    { key: 'roll', label: 'Roll', unit: 'deg' },
    { key: 'pitch', label: 'Pitch', unit: 'deg' },
    { key: 'dps_z', label: 'Yaw Rate', unit: 'deg/s' },
];

const GRAPH_COLORS = ['#00FFFF', '#FF00FF', '#FFFF00', '#00FF00', '#FF3333', '#FFA500'];

// Helper functions
const formatLapTime = (ms: number) => {
    if (!ms) return "0:00.00";
    const min = Math.floor(ms / 60000);
    const sec = Math.floor((ms % 60000) / 1000);
    const mil = Math.floor((ms % 1000) / 10);
    return `${min}:${sec.toString().padStart(2, '0')}.${mil.toString().padStart(2, '0')}`;
};

// --- Components ---

// General graph component
const AddGraphModal = ({
    isOpen,
    onClose,
    onAdd
}: {
    isOpen: boolean;
    onClose: () => void;
    onAdd: (selectedKeys: string[]) => void;
}) => {
    const [selected, setSelected] = useState<string[]>([]);

    if (!isOpen) return null;

    const toggleSelection = (key: string) => {
        setSelected(prev =>
            prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
        );
    };

    return (
        <div className="modal-overlay" style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 9999,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
            <div className="modal-content" style={{
                backgroundColor: '#1a1a1a', border: '1px solid #444', padding: '20px',
                width: '400px', maxWidth: '90%'
            }}>
                <h3 style={{ color: '#fff', marginBottom: '15px' }}>ADD MULTI-CHANNEL GRAPH</h3>
                <div className="channel-grid" style={{
                    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px',
                    maxHeight: '300px', overflowY: 'auto'
                }}>
                    {AVAILABLE_CHANNELS.map(ch => (
                        <label key={ch.key} style={{ display: 'flex', alignItems: 'center', color: '#ccc', fontSize: '12px', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={selected.includes(ch.key)}
                                onChange={() => toggleSelection(ch.key)}
                                style={{ marginRight: '8px' }}
                            />
                            {ch.label}
                        </label>
                    ))}
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                    <button className="btn-tech" onClick={onClose}>CANCEL</button>
                    <button
                        className="btn-tech"
                        style={{ borderColor: 'var(--accent-green)', color: 'var(--accent-green)' }}
                        onClick={() => { onAdd(selected); setSelected([]); onClose(); }}
                    >
                        CREATE GRAPH
                    </button>
                </div>
            </div>
        </div>
    );
};

// Logic is processed on the backend
const MapPanel = () => {
    const { latestData, history, startFinishLine } = useTelemetryData();
    if (!latestData) return <div className="waiting-text">Waiting for connection...</div>;
    return (
        <div style={{ height: '100%', padding: '10px' }}>
            {Mapa(latestData.latitude, latestData.longitude, history.path, startFinishLine, 10)}
        </div>
    )
}

const CarTilt = () => {
    const { latestData } = useTelemetryData();
    if (!latestData) return <div className="waiting-text">Waiting for connection...</div>;
    return (
        <div style={{ height: '100%', padding: '10px' }}>
            {CarModel(latestData.roll, latestData.pitch)}
        </div>
    )
}

// Registering Components for dockview
const components = {
    map_panel: (_props: IDockviewPanelProps) => <MapPanel />,
    car_panel: (_props: IDockviewPanelProps) => <LiveCarPanel />,
    chart_panel: (props: IDockviewPanelProps) => <ChartPanel {...props} />,
    carTilt_panel: (_props: IDockviewPanelProps) => <CarTilt />,
    gg_panel: (_props: IDockviewPanelProps) => <GGDiagram />,
};

// Layout setup
function loadDefaultLayout(api: DockviewApi) {
    api.clear();

    // Lat/Lon/path
    api.addPanel({
        id: 'map_panel',
        component: 'map_panel',
        title: 'GPS Map',
    });

    // Gyroscope
    api.addPanel({
        id: 'carTilt_panel',
        component: 'carTilt_panel',
        title: 'Car Tilt Panel',
        position: { referencePanel: 'map_panel', direction: 'below' }
    });

    // Speed
    api.addPanel({
        id: 'speed_graph',
        component: 'chart_panel',
        title: 'Speed Graph',
        position: { direction: 'right' },
        params: { title: 'Velocity', dataKey: 'speeds', color: '#00FFFF' }
    });

    // RPM
    api.addPanel({
        id: 'rpm_graph',
        component: 'chart_panel',
        title: 'RPM Graph',
        position: { referencePanel: 'speed_graph', direction: 'within' },
        params: { title: 'RPM', dataKey: 'rpms', color: '#50DAB5' }
    });

    api.addPanel({
        id: 'temp_combined_graph',
        component: 'chart_panel',
        title: 'Temperature Monitor',
        position: { referencePanel: 'speed_graph', direction: 'within' },
        params: {
            title: 'System Temperatures',
            lines: [
                { dataKey: 'temperatures_motor', label: 'Motor', color: '#FF3333' },
                { dataKey: 'temperatures_cvt', label: 'CVT', color: '#FFA500' }
            ]
        }
    });

    // Speed, RPM, Voltage, Current, Eng Temp, CVT temp, SoC
    api.addPanel({
        id: 'car_panel',
        component: 'car_panel',
        title: 'Live Data',
        position: { direction: 'right' }
    });

    // ACCX, ACCY, ACCZ
    api.addPanel({
        id: 'gg_panel',
        component: 'gg_panel',
        title: 'G-G Diagram',
        position: { referencePanel: 'car_panel', direction: 'below' }
    });
}

const Dashboard = () => {
    // Interface variables
    const [api, setApi] = useState<DockviewApi>();
    const [serverIp, setServerIp] = useState<string>("");
    const [inputIp, setInputIp] = useState("localhost");
    
    // View States
    const [viewMode, setViewMode] = useState<"time" | "dist">("time");
    const [distMode, setDistMode] = useState<"total" | "lap">("total");
    
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Data received from the backend
    const incomingData = useTelemetry(serverIp || null);

    // Data context
    const [contextState, setContextState] = useState({
        latestData: null as TelemetriaData | null,
        viewMode: "time" as "time" | "dist",
        history: {
            timestamps: [] as number[],
            speeds: [] as number[],
            rpms: [] as number[],
            temperatures_motor: [] as number[],
            temperatures_cvt: [] as number[],
            soc: [] as number[],
            volt: [] as number[],
            current: [] as number[],
            acc_x: [] as number[],
            acc_y: [] as number[],
            acc_z: [] as number[],
            dps_x: [] as number[],
            dps_y: [] as number[],
            dps_z: [] as number[],
            roll: [] as number[],
            pitch: [] as number[],
            latitude: [] as number[],
            longitude: [] as number[],
            total_distance: [] as number[],
            lap_distance: [] as number[],
            path: [] as [number, number][],
        },
        connectedIp: null as string | null,
    });

    // Sync viewMode state with context
    useEffect(() => {
        setContextState(prev => ({ ...prev, viewMode }));
    }, [viewMode]);

    // The server keeps track of the last 500 data points in case of a refresh
    // or new client connection
    useEffect(() => {
        if (!serverIp) return;

        const fetchHistory = async () => {
            try {
                const res = await fetch(`http://${serverIp}:8000/api/session/history`);
                const historyData = await res.json();
                
                if (Array.isArray(historyData) && historyData.length > 0) {
                    setContextState(prev => {
                        // Helper to merge arrays
                        const merge = (_oldArr: number[], key: string) => {
                             // Map the history objects to values, defaulting to 0
                             const newValues = historyData.map((d: any) => d[key] ?? 0);
                             // Return the last 300 points combined
                             return [...newValues].slice(-300);
                        };
                        
                        // Reconstruct path from history
                        const newPath = historyData
                             .filter((d: any) => d.latitude && d.longitude)
                             .map((d: any) => [d.latitude, d.longitude] as [number, number])
                             .slice(-500); // MAX_PATH_POINTS

                        // Return the fully populated state
                        return {
                            ...prev,
                            history: {
                                timestamps: merge(prev.history.timestamps, 'timestamp'),
                                speeds: merge(prev.history.speeds, 'speed'),
                                rpms: merge(prev.history.rpms, 'rpm'),
                                temperatures_motor: merge(prev.history.temperatures_motor, 'temperature'),
                                temperatures_cvt: merge(prev.history.temperatures_cvt, 'temp_cvt'),
                                soc: merge(prev.history.soc, 'soc'),
                                volt: merge(prev.history.volt, 'volt'),
                                current: merge(prev.history.current, 'current'),
                                acc_x: merge(prev.history.acc_x, 'acc_x'),
                                acc_y: merge(prev.history.acc_y, 'acc_y'),
                                acc_z: merge(prev.history.acc_z, 'acc_z'),
                                dps_x: merge(prev.history.dps_x, 'dps_x'),
                                dps_y: merge(prev.history.dps_y, 'dps_y'),
                                dps_z: merge(prev.history.dps_z, 'dps_z'),
                                roll: merge(prev.history.roll, 'roll'),
                                pitch: merge(prev.history.pitch, 'pitch'),
                                latitude: merge(prev.history.latitude, 'latitude'),
                                longitude: merge(prev.history.longitude, 'longitude'),
                                total_distance: merge(prev.history.total_distance, 'total_distance'),
                                lap_distance: merge(prev.history.lap_distance, 'lap_distance'),
                                path: newPath
                            },
                            // Use the last packet to set the "Current" numbers
                            latestData: historyData[historyData.length - 1]
                        };
                    });
                    console.log(`[Dashboard] Restored ${historyData.length} history points.`);
                }
            } catch (e) {
                console.error("Failed to fetch history:", e);
            }
        };

        fetchHistory();
    }, [serverIp]); // Runs once when serverIp is set (new connection)

    // SF calculations are done on the backend server
    const handleSetSF = async () => {
        if (!serverIp) return;
        try {
            await fetch(`http://${serverIp}:8000/api/set-sf`, { method: "POST" });
            console.log("Sent request to set Start/Finish line");
        } catch (err) {
            console.error("Failed to set Start/Finish line:", err);
        }
    };

    const activeSF = contextState.latestData?.sf_lat && contextState.latestData?.sf_lon
        ? { lat: contextState.latestData.sf_lat, lon: contextState.latestData.sf_lon }
        : null;

    // Updates interface to show incoming data
    useEffect(() => {
        if (incomingData) {
            setContextState(prev => {
                const MAX_POINTS = 300;
                const MAX_PATH_POINTS = 500;

                const updateArr = (arr: number[], val: number) => {
                    const newArr = [...arr, val];
                    if (newArr.length > MAX_POINTS) newArr.shift();
                    return newArr;
                };

                const updatePath = (currentPath: [number, number][], lat: number, lon: number) => {
                    const newPoint: [number, number] = [lat, lon];
                    const newPath = [...currentPath, newPoint];
                    if (newPath.length > MAX_PATH_POINTS) newPath.shift();
                    return newPath;
                };

                let safeTimestamp = Date.now();
                if (typeof incomingData.timestamp === 'number') {
                    safeTimestamp = incomingData.timestamp;
                }

                return {
                    latestData: incomingData,
                    viewMode: viewMode, // Ensure state persists
                    connectedIp: serverIp,
                    history: {
                        timestamps: updateArr(prev.history.timestamps, safeTimestamp),
                        speeds: updateArr(prev.history.speeds, incomingData.speed),
                        rpms: updateArr(prev.history.rpms, incomingData.rpm),
                        temperatures_motor: updateArr(prev.history.temperatures_motor, incomingData.temperature),
                        temperatures_cvt: updateArr(prev.history.temperatures_cvt, incomingData.temp_cvt),
                        soc: updateArr(prev.history.soc, incomingData.soc),
                        volt: updateArr(prev.history.volt, incomingData.volt),
                        current: updateArr(prev.history.current, incomingData.current),
                        acc_x: updateArr(prev.history.acc_x, incomingData.acc_x),
                        acc_y: updateArr(prev.history.acc_y, incomingData.acc_y),
                        acc_z: updateArr(prev.history.acc_z, incomingData.acc_z),
                        dps_x: updateArr(prev.history.dps_x, incomingData.dps_x),
                        dps_y: updateArr(prev.history.dps_y, incomingData.dps_y),
                        dps_z: updateArr(prev.history.dps_z, incomingData.dps_z),
                        roll: updateArr(prev.history.roll, incomingData.roll),
                        pitch: updateArr(prev.history.pitch, incomingData.pitch),
                        latitude: updateArr(prev.history.latitude, incomingData.latitude),
                        longitude: updateArr(prev.history.longitude, incomingData.longitude),
                        total_distance: updateArr(prev.history.total_distance, incomingData.total_distance || 0),
                        lap_distance: updateArr(prev.history.lap_distance, incomingData.lap_distance || 0),
                        path: updatePath(prev.history.path, incomingData.latitude, incomingData.longitude)
                    }
                };
            });
        }
    }, [incomingData, serverIp, viewMode]);

    // Draws the main interface
    const onReady = (event: DockviewReadyEvent) => {
        setApi(event.api);
        loadDefaultLayout(event.api);
    };

    const handleResetLayout = () => { if (api) loadDefaultLayout(api); };

    const handleAddGraph = (selectedKeys: string[]) => {
        if (!api || selectedKeys.length === 0) return;
        const panelId = `custom_graph_${Date.now()}`;
        const lines = selectedKeys.map((key, index) => {
            const channelInfo = AVAILABLE_CHANNELS.find(c => c.key === key);
            return {
                dataKey: key,
                label: channelInfo?.label || key,
                color: GRAPH_COLORS[index % GRAPH_COLORS.length]
            };
        });
        const title = lines.map(l => l.label).join(" / ");
        api.addPanel({
            id: panelId,
            component: 'chart_panel',
            title: 'Custom Graph',
            position: { direction: 'right' },
            params: { title: title, lines: lines }
        });
    };

    return (
        <div className="app-container">
            <AddGraphModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onAdd={handleAddGraph}
            />

            <div className="connection-bar">
                <div className="app-logo">
                    <span style={{ color: 'var(--accent-cyan)' }}>MANGUE</span>
                    <span style={{ color: '#fff', fontWeight: 'lighter' }}>TELEMETRY</span>
                </div>
                <div className="divider-v"></div>
                <div className="toolbar-group">
                    <div className="input-group">
                        <span className="input-label">HOST</span>
                        <input
                            className="connection-input"
                            value={inputIp}
                            onChange={(e) => setInputIp(e.target.value)}
                            placeholder="127.0.0.1"
                        />
                    </div>
                    <button
                        className={`btn-tech ${serverIp ? 'disconnect' : 'connect'}`}
                        onClick={() => setServerIp(inputIp)}
                    >
                        {serverIp ? "STOP" : "LINK"}
                        </button>
                        <button
                        className="btn-tech"
                        onClick={handleSetSF}
                        title="Set Start/Finish Line"
                        style={{ 
                            borderColor: activeSF ? 'var(--accent-green)' : '#444',
                            color: activeSF ? 'var(--accent-green)' : '#fff'
                        }}
                        >
                        SET S/F
                        </button>
                </div>
                <div className="divider-v"></div>
                <div className="toolbar-group">
                    <button
                        className="btn-tech"
                        onClick={() => setIsModalOpen(true)}
                        title="Add New Graph Panel"
                    >
                        + ADD GRAPH
                    </button>
                    <div className="mode-toggle">
                        <div
                            className={`mode-option ${viewMode === 'time' ? 'active' : ''}`}
                            onClick={() => setViewMode('time')}
                        >TIME</div>
                        <div
                            className={`mode-option ${viewMode === 'dist' ? 'active' : ''}`}
                            onClick={() => setViewMode('dist')}
                        >DIST</div>
                    </div>
                    <button className="btn-tech" onClick={handleResetLayout}>RESET UI</button>
                </div>
                <div className="divider-v"></div>

                <div className="session-info">
                    <div className="info-block">
                        <span className="info-label">LAP</span>
                        <span className="info-value" style={{ color: 'var(--accent-cyan)' }}>
                            {(incomingData?.lap_count || 0).toString().padStart(2, '0')}
                        </span>
                    </div>
                    
                    <div 
                        className="info-block mobile-hide" 
                        onClick={() => setDistMode(prev => prev === 'total' ? 'lap' : 'total')}
                        style={{ cursor: 'pointer', userSelect: 'none', minWidth: '80px' }}
                        title="Click to switch between Total and Lap distance"
                    >
                        <span className="info-label" style={{ color: distMode === 'lap' ? 'var(--accent-yellow)' : '#666' }}>
                            {distMode === 'total' ? "TOTAL DIST" : "LAP DIST"}
                        </span>
                        <span className="info-value">
                            {distMode === 'total' 
                                ? (incomingData?.total_distance ? (incomingData.total_distance / 1000).toFixed(2) : "0.00")
                                : (incomingData?.lap_distance ? (incomingData.lap_distance / 1000).toFixed(2) : "0.00")
                            } <span style={{fontSize: '10px', color: '#666'}}>km</span>
                        </span>
                    </div>

                    <div className="info-block">
                        <span className="info-label">CURRENT</span>
                        <span className="info-value time">
                            {formatLapTime(incomingData?.current_lap_time || 0)}
                        </span>
                    </div>
                    <div className="info-block mobile-hide">
                        <span className="info-label">LAST</span>
                        <span className="info-value">
                            {formatLapTime(incomingData?.last_lap_time || 0)}
                        </span>
                    </div>
                    <div className="info-block mobile-hide">
                        <span className="info-label">BEST</span>
                        <span className="info-value" style={{ color: 'var(--accent-green)' }}>
                            {formatLapTime(incomingData?.best_lap_time || 0)}
                        </span>
                    </div>
                </div>
                <span className={`connection-status ${incomingData ? 'status-connected' : 'status-disconnected'}`}>
                    {incomingData ? "● LIVE STREAM" : "○ OFFLINE"}
                </span>
            </div>

            <div style={{ flexGrow: 1, overflow: 'hidden' }}>
                <TelemetryProvider value={{ ...contextState, startFinishLine: activeSF }}>
                    <DockviewReact components={components} onReady={onReady} className="dockview-theme-dark" />
                </TelemetryProvider>
            </div>
        </div>
    );
};

export default Dashboard;
