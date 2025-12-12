// src/components/LiveCarPanel.tsx
import { useTelemetryData } from "../context/TelemetryContext";
import { BarGauge } from "./BarGauge";

export const LiveCarPanel = () => {
  const { latestData } = useTelemetryData();

  if (!latestData) return (
    <div style={{
        height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', 
        color: '#444', fontFamily: 'monospace', letterSpacing: '2px'
    }}>
        AWAITING DATA LINK...
    </div>
  );

  return (
    <div className="live-data-container">
      {/* Metric Grid */}
      <div className="data-grid">
        <div className="data-box">
          <span className="data-label">Speed</span>
          <span className="data-value" style={{color: 'var(--accent-cyan)'}}>
            {latestData.speed.toFixed(1)}<span className="data-unit">km/h</span>
          </span>
        </div>
        <div className="data-box">
          <span className="data-label">Engine</span>
          <span className="data-value" style={{color: 'var(--accent-green)'}}>
            {latestData.rpm.toFixed(0)}<span className="data-unit">RPM</span>
          </span>
        </div>
        <div className="data-box">
          <span className="data-label">Battery</span>
          <span className="data-value">
            {latestData.volt.toFixed(1)}<span className="data-unit">V</span>
          </span>
        </div>
        <div className="data-box">
          <span className="data-label">Current</span>
          <span className="data-value">
            {latestData.current.toFixed(2)}<span className="data-unit">A</span>
          </span>
        </div>
      </div>

      {/* Bar Gauges */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '0 5px' }}>
          <BarGauge label="ENG TEMP" value={latestData.temperature} max={150} warning_value={100} critical_value={120} unit="°C" />
          <BarGauge label="CVT TEMP" value={latestData.temp_cvt} max={150} warning_value={90} critical_value={110} unit="°C" />
          <BarGauge label="SOC" value={latestData.soc} max={100} warning_value={30} critical_value={15} unit="%" inverted={true} />
      </div>
    </div>
  );
};
