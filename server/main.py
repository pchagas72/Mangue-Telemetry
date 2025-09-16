import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from settings import settings
from services.parser import DataParser
from services.database import DatabaseService
from telemetry.telemetry_serial import SerialTelemetry
from telemetry.mangue_telemetry import MangueTelemetry
from simuladores.python.simulador import Simuladores

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Change this to concurrent sending
        for connection in self.active_connections:
            await connection.send_text(message)

# Building services
manager = ConnectionManager()
parser = DataParser(payload_fmt=settings.serial_packet_format)
sim = Simuladores()
db_service = DatabaseService(db_path=settings.database_path)
telemetry_service = None

telemetry_service = SerialTelemetry(
    port=settings.serial_port,
    baudrate=settings.serial_baudrate,
    packet_format=settings.serial_packet_format
)

def get_telemetry_service():
    """
        Gets the selected telemetry service (see settings.py)
    """
    source = settings.data_source
    if source == "serial":
        logger.info("Using LoRa serial as data source")
        return SerialTelemetry(port=settings.serial_port,
                               baudrate=settings.serial_baudrate,
                               packet_format=settings.serial_packet_format)
    elif source == "mqtt":
        logger.info("Using MQTT as data source.")
        return MangueTelemetry(hostname=settings.mqtt_hostname,
                               port=settings.mqtt_port,
                               username=settings.mqtt_username,
                               password=settings.mqtt_password)
    elif source == "simulator":
        logger.info("Using simulated data source.")
        return Simuladores()
    else:
        raise ValueError(f"Unknown data source selected, check settings.py")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown events.
    """
    # Code to run on startup
    global telemetry_service
    telemetry_service = get_telemetry_service()

    if settings.data_source != "simulator":
        await telemetry_service.start()
        db_service.connect()
        db_service.create_schema()
        db_service.start_new_session(label="Produção Serial")

    # Start the main telemetry broadcasting loop
    asyncio.create_task(broadcast_telemetry())
    yield
    # Code to run on shutdown
    if  settings.data_source != "simulator":
        await telemetry_service.stop()
        db_service.close()

app = FastAPI(lifespan=lifespan)

async def broadcast_telemetry():
    """
    Continuously gets data (either from the simulator or the serial port),
    parses it, and broadcasts it to all connected WebSocket clients.
    """
    while True:
        try:
            if settings.data_source == "simulator":
                data_to_send = await telemetry_service.gerar_dados()
            else:
                payload = await telemetry_service.get_payload()
                if payload:
                    data_to_send = parser.parse_mqtt_packet(payload)
                    # Debugging: print the processed payload bytes
                    print(data_to_send)
                    if not data_to_send: # Skip if the packet was invalid
                        continue
                else:
                    continue

            message = json.dumps(data_to_send)
            await manager.broadcast(message)

        except Exception as e:
            print(f"[Broadcast Error] {e}")

        await asyncio.sleep(settings.broadcast_delay_seconds)


@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections for the telemetry dashboard.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WebSocket] Cliente desconectado.")
