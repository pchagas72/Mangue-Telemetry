import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from settings import settings
from services.parser import DataParser
from services.database import DatabaseService
from telemetry.telemetry_serial import SerialTelemetry
from simuladores.python.simulador import Simuladores

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Create instances of the services and managers
manager = ConnectionManager()
parser = DataParser(payload_fmt=settings.serial_packet_format)
sim = Simuladores()
db_service = DatabaseService(db_path=settings.database_path)

# Initialize the serial telemetry service with the correct port and packet format

telemetry_service = SerialTelemetry(
    port=settings.serial_port,
    baudrate=settings.serial_baudrate,
    packet_format=settings.serial_packet_format
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown events.
    """
    # Code to run on startup
    if not settings.simular_interface:
        await telemetry_service.start()
        db_service.connect()
        db_service.create_schema()
        db_service.start_new_session(label="Produção Serial")

    # Start the main telemetry broadcasting loop
    asyncio.create_task(broadcast_telemetry())
    yield
    # Code to run on shutdown
    if not settings.simular_interface:
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
            if settings.simular_interface:
                data_to_send = await sim.gerar_dados()
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
