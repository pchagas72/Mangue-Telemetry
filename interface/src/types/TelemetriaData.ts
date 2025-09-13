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
};
