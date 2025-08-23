import { useEffect, useState } from 'react';
import type { TelemetriaData } from "../types/TelemetriaData.ts";

interface SerialProps {
    data: TelemetriaData;
}

const msgs: string[] = [];

export function Serial({ data }: SerialProps) {
    const [mensagens, setMensagens] = useState('');

    useEffect(() => {

        if (data.vel <= 5) {
            if (!msgs.includes('Carro muito devagar ou parado.')){
                msgs.push('Carro muito devagar ou parado.');
            }
        }
        if (data.rpm > 5000) {
            if (!msgs.includes('Rotação do motor extremamente alta.')){
                msgs.push('Rotação do motor extremamente alta.');
            }
        }
        if (data.temp_motor > 150) {
            if (!msgs.includes('Temperatura do motor extremamente alta.')){
                msgs.push('Temperatura do motor extremamente alta.');
            }
        }
        if (data.temp_cvt > 150) {
            if (!msgs.includes('Temperatura da CVT extremamente alta.')){
                msgs.push('Temperatura da CVT extremamente alta.');
            }
        }
        if (data.soc < 5) {
            if (!msgs.includes('Trocar bateria.')){
                msgs.push('Trocar bateria.');
            }
        }
        if (data.volt < 7) {
            if (!msgs.includes('Voltagem da bateria extremamente baixa.')){
                msgs.push('Voltagem da bateria extremamente baixa.');
            }
        }
        if (data.current < 200) {
            if (!msgs.includes('Corrente da bateria extremamente baixa.')){
                msgs.push('Corrente da bateria extremamente baixa.');
            }
        }
        if (msgs.length >= 10){
            msgs.shift();
        }

        setMensagens(msgs.join('\n'));
    }, [
            data.vel,
            data.rpm,
            data.temp_motor,
            data.temp_cvt,
            data.soc,
            data.volt,
            data.current
        ]);

    return (
        <div className="SerialDiv">
            <textarea
                value={mensagens}
                readOnly
                rows={15}
                cols={40}
                style={{ resize: 'none', fontFamily: 'monospace' }}
            />
        </div>
    );
}

