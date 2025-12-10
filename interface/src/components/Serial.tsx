import { useEffect, useState } from 'react';
import type { TelemetriaData } from "../types/TelemetriaData.ts";

export function Serial({ data }: { data: TelemetriaData }) {
    const [messages, setMessages] = useState<string[]>([]);

    useEffect(() => {
        const newMessages: string[] = [];

        if (data.speed <= 5) {
            newMessages.push('Carro muito devagar ou parado.');
        }
        if (data.rpm > 5000) {
            newMessages.push('Rotação do motor extremamente alta.');
        }
        if (data.temperature > 150) {
            newMessages.push('Temperatura do motor extremamente alta.');
        }
        if (data.temp_cvt > 150) {
            newMessages.push('Temperatura da CVT extremamente alta.');
        }
        if (data.soc < 5) {
            newMessages.push('Trocar bateria.');
        }
        if (data.volt < 7) {
            newMessages.push('Voltagem da bateria extremamente baixa.');
        }
        
        setMessages(prevMsgs => {
            const combined = [...prevMsgs, ...newMessages.filter(nm => !prevMsgs.includes(nm))];
            
            if (combined.length > 10) {
                return combined.slice(combined.length - 10);
            }
            return combined;
        });

    }, [data]);

    return (
        <div className="SerialDiv">
            <textarea
                value={messages.join('\n')}
                readOnly
                rows={15}
                cols={40}
                style={{ resize: 'none', fontFamily: 'monospace' }}
            />
        </div>
    );
}
