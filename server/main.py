"""
    Arquivo principal do servidor de telemetria da Mangue Baja.
    Aqui é realizada a captura, armazenamento e envio de dados recebidos do
    carro.
"""

import json
import asyncio
from dotenv import dotenv_values

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from telemetry.mangue_telemetry import MangueTelemetry
from data.mangue_data import MangueData
from simuladores.python.simulador import Simuladores


# Definindo constantes
SIMULAR_INTERFACE = True
credentials = dotenv_values("./credentials.env")

# Construindo classes
app = FastAPI()
telemetry = MangueTelemetry(
    hostname=credentials["HOSTNAME"],
    port=credentials["PORT"],
    username=credentials["USERNAME"],
    password=credentials["PASSWORD"]
)
data = MangueData()
sim = Simuladores()

# Criando variáveis globais
# Set (conjunto) para armazenar todas as conexões WebSocket ativas.
# Criar um conjunto evita repetições de maneira elegante.
active_websockets = set()


async def broadcast_telemetry():
    """
    Função de background que gera dados de simulação e envia
    para todos os clientes conectados.
    """
    try:
        while True:
            if SIMULAR_INTERFACE:
                sim_data = await sim.gerar_dados()
                message = json.dumps(sim_data)
                # Cria uma lista de mensagens a serem enviadas.
                await asyncio.gather(
                    *[ws.send_text(message) for ws in active_websockets],
                    # Permite que as tarefas falhem sem parar o gather.
                    return_exceptions=True
                )
            else:
                tel_data = await telemetry.get_payload()
                data_parsed = data.parse_mqtt_packet(tel_data)
                message = json.dumps(data_parsed)
                await asyncio.gather(
                    *[ws.send_text(message) for ws in active_websockets],
                    return_exceptions=True
                )

            # Pausa para evitar sobrecarga.
            await asyncio.sleep(0.5)

    except asyncio.CancelledError:
        print("[WebSocket] Task de broadcast cancelada.")


@app.on_event("startup")
async def startup_event():
    """
        Inicia todos os processos essenciais para a abertura do servidor e suas
        conexões.
    """
    if SIMULAR_INTERFACE:
        # Cria e inicia a tarefa de background para simulação.
        # Note que dados não serão salvos em simulações de interface.
        asyncio.create_task(broadcast_telemetry())
    else:
        # Inicia a conexão MQTT e o banco de dados.
        await telemetry.start()
        print("[Telemetry] Telemetry started")
        data.connect_to_db()
        print("[Database] Conected the db")
        data.create_schema()
        print("[Database] Created the db")
        data.start_new_session(label="Teste de produção 1")
        print("[Database] Started new section")
        asyncio.create_task(broadcast_telemetry())
        print("[Telemetry] Started broadcasting")


@app.websocket("/ws/telemetry")
async def telemetry_endpoint(websocket: WebSocket):
    """
        Endpoint que gerencia a conexão do cliente, adicionando-o
        à lista de conexões ativas.
    """
    await websocket.accept()
    print("[WebSocket] Novo cliente conectado.")
    active_websockets.add(websocket)
    try:
        await websocket.receive_text()
    except WebSocketDisconnect:
        print("[WebSocket] Cliente desconectado.")
    finally:
        active_websockets.remove(websocket)


@app.on_event("shutdown")
async def shutdown_event():
    """
        Finaliza todos os processos abertos para fechar todas as conexões.
    """
    if not SIMULAR_INTERFACE:
        await telemetry.stop()
        data.close_db()
