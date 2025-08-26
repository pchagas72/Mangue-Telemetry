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
        self.payload_fmt = "<fbbfbhhhhhhhhhhbddi" # Formato do pacote da CAN.
        self.sessao_atual_id = None
        self.database_con = None
        self.database_cur = None

    def connect_to_db(self):
        """
            Cria o cursor e a conexão ao arquivo da database.
            A conexão é auto-explicativa, ela conecta o servidor ao .db
            O cursor executa ações servidor->database.
        """
        os.makedirs("./data/database/", exist_ok=True)
        self.database_con = sqlite3.connect("./data/database/database.db")
        self.database_con.execute("PRAGMA journal_mode=WAL;")
        self.database_con.execute("PRAGMA synchronous=NORMAL;")
        self.database_cur = self.database_con.cursor()

    def create_schema(self):
        """
            Garante que o esquema da database seja criado.
            O esquema contém a chave para a organização dos dados.
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
                accx REAL, accy REAL, accz REAL,
                dpsx REAL, dpsy REAL, dpsz REAL,
                roll REAL, pitch REAL,
                rpm REAL, vel REAL,
                temp_motor REAL, soc REAL, temp_cvt REAL,
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
            Isso é essencial para a organização dos dados.
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
            # fallback simples: cria uma sessão automática
            self.start_new_session(label="auto")

        self.database_cur.execute("""
            INSERT INTO telemetry (
                session_id, accx, accy, accz, dpsx, dpsy, dpsz,
                roll, pitch, rpm, vel, temp_motor, soc, temp_cvt,
                volt, current, flags, latitude, longitude, timestamp
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            self.sessao_atual_id,
            packet["accx"], packet["accy"], packet["accz"],
            packet["dpsx"], packet["dpsy"], packet["dpsz"],
            packet["roll"], packet["pitch"],
            packet["rpm"], packet["vel"],
            packet["temp_motor"], packet["soc"], packet["temp_cvt"],
            packet["volt"], packet["current"],
            packet["flags"], packet["latitude"], packet["longitude"],
            packet["timestamp"],
        ))
        self.database_con.commit()

    def parse_mqtt_packet(self, payload: bytes) -> dict:
        """
            Função que recebe o payload da telemetria e monta a struct que o
            carro envia, qualquer alteração no pacote da CAN deve ser
            documentada e registrada aqui.
        """
        if len(payload) != struct.calcsize(self.payload_fmt):
            raise ValueError(
                f"[DATA] Tamanho do payload inesperado: {len(payload)}\n"
                f"Esperado: {struct.calcsize(self.payload_fmt)}\n"
             )
        (
            volt, soc, cvt, current, temperature, speed,
            acc_x, acc_y, acc_z,
            dps_x, dps_y, dps_z,
            roll, pitch,
            rpm, flags,
            latitude, longitude,
            timestamp
        ) = struct.unpack(self.payload_fmt, payload)

        return {
            "accx": acc_x,
            "accy": acc_y,
            "accz": acc_z,
            "dpsx": dps_x,
            "dpsy": dps_y,
            "dpsz": dps_z,
            "roll": roll,
            "pitch": pitch,
            "rpm": rpm,
            "vel": speed,
            "temp_motor": temperature,
            "soc": soc,
            "temp_cvt": cvt,
            "volt": volt,
            "current": current,
            "flags": flags,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,
        }

    def close_db(self):
        """
            Finaliza todos os processos da database.
        """
        if self.database_cur:
            self.database_cur.close()
        if self.database_con:
            self.database_con.close()
