"""
Arquivo contendo o simulador de telemetria em Python.
"""

import asyncio
from datetime import datetime, timedelta
import math
import random
from typing import Dict, Any

class Simulador:
    """
    Classe que simula dados de telemetria para testes da interface.

    Esta classe gera dados de telemetria semi-aleatórios em uma
    tarefa de fundo e os disponibiliza através de uma fila assíncrona,
    imitando o comportamento de um serviço de telemetria real.
    """

    def __init__(self, update_rate_hz: int = 20):
        """
        Inicializa o simulador.

        Args:
            update_rate_hz (int): A frequência de atualização de
                                  dados em Hertz.
        """
        self.inicio = datetime.now()
        self.vel_anterior = 0.0
        self.timestamp_atual = datetime.now()
        self.base_lat = -8.05428
        self.base_lon = -34.8813
        self.update_interval_seconds = 1.0 / update_rate_hz
        self.queue = asyncio.Queue(maxsize=1)
        self._task = None

    async def start(self):
        """Inicia a tarefa de geração de dados em segundo plano."""
        if not self._task:
            self._task = asyncio.create_task(self._run_simulation_loop())

    async def stop(self):
        """Para a tarefa de geração de dados."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def get_payload(self) -> Dict[str, Any]:
        """
        Retorna o último pacote de dados de telemetria gerado.
        Aguarda se nenhum dado novo estiver disponível.
        """
        return await self.queue.get()

    async def _run_simulation_loop(self):
        """
        Loop principal que gera continuamente novos dados de telemetria
        e os coloca na fila.
        """
        while True:
            try:
                dados = self._gerar_pacote_de_dados()
                if self.queue.full():
                    await self.queue.get()  # Descarta o dado mais antigo
                await self.queue.put(dados)
                await asyncio.sleep(self.update_interval_seconds)
            except asyncio.CancelledError:
                break

    def _gerar_pacote_de_dados(self) -> Dict[str, Any]:
        """
        Gera um único pacote de dados de telemetria semi-aleatórios.

        Returns:
            Um dicionário contendo os dados de telemetria simulados.
        """
        tempo_s = (datetime.now() - self.inicio).total_seconds()
        self.timestamp_atual += timedelta(
            seconds=self.update_interval_seconds
        )

        # Simulação de dados com base em funções senoidais e aleatoriedade
        vel = max(0, min(60, 30 + 15 * math.sin(tempo_s / 10)))
        rpm = vel * 120 + random.uniform(-200, 200)
        accx = (vel - self.vel_anterior) / self.update_interval_seconds

        dados = {
            "accx": round(accx, 2),
            "accy": round(random.uniform(-0.2, 0.2), 2),
            "accz": round(random.uniform(9.4, 9.8), 2),
            "dpsx": round(random.uniform(-1, 1), 2),
            "dpsy": round(random.uniform(-1, 1), 2),
            "dpsz": round(random.uniform(-1, 1), 2),
            "roll": round(random.uniform(-5, 5), 2),
            "pitch": round(random.uniform(-5, 5), 2),
            "rpm": round(rpm, 2),
            "speed": round(vel, 2),
            "temperature": round(min(110, 60 + tempo_s * 0.3), 1),
            "soc": round(max(0, 100 - tempo_s * 0.03), 1),
            "temp_cvt": round(min(95, 50 + tempo_s * 0.25), 1),
            "volt": round(13.0 - tempo_s * 0.001, 2),
            "current": round(random.uniform(150, 300), 1),
            "flags": 0,
            "latitude": round(self.base_lat + tempo_s * 0.00002, 6),
            "longitude": round(
                self.base_lon + math.sin(tempo_s / 20) * 0.0001, 6
            ),
            "timestamp": self.timestamp_atual.isoformat(),
        }

        self.vel_anterior = vel
        return dados

    async def gerar_dados(self) -> Dict[str, Any]:
        """
        Gera um único pacote de dados.
        Recomendado usar `get_payload` com `start` e `stop`.
        """
        return self._gerar_pacote_de_dados()
