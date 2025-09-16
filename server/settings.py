from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    # Server serttings
    data_source: Literal["serial", "mqtt", "simulator"] = "simulator"
    broadcast_delay_seconds: float = 0.01

    # MQTT Broker Settings
    mqtt_hostname: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""

    # LoRa serial receiver settings
    serial_port: str = "/dev/pts/2"
    serial_baudrate: int = 115200
    serial_packet_format: str = "<fBBfBH hhhhhh hh H BddI"

    # Database settings
    database_path: str = "./data/database/database.db"

# Single customized settings entity
settings = Settings()
