"""
    Arquivo contendo os simuladores e rotinas criados em python.
"""

from datetime import datetime, timedelta
import math
import random


class Simuladores:
    """
        Classe que contêm os simuladores.
    """

    def __init__(self):
        self.inicio = datetime.now()
        self.vel_anterior = 0
        self.timestamp_atual = datetime.now()
        self.base_lat = -8.05428
        self.base_lon = -34.8813
        self.id_sessao_atual = None

    async def gerar_dados(self) -> dict:
        """
            Com foco principal de testar a interface de telemetria,
            esta função gera dados semi-aleatórios e exporta como um
            dado válido para a telemetria.
        """
        tempo_s = (datetime.now() - self.inicio).total_seconds()
        self.timestamp_atual += timedelta(milliseconds=500)

        vel = max(0, min(60, 30 + 15 * math.sin(tempo_s / 10)))
        rpm = vel * 120 + random.uniform(-200, 200)
        accx = (vel - self.vel_anterior) / 0.5

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
            "vel": round(vel, 2),
            "temp_motor": round(min(110, 60 + tempo_s * 0.3), 1),
            "soc": round(max(0, 100 - tempo_s * 0.03), 1),
            "temp_cvt": round(min(95, 50 + tempo_s * 0.25), 1),
            "volt": round(13.0 - tempo_s * 0.001, 2),
            "current": round(random.uniform(150, 300), 1),
            "flags": 0,
            "latitude": round(self.base_lat + tempo_s * 0.00002, 6),
            "longitude": round(
                self.base_lon + math.sin(tempo_s / 20) * 0.0001, 6),
            "timestamp": self.timestamp_atual.isoformat(),
        }

        self.vel_anterior = vel
        return dados
