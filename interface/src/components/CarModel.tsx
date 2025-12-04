// src/components/CarModel.tsx
import React from "react";
import "../pages/style.css";

interface CarModelProps {
    roll: number;
    pitch: number;
}

export const CarModel: React.FC<CarModelProps> = ({ roll, pitch }) => {
    // No useState or useEffect needed
    return (
        <div className="car-model-container">
            <div className="image-wrapper" style={{ transform: `rotateZ(${roll}deg)` }}>
                <img src="/baja_front.png" alt="Baja SAE Front View" className="baja-front" />
            </div>
            <div className="image-wrapper" style={{ transform: `rotateZ(${pitch}deg)` }}>
                <img src="/baja_side.png" alt="Baja SAE Side View" className="baja-side" />
            </div>
        </div>
    );
};
