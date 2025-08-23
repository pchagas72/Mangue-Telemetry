"""
    Módulo que contêm a classe MangueTelemetry, responsável por
    receber e enviar dados de telemetria do carro.
"""
import asyncio

import aiomqtt


class MangueTelemetry:
    """
        Classe responsável por receber e enviar dados de telemetria.
    """

    def __init__(self,
                 hostname: str,
                 port: str,
                 username: str,
                 password: str
                 ):
        self.hostname = hostname
        self.port = int(port)
        self.username = username
        self.password = password
        self.queue = asyncio.Queue()  # fila para repassar mensagens
        self._task = None

    async def start(self):
        """
        Inicia a conexão MQTT e escuta mensagens em loop.
        Isso é necessário para manter a conexão sempre aberta,
        mesmo com o código modularizado.
        """
        self._task = asyncio.create_task(self._listen())

    async def _listen(self):
        """
            Essa função é um processo interno/privado (por isso o _)
            que escuta o canal MQTT e coloca os dados em uma fila.
        """
        async with aiomqtt.Client(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password
        ) as client:
            await client.subscribe("/logging")
            async for data in client.messages:
                payload = data.payload
                await self.queue.put(payload)  # adiciona na fila

    async def get_payload(self) -> bytes:
        """
            Retorna um elemento da fila de dados recebidos MQTT,
            mantendo a ordem de chegada.
        """
        return await self.queue.get()

    async def stop(self):
        """
            Cancela as tasks da telemetria.
        """
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
