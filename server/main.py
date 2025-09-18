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

# Setting up components
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
        # Concurrent sending
        await asyncio.gather(*[connection.send_text(message) for connection in self.active_connections])

# Building services
manager = ConnectionManager()
parser = DataParser(payload_fmt=settings.serial_packet_format)
db_service = DatabaseService(db_path=settings.database_path)
telemetry_service = None # Initialized in lifespan

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
    db_service.start_new_session(label=f"Sessão: {settings.data_source.upper()}")

    broadcast_task = asyncio.create_task(broadcast_telemetry())
    yield
    broadcast_task.cancel()
    # Code to run on shutdown
    if  settings.data_source != "simulator":
        await telemetry_service.stop()

    db_service.close()
    logger.info("Application shutdown complete.")

# Building fastAPI app
app = FastAPI(lifespan=lifespan)

async def broadcast_telemetry():
    """
    Continuously gets data from the selected source, parses it, saves to DB,
    and broadcasts to all connected WebSocket clients.
    """
    while True:
        print("new_loop")
        try:
            data_to_send = None
            if settings.data_source == "simulator":
                data_to_send = await telemetry_service.gerar_dados()
            else:
                payload = await telemetry_service.get_payload()
                if payload:
                    data_to_send = parser.parse_packet(payload)
            
            if data_to_send:
                db_service.save_telemetry_data(data_to_send)
                
                # Broadcasting
                logger.info(f"Broadcasting data: Speed={data_to_send.get('speed')}, RPM={data_to_send.get('rpm')}")

                if 'timestamp' in data_to_send and not isinstance(data_to_send['timestamp'], str):
                    data_to_send['timestamp'] = str(data_to_send['timestamp'])

                message = json.dumps(data_to_send)
                await manager.broadcast(message)
            
        except asyncio.CancelledError:
            logger.info("Broadcast task cancelled.")
            break
        except Exception as e:
            logger.error(f"[Broadcast Error] {e}", exc_info=True)

        await asyncio.sleep(settings.broadcast_delay_seconds)

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for the telemetry dashboard."""
    await manager.connect(websocket)
    logger.info(f"New client connected from {websocket.client.host}")
    try:
        while True:
            await websocket.receive_text() # Keeps connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client {websocket.client.host} disconnected.")
