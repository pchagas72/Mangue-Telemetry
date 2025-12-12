// All data received from the server goes here
export type TelemetriaData = {
    speed: number;
    rpm: number;
    temperature: number;
    temp_cvt: number;
    soc: number;
    volt: number;
    current: number;

    acc_x: number;
    acc_y: number;
    acc_z: number;

    dps_x: number;
    dps_y: number;
    dps_z: number;

    roll: number;
    pitch: number;
    latitude: number;
    longitude: number;
    timestamp: number;
    flags: number;
    path: [number, number][];
    lap_count: number;
    current_lap_time: number;
    last_lap_time: number;
    best_lap_time: number;
    gap_to_best?: number;
    sf_lat?: number;
    sf_lon?: number;
};
