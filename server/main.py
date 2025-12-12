import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from settings import settings
from services.parser import DataParser
from services.database import DatabaseService
from services.data_processing import DataProcessing
from telemetry.serial_receiver import SerialTelemetry
from telemetry.mqtt_protocol import MqttProtocol
from simuladores.python.simulador import Simulador

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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Handle empty lists gracefully
        if not self.active_connections:
            return
        await asyncio.gather(*[connection.send_text(message) for connection in self.active_connections])

# Building services
manager = ConnectionManager() # The connection manager takes care of each client
parser = DataParser(payload_fmt=settings.serial_packet_format) # Parses raw serial received data
db_service = DatabaseService(db_path=settings.database_path) # DB interface
data_processing = DataProcessing() # Responsable for processing any data required by the front end
telemetry_service = None # SerialTelemetry, MqttProtocol or Simulador

# Helper for history
history_buffer = []
MAX_BUFFER = 500

def get_telemetry_service():
    """ Gets the selected telemetry service """
    source = settings.data_source
    if source == "serial":
        return SerialTelemetry(port=settings.serial_port,
                               baudrate=settings.serial_baudrate,
                               packet_format=settings.serial_packet_format)
    elif source == "mqtt":
        return MqttProtocol(hostname=settings.mqtt_hostname,
                               port=settings.mqtt_port,
                               username=settings.mqtt_username,
                               password=settings.mqtt_password)
    elif source == "simulator":
        return Simulador()
    else:
        raise ValueError(f"Unknown data source: {source}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telemetry_service
    telemetry_service = get_telemetry_service()
    broadcast_task = None

    if settings.data_source != "simulator":
        await telemetry_service.start()
        db_service.connect()
        db_service.create_schema()
        db_service.start_new_session(label=f"Sessão: {settings.data_source.upper()}")

    broadcast_task = asyncio.create_task(broadcast_telemetry())

    yield

    if broadcast_task:
        broadcast_task.cancel()
    if settings.data_source != "simulator":
        await telemetry_service.stop()
    db_service.close()

app = FastAPI(lifespan=lifespan)

# Allow CORS so your React app can hit the API endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def broadcast_telemetry():
    while True:
        try:
            data_to_send = None
            if settings.data_source == "simulator":
                data_to_send = await telemetry_service.gerar_dados()
            else:
                payload = await telemetry_service.get_payload()
                if payload:
                    data_to_send = parser.parse_packet(payload)
            
            if data_to_send:
                if settings.data_source != "simulator":
                    db_service.save_telemetry_data(data_to_send)

                # Do post processing needed for the interface display
                # Apply filters and calculate new variables here
                # Do not mix this up with the math channel
                enriched_data = data_processing.process_packet(data_to_send)
                
                # History Buffer
                # This allows for quicker rendering of the last 500 points
                history_buffer.append(enriched_data)
                if len(history_buffer) > MAX_BUFFER:
                    history_buffer.pop(0)

                # Send data
                await manager.broadcast(json.dumps(enriched_data))
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Broadcast Error: {e}")
            await asyncio.sleep(1) # Prevent tight loop on error

        await asyncio.sleep(settings.broadcast_delay_seconds)

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Endpoint to set S/F Line
# This is essential for the lap counter
@app.post("/api/set-sf")
async def set_start_finish():
    if history_buffer:
        last_packet = history_buffer[-1]
        lat = last_packet.get('latitude')
        lon = last_packet.get('longitude')
        if lat and lon:
            data_processing.set_sf_line(lat, lon)
            return {"status": "ok", "location": {"lat": lat, "lon": lon}}
    return {"status": "error", "message": "No GPS data available"}

@app.get("/api/session/history")
async def get_history():
    """
    Returns the cached telemetry history so new clients 
    can populate their graphs immediately.
    """
    # Return the global buffer (last 500 points)
    return history_buffer
