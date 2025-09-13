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

    # Database settings
    database_path: str = "./data/database/database.db"

    # This tells Pydantic to load from a .env file
    model_config = SettingsConfigDict(env_file="credentials.env", env_file_encoding='utf-8')

# Single customized settings entity
settings = Settings()
