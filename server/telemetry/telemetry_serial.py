# server/telemetry/telemetry_serial.py
import asyncio
import serial
import struct
from collections import deque

class SerialTelemetry:
    """
        Handles receiving telemetry data from a serial port.
    """

    def __init__(self, port: str, baudrate: int, packet_format: str):
        self.port = port
        self.baudrate = baudrate
        self.packet_format = packet_format
        self.packet_size = struct.calcsize(self.packet_format)
        self.start_marker = b'\xaa\xbb\xcc\xdd'
        self._latest_payload: bytes | None = None
        self._new_payload_event = asyncio.Event()
        self._task = None
        self.ser = None

    async def start(self):
        """
            Initializes the serial connection and starts listening for data.
        """
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"[Serial] Conectado na porta {self.port}")
            self._task = asyncio.create_task(self._listen())
        except serial.SerialException as e:
            print(f"[Serial] Erro ao abrir a porta serial: {e}")
            self._task = None

    async def _listen(self):
        """
            Listens for a start marker and then reads a complete packet.
        """
        loop = asyncio.get_event_loop()
        buffer = deque(maxlen=len(self.start_marker))

        while True:
            try:
                byte = await loop.run_in_executor(None, self.ser.read, 1)
                if not byte:
                    await asyncio.sleep(0.01)
                    continue

                buffer.append(byte)

                if b"".join(buffer) == self.start_marker:
                    payload = await loop.run_in_executor(
                        None, self.ser.read, self.packet_size
                    )
                    
                    if len(payload) == self.packet_size:
                        self._latest_payload = payload
                        self._new_payload_event.set()
                        self._new_payload_event.clear()

            except Exception as e:
                print(f"[Serial] Erro durante a leitura: {e}")
                break

    async def get_payload(self) -> bytes:
        """
            Returns the latest data packet from the serial port.
        """
        await self._new_payload_event.wait()
        return self._latest_payload

    async def stop(self):
        """
            Closes the serial connection and stops the listening task.
        """
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[Serial] Conexão serial fechada.")
