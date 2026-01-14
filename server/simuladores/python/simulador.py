"""
Arquivo contendo o simulador de telemetria em Python.
A lógica de simulação foi atualizada para espelhar o simulador C++,
mantendo a saída no formato de dicionário para compatibilidade com a API.
"""

import asyncio
import math
import time
from typing import Dict, Any

class Simulador:
    """
    Classe que simula dados de telemetria para testes da interface.

    Esta classe gera dados de telemetria usando a mesma lógica do emulador C++,
    mas os disponibiliza como um dicionário Python, compatível com a aplicação FastAPI.
    """

    def __init__(self, update_rate_hz: int = 20):
        """
        Inicializa o simulador.

        Args:
            update_rate_hz (int): A frequência de atualização de
                                  dados em Hertz.
        """
        # O contador é usado para a lógica de simulação, assim como no C++
        self.counter = 0
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
        Retorna o último pacote de dados de telemetria gerado pela tarefa de fundo.
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
        Gera um único pacote de dados de telemetria usando a lógica do C++.
        
        A função gera valores flutuantes que correspondem aos valores decodificados
        que o parser geraria a partir do pacote binário do C++.

        Returns:
            Um dicionário contendo os dados de telemetria simulados.
        """
        c = self.counter 

        # --- Lógica portada do C++ (populate_packet) ---
        
        # Acelerômetro
        # C++: int16 scaled (x100). Python: float real.
        acc_x = round(math.sin(c * 0.5), 2)
        acc_y = round(math.cos(c * 0.5), 2)
        acc_z = round(9.8 + math.sin(c * 0.2) * 0.1, 2)
        
        # Giroscópio / DPS
        # C++: int16 scaled. Ex: 50, 50, 5. Assumindo escala x10 -> 5.0, 5.0, 0.5
        dps_x = round(math.cos(c * 0.4) * 5, 2)
        dps_y = round(math.sin(c * 0.4) * 5, 2)
        dps_z = round(math.cos(c * 0.1) * 0.5, 2)

        # Ângulos (Roll/Pitch)
        # C++: 20, 10. Assumindo escala x10 -> 2.0, 1.0 graus
        roll = round(math.sin(c * 0.1) * 2, 2)
        pitch = round(math.cos(c * 0.1) * 1, 2)

        # Dados do Veículo
        speed = (c * 2) % 60
        rpm = 3000 + int(math.sin(c * 0.8) * 500)
        
        volt = round(12.5 + math.sin(c * 0.1) * 0.5, 2)
        soc = 98 - (c % 20)
        temp_cvt = 80 + int(math.sin(c * 0.2) * 5)
        current = round(15.3 + math.cos(c * 0.1) * 2.0, 2)
        temperature = 75 + int(math.cos(c * 0.3) * 3)
        
        # GPS
        latitude = -8.05428 + math.sin(c * 0.01) * 0.001
        longitude = -34.8813 + math.cos(c * 0.01) * 0.001

        # Timestamp em milissegundos (igual ao C++ system_clock)
        timestamp = int(time.time() * 1000)

        dados = {
            "acc_x": acc_x,
            "acc_y": acc_y,
            "acc_z": acc_z,
            "dps_x": dps_x,
            "dps_y": dps_y,
            "dps_z": dps_z,
            "roll": roll,
            "pitch": pitch,
            "rpm": rpm,
            "speed": speed,
            "temperature": temperature,
            "soc": soc,
            "temp_cvt": temp_cvt,
            "volt": volt,
            "current": current,
            "flags": c % 2,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,
        }

        self.counter += 1
        return dados

    async def gerar_dados(self) -> Dict[str, Any]:
        """
        Gera e retorna um único pacote de dados.
        Chamado pelo main.py quando settings.data_source == "simulator".
        """
        return self._gerar_pacote_de_dados()

# --- Bloco de Teste ---
async def main():
    """Função para testar e visualizar a saída do simulador."""
    sim = Simulador()
    dados_simulados = await sim.gerar_dados()
    
    import json
    print("Saída do simulador no formato JSON (dicionário):")
    print(json.dumps(dados_simulados, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
