# server/services/database.py
import sqlite3
import os
from typing import Dict, Any

class DatabaseService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.session_id = None
        self._lock = sqlite3.connect(self.db_path, check_same_thread=False)

    def connect(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.cursor = self.conn.cursor()
        print("[Database] Conectado ao banco de dados.")

    def close(self):
        if self.conn:
            self.conn.close()
            print("[Database] Conexão fechada.")

    def create_schema(self):
        self.cursor.executescript("""
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
        """)
        self.conn.commit()
        print("[Database] Esquema verificado/criado.")

    def start_new_session(self, label: str = "Default Session"):
        self.cursor.execute("INSERT INTO sessions (label) VALUES (?);", (label,))
        self.conn.commit()
        self.session_id = self.cursor.lastrowid
        print(f"[Database] Nova sessão iniciada com ID: {self.session_id}")

    def save_telemetry_data(self, packet: Dict[str, Any]):
        """
        Saves a telemetry packet to the database.
        If no session is active, it starts one automatically.
        """
        if not self.conn:
            raise RuntimeError("Database connection not established.")

        if self.session_id is None:
            print("[Database] Warning: No active session. Starting a new 'auto' session.")
            self.start_new_session(label="Auto-Session")
            if self.session_id is None:
                print("[Database] Error: Failed to start a new session. Cannot save data.")
                return

        self.cursor.execute("""
            INSERT INTO telemetry (
                session_id, acc_x, acc_y, acc_z, dps_x, dps_y, dps_z,
                roll, pitch, rpm, speed, temperature, soc, temp_cvt,
                volt, current, flags, latitude, longitude, timestamp
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            self.session_id,
            packet.get("acc_x"), packet.get("acc_y"), packet.get("acc_z"),
            packet.get("dps_x"), packet.get("dps_y"), packet.get("dps_z"),
            packet.get("roll"), packet.get("pitch"),
            packet.get("rpm"), packet.get("speed"),
            packet.get("temperature"), packet.get("soc"), packet.get("temp_cvt"),
            packet.get("volt"), packet.get("current"),
            packet.get("flags"), packet.get("latitude"), packet.get("longitude"),
            packet.get("timestamp"),
        ))
        self.conn.commit()
