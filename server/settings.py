from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Server serttings
    simular_interface: bool = False
    broadcast_delay_seconds: float = 0.01

    # MQTT Broker settings
    mqtt_hostname: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str

    # LoRa serial receiver settings
    serial_port: str = "/dev/pts/2"
    serial_baudrate: int = 115200
    serial_packet_format: str = "<fBBfBH hhhhhh hh H BddI"

    # Database settings
    database_path: str = "./data/database/database.db"

    # This tells Pydantic to load from a .env file
    model_config = SettingsConfigDict(env_file="credentials.env", env_file_encoding='utf-8')

# Single customized settings entity
settings = Settings()
