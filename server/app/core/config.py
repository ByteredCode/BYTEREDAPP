from typing import Optional

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "byteredapp"

    # Seguridad JWT
    JWT_SECRET: str = "changeme"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    SMTP_HOST: str = ""
    SMTP_PORT: Optional[int] = None
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    TICKETS_EMAIL: str = "admin@byteredapp.com"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    model_config = {"env_file": "../.env", "case_sensitive": True, "extra": "ignore"}


# Instancia unica (singleton) importada en toda la aplicacion
config = Config()
