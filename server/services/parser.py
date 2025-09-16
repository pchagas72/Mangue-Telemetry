# server/services/parser.py
import struct
from typing import Dict, Any

class DataParser:
    """
    Decodes the raw binary telemetry payload into a structured dictionary.
    """
    def __init__(self, payload_fmt: str):
        self.payload_fmt = payload_fmt
        try:
            self.expected_size = struct.calcsize(self.payload_fmt)
        except struct.error as e:
            raise ValueError(f"Invalid packet format string: {e}")

    def parse_packet(self, payload: bytes) -> Dict[str, Any] | None:
        """
        Parses a raw byte payload into a dictionary with physical units.
        Returns None if the packet is invalid.
        """
        if len(payload) != self.expected_size:
            print(f"[Parser] ERRO: Tamanho do payload inesperado: {len(payload)}. Esperado: {self.expected_size}")
            return None

        raw = struct.unpack(self.payload_fmt, payload)

        # These conversion formulas should match the firmware or sensor datasheets.
        processed_data = {
            "volt": raw[0],
            "soc": raw[1],
            "temp_cvt": raw[2],
            "current": raw[3],
            "temperature": raw[4],
            "speed": raw[5],
            
            # Accelerometer Conversion (to G-force)
            "acc_x": (raw[6] * 0.061) / 1000.0,
            "acc_y": (raw[7] * 0.061) / 1000.0,
            "acc_z": (raw[8] * 0.061) / 1000.0,

            # Gyroscope Conversion (to degrees per second)
            "dps_x": (raw[9] * 70.0) / 1000.0,
            "dps_y": (raw[10] * 70.0) / 1000.0,
            "dps_z": (raw[11] * 70.0) / 1000.0,

            "roll": raw[12],
            "pitch": raw[13],
            "rpm": raw[14],
            "flags": raw[15],
            "latitude": raw[16],
            "longitude": raw[17],
            "timestamp": raw[18],
        }
        return processed_data
