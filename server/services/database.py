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
        # ... (schema creation code is the same as before) ...
        print("[Database] Esquema verificado/criado.")

    def start_new_session(self, label: str = "Default Session"):
        # ... (session creation code is the same) ...
        self.session_id = self.cursor.lastrowid
        print(f"[Database] Nova sessão iniciada com ID: {self.session_id}")
    
    def save_telemetry_data(self, packet: Dict[str, Any]):
        # ... (The INSERT INTO telemetry logic is the same) ...
        pass
