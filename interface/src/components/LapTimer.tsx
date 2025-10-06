import { useState, useEffect, useRef } from 'react';

export function LapTimer() {
    const [laps, setLaps] = useState<number[]>([]);
    const [timer, setTimer] = useState<number>(0);
    const [running, setRunning] = useState<boolean>(false);
    const lapsListRef = useRef<HTMLUListElement>(null);

    useEffect(() => {
        let interval: number;
        if (running) {
            interval = setInterval(() => {
                setTimer(prev => prev + 10);
            }, 10);
        }
        return () => clearInterval(interval);
    }, [running]);

    useEffect(() => {
        if (lapsListRef.current) {
            lapsListRef.current.scrollTop = lapsListRef.current.scrollHeight;
        }
    }, [laps]);

    const handleStartStop = () => {
        setRunning(!running);
    };

    const handleLap = () => {
        setLaps(prev => [...prev, timer]);
    };

    const handleReset = () => {
        setTimer(0);
        setLaps([]);
        setRunning(false);
    };

    const formatTime = (time: number) => {
        const minutes = Math.floor(time / 60000);
        const seconds = Math.floor((time % 60000) / 1000);
        const milliseconds = time % 1000;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
    };

    return (
        <div className="bateria_container">
            <h3>Lap Timer</h3>
            <p style={{ fontSize: '2rem', textAlign: 'center' }}>{formatTime(timer)}</p>
            <div className="lap-timer-buttons">
                <button onClick={handleStartStop} className={`lap-button ${running ? 'stop' : 'start'}`}>{running ? 'Stop' : 'Start'}</button>
                <button onClick={handleLap} disabled={!running} className="lap-button lap">Lap</button>
                <button onClick={handleReset} className="lap-button reset">Reset</button>
            </div>
            <ul className="lap-list" ref={lapsListRef}>
                {laps.map((lap, index) => (
                    <li key={index}>Lap {index + 1}: {formatTime(lap)}</li>
                ))}
            </ul>
        </div>
    );
}
