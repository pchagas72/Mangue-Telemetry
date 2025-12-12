import { useEffect, useRef } from 'react';
import { useTelemetryData } from '../context/TelemetryContext';

export const GGDiagram = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const { latestData, history } = useTelemetryData();

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || !latestData) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const w = canvas.width;
        const h = canvas.height;
        const cx = w / 2;
        const cy = h / 2;
        const scale = Math.min(w, h) / 4; // Scale: 1G = 1/4th of screen size (allows up to 2G)

        // Clear Screen
        ctx.clearRect(0, 0, w, h);

        // Draw Grid (circle)
        ctx.lineWidth = 1;
        ctx.strokeStyle = '#333';
        ctx.fillStyle = '#111';

        // Rings: 0.5G, 1.0G, 1.5G
        [0.5, 1.0, 1.5].forEach(g => {
            ctx.beginPath();
            ctx.arc(cx, cy, g * scale, 0, Math.PI * 2);
            ctx.stroke();
            // Label
            ctx.fillStyle = '#666';
            ctx.font = '10px Consolas';
            ctx.fillText(`${g.toFixed(1)}G`, cx + 5, cy - (g * scale) - 5);
        });

        // Crosshair
        ctx.beginPath();
        ctx.moveTo(cx, 0); ctx.lineTo(cx, h);
        ctx.moveTo(0, cy); ctx.lineTo(w, cy);
        ctx.stroke();

        // Labels
        ctx.fillStyle = '#888';
        ctx.fillText("LATERAL", w - 50, cy - 5);
        ctx.fillText("LONG", cx + 5, 15);

        // Draws the data and 50 previous points
        const trailLength = Math.min(history.acc_x.length, 50);
        const startIndex = history.acc_x.length - trailLength;

        if (trailLength > 0) {
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';

            for (let i = 0; i < trailLength; i++) {
                const idx = startIndex + i;
                const gx = history.acc_y[idx] || 0; // Lateral
                const gy = history.acc_x[idx] || 0; // Longitudinal

                // Calculate Opacity: Older points are transparent
                const alpha = (i / trailLength); 
                
                const x = cx + (gx * scale);
                const y = cy - (gy * scale); // Invert Y because Canvas Y+ is down

                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(0, 255, 255, ${alpha})`;
                ctx.fill();
            }
        }

        // Draw Current Point (Ball)
        const currX = cx + (latestData.acc_y * scale);
        const currY = cy - (latestData.acc_x * scale);

        // Glow Effect
        const grad = ctx.createRadialGradient(currX, currY, 2, currX, currY, 10);
        grad.addColorStop(0, '#FFFFFF');
        grad.addColorStop(0.4, '#FFFF00'); // Yellow Core
        grad.addColorStop(1, 'rgba(255, 255, 0, 0)');

        ctx.beginPath();
        ctx.arc(currX, currY, 8, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();

        // Digital Readout overlay
        ctx.fillStyle = '#FFF';
        ctx.font = 'bold 12px Consolas';
        ctx.fillText(`X: ${latestData.acc_x.toFixed(2)}`, 10, h - 25);
        ctx.fillText(`Y: ${latestData.acc_y.toFixed(2)}`, 10, h - 10);

    }, [latestData, history]);

    // Handle Resize (Naive approach for canvas)
    useEffect(() => {
        const resize = () => {
            if (canvasRef.current && canvasRef.current.parentElement) {
                canvasRef.current.width = canvasRef.current.parentElement.clientWidth;
                canvasRef.current.height = canvasRef.current.parentElement.clientHeight;
            }
        };
        window.addEventListener('resize', resize);
        resize(); // Init
        return () => window.removeEventListener('resize', resize);
    }, []);

    return (
        <div style={{ width: '100%', height: '100%', background: '#000', overflow: 'hidden' }}>
            <canvas ref={canvasRef} style={{ display: 'block' }} />
        </div>
    );
};
