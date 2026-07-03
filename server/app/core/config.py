import logging
from typing import Optional

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


# Pydantic BaseSettings lee automaticamente variables de entorno y .env
# Ofrece tipado estricto y validacion en lugar de os.getenv() manual
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

    # Email via Resend API (HTTPS, nunca bloqueado desde cloud)
    RESEND_API_KEY: str = ""
    RESEND_FROM: str = "BYTERED <sat@bytered.es>"
    TICKETS_EMAIL: str = "sat@bytered.es"

    # @property evita almacenar valores derivados: se calculan cada vez que se accede
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
    def resend_configurado(self) -> bool:
        return bool(self.RESEND_API_KEY)

    # Hook de Pydantic v2 que se ejecuta tras crear la instancia
    # Sirve para validaciones que dependen del valor final de los campos
    def model_post_init(self, __context) -> None:
        if self.JWT_SECRET in {"changeme", "super-secret-key-change-in-production"}:
            logger.warning(
                "JWT_SECRET usa un valor por defecto. "
                "Genera uno seguro con: python scripts/generate_secret.py"
            )
        if not self.resend_configurado:
            logger.warning(
                "RESEND_API_KEY no configurada: los correos de tickets no se enviaran. "
                "Configura RESEND_API_KEY en .env"
            )
        origenes = [o.strip() for o in self.CORS_ORIGINS.split(",")]
        if any("localhost" in o or "127.0.0.1" in o for o in origenes):
            logger.info(
                "CORS incluye localhost — adecuado para desarrollo. "
                "En produccion usa solo dominios reales."
            )

    model_config = {"env_file": "../.env", "case_sensitive": True, "extra": "ignore"}


# Singleton: se instancia una sola vez al importar el modulo
# Carga el .env una unica vez y todas las capas usan la misma instancia
config = Config()
