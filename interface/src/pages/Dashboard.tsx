// src/pages/Dashboard.tsx
import _React, { useEffect, useState } from "react";
import { DockviewReact, DockviewApi} from "dockview";
import type { IDockviewPanelProps } from "dockview";
import type { DockviewReadyEvent } from "dockview";
import "dockview/dist/styles/dockview.css";
import "./style.css";

// Internal Components
import { useTelemetry } from "../hooks/useTelemetry";
import { ChartPanel } from "../components/ChartPanel";
import { TelemetryProvider, useTelemetryData } from "../context/TelemetryContext";
import type { TelemetriaData } from "../types/TelemetriaData";
import { Mapa } from "../components/Mapa";
import { CarModel } from "../components/CarModel";
import { LiveCarPanel } from "../components/LiveCarPanel";
import { GGDiagram } from "../components/CGDiagram";

// --- Helpers ---
function getDistanceFromLatLonInM(lat1: number, lon1: number, lat2: number, lon2: number) {
  var R = 6371; 
  var dLat = deg2rad(lat2 - lat1);
  var dLon = deg2rad(lon2 - lon1);
  var a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  var d = R * c; 
  return d * 1000; 
}

function deg2rad(deg: number) {
  return deg * (Math.PI / 180);
}

const formatLapTime = (ms: number) => {
    const min = Math.floor(ms / 60000);
    const sec = Math.floor((ms % 60000) / 1000);
    const mil = Math.floor((ms % 1000) / 10); 
    return `${min}:${sec.toString().padStart(2, '0')}.${mil.toString().padStart(2, '0')}`;
};

// --- Helper Components ---
const MapPanel = () => {
    const { latestData, history, startFinishLine } = useTelemetryData();
    if (!latestData) return <div className="waiting-text">Waiting for connection...</div>;
    return(
        <div style={{ height: '100%', padding: '10px' }}>
            {Mapa(latestData.latitude, latestData.longitude, history.path, startFinishLine)}
        </div>
    )
}
const CarTilt = () => {
    const { latestData } = useTelemetryData();
    if (!latestData) return <div className="waiting-text">Waiting for connection...</div>;
    return(
        <div style={{ height: '100%', padding: '10px' }}>
            {CarModel(latestData.roll, latestData.pitch)}
        </div>
    )
}

// --- Register Components ---
const components = {
  map_panel: (_props: IDockviewPanelProps) => <MapPanel />,
  car_panel: (_props: IDockviewPanelProps) => <LiveCarPanel />,
  chart_panel: (props: IDockviewPanelProps) => <ChartPanel {...props} />,
  carTilt_panel: (_props: IDockviewPanelProps) => <CarTilt/>,
  gg_panel: (_props: IDockviewPanelProps) => <GGDiagram />, // NEW REGISTER
};

// --- Layout Logic ---
function loadDefaultLayout(api: DockviewApi) {
    api.clear();

    api.addPanel({
        id: 'map_panel',
        component: 'map_panel',
        title: 'GPS Map',
    });

    // Added G-G Diagram to the right of Live Data
    api.addPanel({
        id: 'carTilt_panel',
        component: 'carTilt_panel',
        title: 'Car Tilt Panel',
        position: { referencePanel: 'map_panel',direction: 'below' }
    });

    api.addPanel({
        id: 'speed_graph',
        component: 'chart_panel',
        title: 'Speed Graph',
        position: { direction: 'right' },
        params: { title: 'Velocity', dataKey: 'speeds', color: '#00FFFF' }
    });

    api.addPanel({
        id: 'rpm_graph',
        component: 'chart_panel',
        title: 'RPM Graph',
        position: { referencePanel: 'speed_graph', direction: 'below' },
        params: { title: 'RPM', dataKey: 'rpms', color: '#50DAB5' }
    });

    api.addPanel({
        id: 'car_panel',
        component: 'car_panel',
        title: 'Live Data',
        position: { direction: 'right' }
    });

    // Added G-G Diagram to the right of Live Data
    api.addPanel({
        id: 'gg_panel',
        component: 'gg_panel',
        title: 'G-G Diagram',
        position: { referencePanel: 'car_panel',direction: 'below' }
    });

}

