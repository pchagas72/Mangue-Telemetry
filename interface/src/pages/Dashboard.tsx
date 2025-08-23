import "./style.css";
import { ChartGrafico } from "../components/ChartGrafico";
import { Mapa } from "../components/Mapa";
import { Bateria } from "../components/Bateria";
import { Serial } from "../components/Serial";
import { useTelemetry } from "../hooks/useTelemetry";
import { useEffect, useState } from "react";

export default function Dashboard() {
    const data = useTelemetry();

    const [layout, setLayout] = useState<"mapa" | "dados" | "graficos">("graficos");

    const [timestamps, setTimestamps] = useState<number[]>([]);
    const [velocidades, setVelocidades] = useState<number[]>([]);
    const [rpms, setRpms] = useState<number[]>([]);
    const [temps_motor, setTemps_motor] = useState<number[]>([]);
    const [temps_cvt, setTemps_cvt] = useState<number[]>([]);
    const [aceleracoesX, setAceleracoesX] = useState<number[]>([]);
    const [aceleracoesY, setAceleracoesY] = useState<number[]>([]);
    const [aceleracoesZ, setAceleracoesZ] = useState<number[]>([]);
    const [caminho, setCaminho] = useState<[number, number][]>([]);

    useEffect(() => {
        if (data) {
            const timestamp = Date.now();

            // Adiciona timestamp se qualquer dado válido chegar
            let novoDado = false;

            if (typeof data.vel === "number") {
                setVelocidades((prev) => [...prev.slice(-99), data.vel]);
                novoDado = true;
            }
            if (typeof data.rpm === "number") {
                setRpms((prev) => [...prev.slice(-99), data.rpm]);
                novoDado = true;
            }
            if (typeof data.temp_motor === "number") {
                setTemps_motor((prev) => [...prev.slice(-99), data.temp_motor]);
                novoDado = true;
            }
            if (typeof data.temp_cvt === "number") {
                setTemps_cvt((prev) => [...prev.slice(-99), data.temp_cvt]);
                novoDado = true;
            }
            if (typeof data.accx === "number") {
                setAceleracoesX((prev) => [...prev.slice(-99), data.accx]);
                novoDado = true;
            }
            if (typeof data.accy === "number") {
                setAceleracoesY((prev) => [...prev.slice(-99), data.accy]);
                novoDado = true;
            }
            if (typeof data.accz === "number") {
                setAceleracoesZ((prev) => [...prev.slice(-99), data.accz]);
                novoDado = true;
            }

            // Se entrou pelo menos um valor válido, adiciona timestamp correspondente
            if (novoDado) {
                setTimestamps((prev) => [...prev.slice(-99), timestamp]);
            }
            // GPS com tolerância
            if (!isNaN(data.latitude) && !isNaN(data.longitude)) {
                const pos: [number, number] = [data.latitude, data.longitude];
                const last = caminho.at(-1);

                // tolerância de 1e-5 graus (~1m)
                const tol = 1e-5;
                if (
                    !last ||
                    Math.abs(last[0] - pos[0]) > tol ||
                    Math.abs(last[1] - pos[1]) > tol
                ) {
                    setCaminho((prev) => [...prev, pos]);
                }
            }
        }

    }, [data]);

    return (
        <div className="dashboard">
            <div className="sideBar">
                <img className="mangue_logo" src="/mangue_logo_white.avif"/>
                <button
                    onClick={() => setLayout("mapa")}
                >
                    Mapa
                </button>
                <button
                    onClick={() => setLayout("dados")}
                >
                    Dados
                </button>
                <button
                    onClick={() => setLayout("graficos")}
                >
                    Gráficos
                </button>
            </div>
            <main className="main_window">
                {layout === "mapa" && (
                    <div className="map_layout">
                        <div className="map_layout_map">
                            {data && <Mapa latitude={data.latitude} longitude={data.longitude} caminho={caminho} />}
                        </div>
                        <div className="map_layout_below">
                            <div className="map_layout_databoxes">
                                <div className="map_layout_databox">
                                    <h3>Velocidade</h3>
                                    <p>{data?.vel ?? 'N/A'} km/h</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>RPM</h3>
                                    <p>{data?.rpm ?? 'N/A'}</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>Temp. Motor</h3>
                                    <p>{data?.temp_motor ?? 'N/A'} ºC</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>Temp. CVT</h3>
                                    <p>{data?.temp_cvt ?? 'N/A'} ºC</p>
                                </div>
                            </div>
                            <div className="map_layout_below_right">
                                {data && <Serial data={data} />}
                                {data && <Bateria soc={data.soc} tensao={data.volt} corrente={data.current} />}
                            </div>
                        </div>
                    </div>
                )}
                {layout === "dados" && (
                    <div className="graficos_dashboard">
                        <div className="left_panel">
                            <div className="map_layout_databoxes">
                                <div className="map_layout_databox">
                                    <h3>Velocidade</h3>
                                    <p>{data?.vel ?? 'N/A'} km/h</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>RPM</h3>
                                    <p>{data?.rpm ?? 'N/A'}</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>Temp. Motor</h3>
                                    <p>{data?.temp_motor ?? 'N/A'} ºC</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>Temp. CVT</h3>
                                    <p>{data?.temp_cvt ?? 'N/A'} ºC</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>Aceleração X</h3>
                                    <p>{data?.accx ?? 'N/A'}</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>Aceleração Y</h3>
                                    <p>{data?.accy ?? 'N/A'}</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>Aceleração Z</h3>
                                    <p>{data?.accz ?? 'N/A'}</p>
                                </div>
                                <div className="map_layout_databox">
                                    <h3>GPS</h3>
                                    <p>Lat: {data?.latitude.toFixed(4) ?? 'N/A'}</p>
                                    <p>Lon: {data?.longitude.toFixed(4) ?? 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                        <div className="right_panel">
                            {data && <Serial data={data} />}
                            {data && <Bateria soc={data.soc} tensao={data.volt} corrente={data.current} />}
                        </div>
                    </div>
                )}

                {layout === "graficos" && (
                    <div className="graficos_dashboard">
                        <div className="left_panel">
                            <ChartGrafico
                                titulo="Velocidade"
                                timestamps={timestamps}
                                series={[
                                    {
                                        label: "Velocidade",
                                        valores: velocidades,
                                        cor: "#a6e3a1",
                                    },
                                ]}
                            />
                            <ChartGrafico
                                titulo="RPM"
                                timestamps={timestamps}
                                series={[
                                    {
                                        label: "RPM",
                                        valores: rpms,
                                        cor: "#a6e3a1",
                                    },
                                ]}
                            />
                            <div className="graficos_temperatura">
                                <ChartGrafico
                                    titulo="Temperatura Motor (ºC)"
                                    timestamps={timestamps}
                                    series={[
                                        {
                                            label: "Temp. Motor",
                                            valores: temps_motor,
                                            cor: "#a6e3a1",
                                        },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Temperatura CVT (ºC)"
                                    timestamps={timestamps}
                                    series={[
                                        {
                                            label: "Temp. CVT",
                                            valores: temps_cvt,
                                            cor: "#a6e3a1",
                                        },
                                    ]}
                                />
                            </div>
                            <div className="graficos_acc">
                                <ChartGrafico
                                    titulo="Aceleração X"
                                    timestamps={timestamps}
                                    series={[
                                        {
                                            label: "accX",
                                            valores: aceleracoesX,
                                            cor: "#74c7ec",
                                        },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Aceleração Y"
                                    timestamps={timestamps}
                                    series={[
                                        {
                                            label: "accY",
                                            valores: aceleracoesY,
                                            cor: "#74c7ec",
                                        },
                                    ]}
                                />
                                <ChartGrafico
                                    titulo="Aceleração Z"
                                    timestamps={timestamps}
                                    series={[
                                        {
                                            label: "accZ",
                                            valores: aceleracoesZ,
                                            cor: "#74c7ec",
                                        },
                                    ]}
                                />
                            </div>

                        </div>

                        <div className="right_panel">
                            {data && <Mapa latitude={data.latitude} longitude={data.longitude} caminho={caminho} />}
                            {data && <Serial data={data} />}
                            {data && <Bateria soc={data.soc} tensao={data.volt} corrente={data.current} />}
                        </div>

                    </div>
                )}
            </main>
        </div>
    );
}
