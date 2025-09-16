# server/telemetry/telemetry_serial.py
import asyncio
import serial
import struct
from collections import deque
import logging # Use the logging module

logger = logging.getLogger(__name__)

class SerialTelemetry:
    """
    Handles receiving telemetry data from a serial port using a robust queue.
    """
    def __init__(self, port: str, baudrate: int, packet_format: str):
        self.port = port
        self.baudrate = baudrate
        self.packet_format = packet_format
        self.packet_size = struct.calcsize(self.packet_format)
        self.start_marker = b'\xaa\xbb\xcc\xdd'
        self._task = None
        self.ser = None
        self.queue = asyncio.Queue(maxsize=10)

    async def start(self):
        """
        Initializes the serial connection asynchronously and starts listening for data.
        """
        loop = asyncio.get_running_loop()
        try:
            # --- FIX: Run the blocking serial connection in an executor ---
            self.ser = await loop.run_in_executor(
                None,
                lambda: serial.Serial(self.port, self.baudrate, timeout=1)
            )
            logger.info(f"[Serial] Conectado na porta {self.port}")
            self._task = asyncio.create_task(self._listen())
        except serial.SerialException as e:
            logger.error(f"[Serial] Erro ao abrir a porta serial: {e}")
            self._task = None

    async def _listen(self):
        """
        Listens for a start marker, reads a complete packet, and puts it on the queue.
        """
        loop = asyncio.get_event_loop()
        buffer = deque(maxlen=len(self.start_marker))
        logger.info("[Serial] Listening for incoming data...")

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
                        logger.info(f"[Serial] Pacote completo recebido ({self.packet_size} bytes)")
                        if self.queue.full():
                            await self.queue.get() # Discard oldest if full
                        await self.queue.put(payload)

            except Exception as e:
                logger.error(f"[Serial] Erro durante a leitura: {e}", exc_info=True)
                break

    async def get_payload(self) -> bytes:
        """Returns the latest data packet from the queue."""
        return await self.queue.get()

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.info("[Serial] Conexão serial fechada.")
