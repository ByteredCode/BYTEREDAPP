import logging
from typing import Optional

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


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

    # Redis (blocklist persistente)
    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    SMTP_HOST: str = ""
    SMTP_PORT: Optional[int] = None
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    TICKETS_EMAIL: str = "admin@byteredapp.com"

    @property
    def redis_configurado(self) -> bool:
        return bool(self.REDIS_HOST)

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    @property
    def smtp_configurado(self) -> bool:
        return bool(self.SMTP_HOST and self.SMTP_PORT)

    def model_post_init(self, __context) -> None:
        if self.JWT_SECRET == "changeme":
            logger.warning(
                "JWT_SECRET usa el valor por defecto 'changeme'. "
                "Genera uno seguro con: python scripts/generate_secret.py"
            )
        if not self.smtp_configurado:
            logger.warning(
                "SMTP no configurado: los correos de tickets no se enviaran. "
                "Configura SMTP_HOST y SMTP_PORT en .env"
            )
        origenes = [o.strip() for o in self.CORS_ORIGINS.split(",")]
        if any("localhost" in o or "127.0.0.1" in o for o in origenes):
            logger.info(
                "CORS incluye localhost — adecuado para desarrollo. "
                "En produccion usa solo dominios reales."
            )

    model_config = {"env_file": "../.env", "case_sensitive": True, "extra": "ignore"}


# Instancia unica (singleton) importada en toda la aplicacion
config = Config()
