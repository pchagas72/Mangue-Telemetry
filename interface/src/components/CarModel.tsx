// src/components/CarModel.tsx
import "../pages/style.css";


export const CarModel = (roll: number, pitch: number) => {
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
