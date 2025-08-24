import React, { useState, useEffect } from "react";
import "../pages/style.css"; // Ensure you import your existing CSS file

interface CarModelProps {
    roll: number;
    pitch: number;
}

export const CarModel: React.FC<CarModelProps> = ({ roll, pitch }) => {
    const [rollRotation, setRollRotation] = useState(0);
    const [pitchRotation, setPitchRotation] = useState(0);

    useEffect(() => {
        // Apply rotation to the images
        // We'll use the roll and pitch values directly to set the rotation in degrees
        setRollRotation(roll);
        setPitchRotation(pitch);
    }, [roll, pitch]);

    return (
        <div className="car-model-container">
            <div className="image-wrapper" style={{ transform: `rotateZ(${rollRotation}deg)` }}>
                <img src="/baja_front.png" alt="Baja SAE Front View" className="baja-front" />
            </div>
            <div className="image-wrapper" style={{ transform: `rotateZ(${pitchRotation}deg)` }}>
                <img src="/baja_side.png" alt="Baja SAE Side View" className="baja-side" />
            </div>
        </div>
    );
};
