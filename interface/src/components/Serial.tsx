import { useEffect, useState } from 'react';
import type { TelemetriaData } from "../types/TelemetriaData.ts";

// The msgs array is removed from here

export function Serial({ data }: { data: TelemetriaData }) {
    // Manage messages with useState, making it component-local state
    const [messages, setMessages] = useState<string[]>([]);

    useEffect(() => {
        const newMessages: string[] = [];

        // Check conditions and add new messages
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
        
        // This is a more robust way to update the list of messages
        setMessages(prevMsgs => {
            // Combine previous messages with new, unique messages
            const combined = [...prevMsgs, ...newMessages.filter(nm => !prevMsgs.includes(nm))];
            
            // Ensure the list does not exceed 10 items
            if (combined.length > 10) {
                return combined.slice(combined.length - 10);
            }
            return combined;
        });

    }, [data]); // Effect runs whenever data changes

    return (
        <div className="SerialDiv">
            <textarea
                value={messages.join('\n')} // Join the state array to display
                readOnly
                rows={15}
                cols={40}
                style={{ resize: 'none', fontFamily: 'monospace' }}
            />
        </div>
    );
}
