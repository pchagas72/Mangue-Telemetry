# server/services/parser.py
import struct
from typing import Dict, Any

class DataParser:
    """
    Classe responsável exclusivamente por decodificar o payload binário da telemetria.
    """
    # This format string now correctly matches the C++ struct.
    def __init__(self, payload_fmt: str = "<fBfBHHhhh hhh hhH BddI"):
        self.payload_fmt = payload_fmt
        self.expected_size = struct.calcsize(self.payload_fmt)

    def parse_mqtt_packet(self, payload: bytes) -> Dict[str, Any]:
        if len(payload) != self.expected_size:
            print(f"[Parser] ERRO: Tamanho do payload inesperado: {len(payload)}. Esperado: {self.expected_size}")
            # We return an empty dict to avoid crashing the server on a bad packet
            return {}

        raw = struct.unpack(self.payload_fmt, payload)

        processed_data = {
            "volt": raw[0],
            "soc": raw[1],
            "temp_cvt": raw[2],
            "current": raw[3],
            "temperature": raw[4],
            "speed": raw[5],
            # IMU Acceleration
            "acc_x": (raw[6] * 0.061) / 1000.0,
            "acc_y": (raw[7] * 0.061) / 1000.0,
            "acc_z": (raw[8] * 0.061) / 1000.0,
            # IMU Gyroscope
            "dps_x": (raw[9] * 70.0) / 1000.0,
            "dps_y": (raw[10] * 70.0) / 1000.0,
            "dps_z": (raw[11] * 70.0) / 1000.0,
            # Angle
            "roll": raw[12],
            "pitch": raw[13],
            "rpm": raw[14],
            "flags": raw[15],
            # GPS Data
            "latitude": raw[16],
            "longitude": raw[17],
            "timestamp": raw[18],
        }
        return processed_data
