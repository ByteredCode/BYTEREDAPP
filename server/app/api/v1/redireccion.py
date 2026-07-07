import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.empresa import Empresa

router = APIRouter(tags=["Redireccion"])


def _es_url_segura(url: str) -> bool:
    """Valida que la URL no apunte a IPs internas/privadas (SSRF)."""
    parsed = urlparse(url)
    if not parsed.hostname:
        return False
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
    except ValueError:
        # No es una IP, es un dominio — aceptar
        return True


@router.get("/r/{codigo_empresa}")
async def redirigir(codigo_empresa: int, db: AsyncSession = Depends(get_db)):
    # Endpoint público (sin autenticación) porque se usa desde códigos QR,
    # emails o enlaces externos que ningún usuario ha iniciado sesión
    resultado = await db.execute(select(Empresa).where(Empresa.codigo_empresa == codigo_empresa))
    empresa = resultado.scalar_one_or_none()
    if not empresa or not empresa.web:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa o enlace no configurado")
    # Validamos el esquema de la URL para evitar open redirect que permita
    # redirigir a protocolos peligrosos como file://, javascript: o data:
    parsed = urlparse(empresa.web)
    if parsed.scheme not in ("https", "http"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL no valida")
    # Protección SSRF: verificar que la IP no sea interna/privada
    if not _es_url_segura(empresa.web):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL no permitida")
    return RedirectResponse(url=empresa.web)
