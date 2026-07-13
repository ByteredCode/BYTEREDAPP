# Tests de integración para el módulo de redirección (/r/<codigo_empresa>)
from app.models.empresa import Empresa
from app.models.empresa_servicio import EmpresaServicio


async def test_redireccion_exito(client, test_session):
    # Una empresa con web configurada y servicio activo debe redirigir (307) a esa URL
    empresa = Empresa(nombre="Test", web="https://example.com")
    test_session.add(empresa)
    await test_session.flush()
    test_session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio="redireccion", activo=True))
    await test_session.flush()

    resp = await client.get(f"/r/{empresa.codigo_empresa}")

    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com"


async def test_redireccion_empresa_sin_web(client, test_session):
    # Una empresa sin web configurada debe devolver 404 (no hay URL a la que redirigir)
    empresa = Empresa(nombre="Test Sin Web")
    test_session.add(empresa)
    await test_session.flush()
    test_session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio="redireccion", activo=True))
    await test_session.flush()

    resp = await client.get(f"/r/{empresa.codigo_empresa}")

    assert resp.status_code == 404


async def test_redireccion_empresa_inexistente(client):
    # Un código de empresa que no existe debe devolver 404
    resp = await client.get("/r/99999")

    assert resp.status_code == 404


async def test_redireccion_url_no_https(client, test_session):
    # Solo se permiten URLs HTTPS (seguridad); protocolos no seguros deben ser rechazados
    empresa = Empresa(nombre="Test Malicious", web="ftp://malicious.com")
    test_session.add(empresa)
    await test_session.flush()
    test_session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio="redireccion", activo=True))
    await test_session.flush()

    resp = await client.get(f"/r/{empresa.codigo_empresa}")

    assert resp.status_code == 400


async def test_redireccion_servicio_desactivado(client, test_session):
    # Si el servicio redireccion está desactivado, debe devolver 404
    empresa = Empresa(nombre="Test NoRedirect", web="https://example.com")
    test_session.add(empresa)
    await test_session.flush()
    test_session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio="redireccion", activo=False))
    await test_session.flush()

    resp = await client.get(f"/r/{empresa.codigo_empresa}")

    assert resp.status_code == 404


async def test_redireccion_url_ip_privada_127(client, test_session):
    # URL con IP de loopback (127.0.0.1) debe ser bloqueada por SSRF
    empresa = Empresa(nombre="Test Loopback", web="http://127.0.0.1/admin")
    test_session.add(empresa)
    await test_session.flush()
    test_session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio="redireccion", activo=True))
    await test_session.flush()

    resp = await client.get(f"/r/{empresa.codigo_empresa}")

    assert resp.status_code == 400
    assert "no permitida" in resp.json()["detail"].lower()


async def test_redireccion_url_ip_privada_192(client, test_session):
    # URL con IP privada (192.168.1.1) debe ser bloqueada por SSRF
    empresa = Empresa(nombre="Test Privada", web="http://192.168.1.1/secreto")
    test_session.add(empresa)
    await test_session.flush()
    test_session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio="redireccion", activo=True))
    await test_session.flush()

    resp = await client.get(f"/r/{empresa.codigo_empresa}")

    assert resp.status_code == 400
    assert "no permitida" in resp.json()["detail"].lower()


async def test_redireccion_url_javascript_scheme(client, test_session):
    # URL con scheme javascript: debe ser rechazada (open redirect XSS)
    empresa = Empresa(nombre="Test XSS", web="javascript:alert(1)")
    test_session.add(empresa)
    await test_session.flush()
    test_session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio="redireccion", activo=True))
    await test_session.flush()

    resp = await client.get(f"/r/{empresa.codigo_empresa}")

    assert resp.status_code == 400
    assert "no valida" in resp.json()["detail"].lower()