const Dashboard = () => {
  const [api, setApi] = useState<DockviewApi>();
  const [serverIp, setServerIp] = useState<string>(""); 
  const [inputIp, setInputIp] = useState("localhost");
  const [viewMode, setViewMode] = useState<"time" | "dist">("time");
  
  const incomingData = useTelemetry(serverIp || null);

  const [session, setSession] = useState({
      lapCount: 0,
      currentLapStart: 0,     
      currentLapDuration: 0,  
      lastLapTime: 0,
      bestLapTime: 0,
      startFinishLine: null as { lat: number, lon: number } | null,
      isLapValid: false       
  });

  const [contextState, setContextState] = useState({
      latestData: null as TelemetriaData | null,
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
          path: [] as [number, number][],
      },
      connectedIp: null as string | null,
  });

  useEffect(() => {
    if (!incomingData) return;
    const now = Date.now();
    const lat = incomingData.latitude;
    const lon = incomingData.longitude;

    setSession(prev => {
        let newState = { ...prev };
        if (newState.currentLapStart === 0) newState.currentLapStart = now;
        newState.currentLapDuration = now - newState.currentLapStart;

        if (newState.startFinishLine && lat !== 0 && lon !== 0) {
            const dist = getDistanceFromLatLonInM(lat, lon, newState.startFinishLine.lat, newState.startFinishLine.lon);
            // Increased radius to 25m as discussed
            if (dist < 25 && newState.currentLapDuration > 10000) {
                const lapTime = newState.currentLapDuration;
                newState.lapCount += 1;
                newState.lastLapTime = lapTime;
                if (newState.bestLapTime === 0 || lapTime < newState.bestLapTime) {
                    newState.bestLapTime = lapTime;
                }
                newState.currentLapStart = now;
                newState.currentLapDuration = 0;
            }
        }
        return newState;
    });

  }, [incomingData]); 

  const handleSetSF = () => {
      if (contextState.latestData) {
          setSession(prev => ({
              ...prev,
              startFinishLine: { 
                  lat: contextState.latestData!.latitude, 
                  lon: contextState.latestData!.longitude 
              }
          }));
      }
  };

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
                      path: updatePath(prev.history.path, incomingData.latitude, incomingData.longitude) 
                  }
              };
          });
      }
  }, [incomingData, serverIp]);

  const onReady = (event: DockviewReadyEvent) => {
    setApi(event.api);
    loadDefaultLayout(event.api);
  };

  const handleResetLayout = () => { if (api) loadDefaultLayout(api); };

  return (
    <div className="app-container">
      <div className="connection-bar">
         <div className="app-logo">
            <span style={{color: 'var(--accent-cyan)'}}>MANGUE</span>
            <span style={{color: '#fff', fontWeight: 'lighter'}}>TELEMETRY</span>
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
                style={{borderColor: session.startFinishLine ? 'var(--accent-green)' : '#444'}}
            >
                {session.startFinishLine ? "S/F SET" : "SET S/F"}
            </button>
         </div>
         <div className="divider-v"></div>
         <div className="toolbar-group">
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
                 <span className="info-value" style={{color: 'var(--accent-cyan)'}}>
                    {session.lapCount.toString().padStart(2, '0')}
                 </span>
             </div>
             <div className="info-block">
                 <span className="info-label">CURRENT</span>
                 <span className="info-value time">
                    {formatLapTime(session.currentLapDuration)}
                 </span>
             </div>
             <div className="info-block mobile-hide">
                 <span className="info-label">LAST</span>
                 <span className="info-value">
                    {formatLapTime(session.lastLapTime)}
                 </span>
             </div>
             <div className="info-block mobile-hide">
                 <span className="info-label">BEST</span>
                 <span className="info-value" style={{color: 'var(--accent-green)'}}>
                    {formatLapTime(session.bestLapTime)}
                 </span>
             </div>
         </div>
         <span className={`connection-status ${incomingData ? 'status-connected' : 'status-disconnected'}`}>
            {incomingData ? "● LIVE STREAM" : "○ OFFLINE"}
         </span>
      </div>

      <div style={{ flexGrow: 1, overflow: 'hidden' }}>
        <TelemetryProvider value={{ ...contextState, startFinishLine: session.startFinishLine }}>
            <DockviewReact components={components} onReady={onReady} className="dockview-theme-dark" />
        </TelemetryProvider>
      </div>
    </div>
  );
};

export default Dashboard;
