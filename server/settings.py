from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    # Server serttings
    # Choose the data source: 'serial', 'mqtt', or 'simulator' data_source: Literal["serial", "mqtt", "simulator"] = "simulator"
    data_source: Literal["serial", "mqtt", "simulator"] = "simulator"
    broadcast_delay_seconds: float = 0.1

    # MQTT Broker Settings
    mqtt_hostname: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""

    # LoRa Serial Receiver Settings
    serial_port: str = "/dev/pts/3" # Change to your actual port
    serial_baudrate: int = 115200
    serial_packet_format: str = "<fBBfBHhhhhhh hhH BddI" # Always check

    # Database Settings
    database_path: str = "./data/database/database.db"

# Exports the settings
# Single customized settings entity
settings = Settings()
