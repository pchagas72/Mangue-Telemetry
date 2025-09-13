"""
    Módulo que lida com os dados recebidos da telemetria.
    Este arquivo guarda os dados na database e processa o que for
    necessário
"""

import struct
import os
import sqlite3

class MangueData:
    """
        Classe responsável por processar e guardar dados.
        Note a importância da variável "payload_fmt"
    """

    def __init__(self):
        self.payload_fmt = "<fBBfBH hhh hhh hh H B ddI"
        self.sessao_atual_id = None
        self.database_con = None
        self.database_cur = None

    def connect_to_db(self):
        """
            Cria o cursor e a conexão ao arquivo da database.
        """
        os.makedirs("./data/database/", exist_ok=True)
        self.database_con = sqlite3.connect("./data/database/database.db")
        self.database_con.execute("PRAGMA journal_mode=WAL;")
        self.database_con.execute("PRAGMA synchronous=NORMAL;")
        self.database_cur = self.database_con.cursor()

    def create_schema(self):
        """
            Garante que o esquema da database seja criado.
        """
        if self.database_cur is None:
            raise RuntimeError(
                "DB não conectada. Chame connect_to_db() primeiro."
            )

        self.database_cur.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
                label TEXT
            );

            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                acc_x REAL, acc_y REAL, acc_z REAL,
                dps_x REAL, dps_y REAL, dps_z REAL,
                roll REAL, pitch REAL,
                rpm REAL, speed REAL,
                temperature REAL, soc REAL, temp_cvt REAL,
                volt REAL, current REAL,
                flags INTEGER,
                latitude REAL, longitude REAL,
                timestamp INTEGER,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            );

            CREATE INDEX IF NOT EXISTS idx_telemetry_session_ts
            ON telemetry(session_id, timestamp);
        """)
        self.database_con.commit()

    def start_new_session(self, label: str | None = None):
        """
            Cada vez que o servidor funcionar, ele cria uma sessão.
        """
        self.database_cur.execute(
            "INSERT INTO sessions (label) VALUES (?);",
            (label,)
        )
        self.database_con.commit()
        self.sessao_atual_id = self.database_cur.lastrowid

    def save_in_db(self, packet: dict):
        """
            Função que escreve os dados da telemetria (packet) na database.
        """
        if self.database_con is None:
            raise RuntimeError(
                "DB não conectada. Chame connect_to_db() primeiro."
            )
        if self.sessao_atual_id is None:
            self.start_new_session(label="auto")

        self.database_cur.execute("""
            INSERT INTO telemetry (
                session_id, acc_x, acc_y, acc_z, dps_x, dps_y, dps_z,
                roll, pitch, rpm, speed, temperature, soc, temp_cvt,
                volt, current, flags, latitude, longitude, timestamp
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            self.sessao_atual_id,
            packet["acc_x"], packet["acc_y"], packet["acc_z"],
            packet["dps_x"], packet["dps_y"], packet["dps_z"],
            packet["roll"], packet["pitch"],
            packet["rpm"], packet["speed"],
            packet["temperature"], packet["soc"], packet["temp_cvt"],
            packet["volt"], packet["current"],
            packet["flags"], packet["latitude"], packet["longitude"],
            packet["timestamp"],
        ))
        self.database_con.commit()

    def parse_mqtt_packet(self, payload: bytes) -> dict:
        """
            Função que recebe o payload da telemetria, desempacota os dados
            brutos e os converte para unidades físicas legíveis.
        """
        expected_size = struct.calcsize(self.payload_fmt)
        if len(payload) != expected_size:
            raise ValueError(
                f"[DATA] Tamanho do payload inesperado: {len(payload)}. "
                f"Esperado: {expected_size}"
             )
        
        raw = struct.unpack(self.payload_fmt, payload)

        # Mapeia e converte os dados brutos para um dicionário com unidades físicas
        # As fórmulas de conversão devem corresponder às do firmware ou do datasheet do sensor.
        processed_data = {
            "volt": raw[0],
            "soc": raw[1],
            "temp_cvt": raw[2],
            "current": raw[3],
            "temperature": raw[4],
            "speed": raw[5],
            
            # Conversão do Acelerômetro (G-force)
            "acc_x": (raw[6] * 0.061) / 1000.0,
            "acc_y": (raw[7] * 0.061) / 1000.0,
            "acc_z": (raw[8] * 0.061) / 1000.0,

            # Conversão do Giroscópio (graus por segundo)
            # NOTA: O fator 70.0 é um valor comum para giroscópios (mdps/LSB).
            # Mas sempre é válido verificar no datasheet
            "dps_x": (raw[9] * 70.0) / 1000.0,
            "dps_y": (raw[10] * 70.0) / 1000.0,
            "dps_z": (raw[11] * 70.0) / 1000.0,

            "roll": raw[12],
            "pitch": raw[13],
            "rpm": raw[14],
            "flags": raw[15],
            "latitude": raw[16],
            "longitude": raw[17],
            "timestamp": raw[18],
        }

        return processed_data

    def close_db(self):
        """
            Finaliza todos os processos da database.
        """
        if self.database_cur:
            self.database_cur.close()
        if self.database_con:
            self.database_con.close()
