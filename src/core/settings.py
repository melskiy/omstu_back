from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str
    port: int
    login: str
    password: str
    base_host: str
    base_port: int
    base_name: str


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
