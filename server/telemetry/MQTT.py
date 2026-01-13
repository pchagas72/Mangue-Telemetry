import asyncio
import aiomqtt
import logging
import ssl

# Configure logging
logger = logging.getLogger(__name__)

class MqttProtocol:
    """
    Classe responsável por receber e enviar dados de telemetria via MQTT.
    Gerencia conexão segura (SSL) e reconexão automática.
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
        Inicia a tarefa de escuta MQTT em segundo plano.
        """
        self._task = asyncio.create_task(self._listen())

    def ping(self):
        """
        Loga mensagem confirmando conexão ativa.
        """
        logger.info(f"[MQTT] Connected to broker {self.hostname}")
        logger.info(f"[MQTT] Listening to /logging")

    async def _listen(self):
        """
        Loop principal que gerencia a conexão e assinatura dos tópicos.
        Inclui tratamento de erros e reconexão automática.
        """
        # Cria contexto SSL para conexão segura (obrigatório para HiveMQ Cloud)
        tls_context = ssl.create_default_context()
        
        logger.info("[MQTT] Attempting to connect to HiveMQ Broker...")

        while True:
            try:
                # Conecta com timeout para evitar travamentos
                async with aiomqtt.Client(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    tls_context=tls_context,
                    timeout=10
                ) as client:
                    
                    # Se chegou aqui, conectou com sucesso
                    self.ping()

                    await client.subscribe("/logging")
                    
                    # Loop de processamento de mensagens
                    async for data in client.messages:
                        # Removido print(data.payload) para evitar spam no terminal
                        payload = data.payload
                        self._latest_payload = payload
                        self._new_payload_event.set()
            
            except aiomqtt.MqttError as e:
                # Captura erros específicos do MQTT (ex: autenticação, conexão perdida)
                logger.error(f"[MQTT] Connection Error: {e}")
                await asyncio.sleep(5) # Espera 5s antes de tentar reconectar
            
            except asyncio.CancelledError:
                # Encerra o loop se a task for cancelada
                break
                
            except Exception as e:
                # Captura erros genéricos
                logger.error(f"[MQTT] Unexpected Error: {e}")
                await asyncio.sleep(5)

    async def get_payload(self) -> bytes:
        """
        Retorna o payload mais recente recebido via MQTT.
        Se nenhum payload foi recebido ainda, espera pelo primeiro.
        """
        if self._latest_payload is None:
            await self._new_payload_event.wait()
        return self._latest_payload

    async def stop(self):
        """
        Cancela a tarefa de telemetria.
        """
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
