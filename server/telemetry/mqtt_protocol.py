# mangue_telemetry.py (Modified for Real-Time Dashboard)

"""
    Módulo que contêm a classe MangueTelemetry, responsável por
    receber e enviar dados de telemetria do carro.
"""
import asyncio
import aiomqtt


class MqttProtocol:
    """
        Classe responsável por receber e enviar dados de telemetria.
        Esta versão foi modificada para priorizar os dados mais recentes,
        descartando pacotes intermediários para garantir baixa latência.
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
        self._latest_payload: bytes | None = None
        self._new_payload_event = asyncio.Event()
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
            Escuta o canal MQTT e sobrescreve a variável com o dado mais recente.
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
                self._latest_payload = payload
                # Notifica qualquer tarefa que esteja esperando pelo primeiro pacote
                self._new_payload_event.set()

    async def get_payload(self) -> bytes:
        """
            Retorna o payload mais recente recebido via MQTT.
            Se nenhum payload foi recebido ainda, espera pelo primeiro.
        """
        # Se for a primeira vez, espera o _listen receber algo
        if self._latest_payload is None:
            await self._new_payload_event.wait()

        return self._latest_payload

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
