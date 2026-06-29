import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import limiter, router as auth_router
from app.api.v1.empresa import router as empresa_router
from app.api.v1.scrum import router as scrum_router
from app.api.v1.tickets import router as tickets_router
from app.api.v1.documentos import router as documentos_router
from app.api.v1.fichajes import router as fichajes_router
from app.api.v1.redireccion import router as redireccion_router
from app.core.blocklist import cerrar as cerrar_blocklist
from app.core.config import config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando BYTEREDAPP API — entorno: {'produccion' if config.JWT_SECRET != 'changeme' else 'desarrollo'}")
    logger.info(f"Documentacion {'habilitada' if config.docs_url else 'deshabilitada'} (CORS: {config.CORS_ORIGINS})")
    yield
    await cerrar_blocklist()


cors_origins = [o.strip() for o in config.CORS_ORIGINS.split(",")]

app = FastAPI(
    title="BYTEREDAPP API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if cors_origins == ["http://localhost:5173"] else None,
    redoc_url="/redoc" if cors_origins == ["http://localhost:5173"] else None,
)

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def seguridad_headers_middleware(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=seguridad_headers_middleware)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(empresa_router)
app.include_router(scrum_router)
app.include_router(tickets_router)
app.include_router(documentos_router)
app.include_router(fichajes_router)
app.include_router(redireccion_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
