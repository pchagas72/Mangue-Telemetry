// src/components/BarGauge.tsx
import React from "react";

interface BarGaugeProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  warning_value: number;
  critical_value: number;
  unit?: string;
  inverted?: boolean;
}

export const BarGauge: React.FC<BarGaugeProps> = ({
  label,
  value,
  min = 0,
  max = 100,
  warning_value,
  critical_value,
  unit = "",
  inverted = false,
}) => {
  const safeValue = Math.min(Math.max(value, min), max);
  const percentage = ((safeValue - min) / (max - min)) * 100;

  // Engineering Colors
  let color = "#00FF00"; // Green

  if (inverted) {
    if (value <= critical_value) color = "#FF3333";
    else if (value <= warning_value) color = "#FFFF00";
  } else {
    if (value >= critical_value) color = "#FF3333";
    else if (value >= warning_value) color = "#FFFF00";
  }

  return (
    <div className="bar-gauge-container">
      <div className="bar-gauge-header">
        <span style={{ color: '#aaa' }}>{label}</span>
        <span style={{ color: 'white', fontWeight: 'bold' }}>
            {value.toFixed(1)}{unit}
        </span>
      </div>
      
      <div className="bar-bg">
        <div 
            className="bar-fill"
            style={{ 
                width: `${percentage}%`, 
                background: color,
            }} 
        />
      </div>
    </div>
  );
};
