from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
<<<<<<< HEAD
    # Choose the data source: 'serial', 'mqtt', or 'simulator' data_source: Literal["serial", "mqtt", "simulator"] = "mqtt"
    data_source: Literal["serial", "mqtt", "simulator"] = "simulator"
=======
    # Server serttings
    data_source: Literal["serial", "mqtt", "simulator"] = "simulator"
    broadcast_delay_seconds: float = 0.01
>>>>>>> d723a362756af9dadec4073b8ed0d8b5da1f5067

    # MQTT Broker Settings
    mqtt_hostname: str = ""
    mqtt_port: int = 0
    mqtt_username: str = ""
    mqtt_password: str = ""

    # LoRa Serial Receiver Settings
    serial_port: str = "/dev/pts/2" # Change to your actual port
    serial_baudrate: int = 115200
    serial_packet_format: str = "<fBBfBHhhhhhh hhH BddI" # Always check

    # Database Settings
    database_path: str = "./data/database/database.db"

<<<<<<< HEAD
# Exports the settings
=======
# Single customized settings entity
>>>>>>> d723a362756af9dadec4073b8ed0d8b5da1f5067
settings = Settings()
