import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from settings import settings
from services.parser import DataParser
from services.database import DatabaseService
from telemetry.mangue_telemetry import MangueTelemetry
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

# Create instances of our services and managers
# These will be treated like singletons for the app's lifespan
manager = ConnectionManager()
parser = DataParser()
sim = Simuladores()
db_service = DatabaseService(db_path=settings.database_path)
telemetry_service = MangueTelemetry(
    hostname=settings.mqtt_hostname,
    port=settings.mqtt_port,
    username=settings.mqtt_username,
    password=settings.mqtt_password
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    if not settings.simular_interface:
        await telemetry_service.start()
        db_service.connect()
        db_service.create_schema()
        db_service.start_new_session(label="Produção")
    
    # Start the main broadcast loop
    asyncio.create_task(broadcast_telemetry())
    
    yield
    
    # Code to run on shutdown
    if not settings.simular_interface:
        await telemetry_service.stop()
        db_service.close()

app = FastAPI(lifespan=lifespan)

async def broadcast_telemetry():
    while True:
        try:
            if settings.simular_interface:
                data_to_send = await sim.gerar_dados()
            else:
                payload = await telemetry_service.get_payload()
                data_to_send = parser.parse_mqtt_packet(payload)
                # db_service.save_telemetry_data(data_to_send) # Uncomment to save data
            
            message = json.dumps(data_to_send)
            await manager.broadcast(message)

        except Exception as e:
            print(f"[Broadcast Error] {e}")

        await asyncio.sleep(settings.broadcast_delay_seconds)


@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, can add logic here to handle client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WebSocket] Cliente desconectado.")
