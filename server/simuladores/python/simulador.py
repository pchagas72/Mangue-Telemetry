"""
Arquivo contendo o simulador de telemetria em Python.
A lógica de simulação foi atualizada para espelhar o simulador C++,
mantendo a saída no formato de dicionário para compatibilidade com a API.
"""

import asyncio
from datetime import datetime
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

        Returns:
            Um dicionário contendo os dados de telemetria simulados.
        """
        c = self.counter  # Usando 'c' para ser mais parecido com o C++

        # --- Lógica de geração de dados portada do `populate_packet` em C++ ---
        # Os valores são arredondados para manter o formato do simulador original
        
        # O C++ armazena valores como inteiros escalados (ex: acc_x como int16_t).
        # Aqui, vamos manter como floats, mas usando a mesma função base.
        # Ex: int16_t(sin(c * 0.5) * 100) -> round(sin(c * 0.5), 2)
        accx = round(math.sin(c * 0.5), 2)
        accy = round(math.cos(c * 0.5), 2)
        # 980 em C++ é 9.8 m/s^2. Dividimos por 100 para normalizar.
        accz = round(9.8 + math.sin(c * 0.2) * 0.1, 2)
        
        # DPS (Degrees Per Second)
        dpsx = round(math.cos(c * 0.4) * 5, 2) # Reduzido para valores mais sutis
        dpsy = round(math.sin(c * 0.4) * 5, 2)
        dpsz = round(math.cos(c * 0.1), 2)

        dados = {
            "accx": accx,
            "accy": accy,
            "accz": accz,
            "dpsx": dpsx,
            "dpsy": dpsy,
            "dpsz": dpsz,
            "roll": round(math.sin(c * 0.1) * 20, 2),
            "pitch": round(math.cos(c * 0.1) * 10, 2),
            "rpm": round(3000 + math.sin(c * 0.8) * 500, 2),
            "speed": round((c * 2) % 60, 2),
            "temperature": round(75 + math.cos(c * 0.3) * 3, 1),
            "soc": round(98 - (c % 20), 1),
            "temp_cvt": round(80 + math.sin(c * 0.2) * 5, 1), # Mapeado de 'cvt'
            "volt": round(12.5 + math.sin(c * 0.1) * 0.5, 2),
            "current": round(15.3 + math.cos(c * 0.1) * 2.0, 1),
            "flags": c % 2,
            "latitude": round(-8.05428 + math.sin(c * 0.01) * 0.001, 6),
            "longitude": round(-34.8813 + math.cos(c * 0.01) * 0.001, 6),
            "timestamp": datetime.now().isoformat(),
        }

        self.counter += 1
        return dados

    async def gerar_dados(self) -> Dict[str, Any]:
        """
        Gera e retorna um único pacote de dados.
        Este é o método chamado pelo `main.py`. Ele precisa ser `async`.
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
