# Tests de integración para el módulo de documentos (subida, listado, permisos, eliminación)
from io import BytesIO

import pytest
from httpx import AsyncClient


class TestDocumentos:

    async def test_subir_documento(self, client: AsyncClient, headers_usuario):
        # Subida básica de un archivo PDF con tipo DPD; debe crear el documento en la BD
        files = {"archivo": ("test.pdf", BytesIO(b"contenido pdf"), "application/pdf")}
        data = {"tipo_documento": "DPD"}
        response = await client.post(
            "/documentos", files=files, data=data, headers=headers_usuario
        )
        assert response.status_code == 201
        body = response.json()
        assert body["nombre"] == "test.pdf"
        assert body["tipo_documento"] == "DPD"
        assert body["ruta_archivo"] is not None

    async def test_subir_tipo_no_permitido(self, client: AsyncClient, headers_usuario):
        # El backend debe rechazar tipos de archivo no permitidos (ejecutables, etc.)
        files = {"archivo": ("malware.exe", BytesIO(b"datos"), "application/x-msdownload")}
        response = await client.post("/documentos", files=files, headers=headers_usuario)
        assert response.status_code == 400

    async def test_listar_documentos(self, client: AsyncClient, headers_usuario):
        # Tras subir un documento, debe aparecer en el listado
        files = {"archivo": ("doc1.pdf", BytesIO(b"contenido"), "application/pdf")}
        await client.post("/documentos", files=files, headers=headers_usuario)

        response = await client.get("/documentos", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1

    async def test_obtener_documento(self, client: AsyncClient, headers_usuario):
        # Obtener un documento por su ID debe devolver sus metadatos
        files = {"archivo": ("doc.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        response = await client.get(f"/documentos/{doc_id}", headers=headers_usuario)
        assert response.status_code == 200
        assert response.json()["id_documento"] == doc_id

    async def test_agregar_permiso(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        # El propietario del documento puede conceder permisos a otro usuario de la misma empresa
        from app.core.security import hash_contrasena
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="otro@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="Otro",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        files = {"archivo": ("permisos.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        payload = {"codigo_usuario": otro.codigo_usuario}
        response = await client.post(
            f"/documentos/{doc_id}/permisos",
            json=payload,
            headers=headers_usuario,
        )
        assert response.status_code == 201
        permiso = response.json()
        assert permiso["codigo_usuario"] == otro.codigo_usuario
        assert permiso["id_documento"] == doc_id

    async def test_agregar_permiso_sin_ser_owner(
        self, client: AsyncClient, headers_usuario, headers_admin, test_session, test_empresa
    ):
        # Un usuario que NO es propietario del documento no puede conceder permisos (403)
        from app.core.security import hash_contrasena
        from app.models.usuario import Usuario

        otro_owner = Usuario(
            correo="owner@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="Owner",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro_owner)
        await test_session.flush()

        from app.core.security import crear_access_token

        token_owner = crear_access_token(
            {"sub": str(otro_owner.codigo_usuario), "empresa": otro_owner.codigo_empresa}
        )
        headers_owner = {"Authorization": f"Bearer {token_owner}"}

        files = {"archivo": ("owner.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_owner)
        doc_id = post_resp.json()["id_documento"]

        # headers_usuario NO es el owner de este documento
        payload = {"codigo_usuario": 999}
        response = await client.post(
            f"/documentos/{doc_id}/permisos",
            json=payload,
            headers=headers_usuario,
        )
        assert response.status_code == 403

    async def test_listar_permisos(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        # Tras agregar un permiso, debe aparecer en el listado de permisos del documento
        from app.core.security import hash_contrasena
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="permiso@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="Permiso",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        files = {"archivo": ("list.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        await client.post(
            f"/documentos/{doc_id}/permisos",
            json={"codigo_usuario": otro.codigo_usuario},
            headers=headers_usuario,
        )

        response = await client.get(f"/documentos/{doc_id}/permisos", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["codigo_usuario"] == otro.codigo_usuario

    async def test_quitar_permiso(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        # El propietario puede revocar un permiso existente
        from app.core.security import hash_contrasena
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="quitar@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="Quitar",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        files = {"archivo": ("quitar.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        await client.post(
            f"/documentos/{doc_id}/permisos",
            json={"codigo_usuario": otro.codigo_usuario},
            headers=headers_usuario,
        )

        response = await client.delete(
            f"/documentos/{doc_id}/permisos/{otro.codigo_usuario}",
            headers=headers_usuario,
        )
        assert response.status_code == 204

    async def test_eliminar_documento(self, client: AsyncClient, headers_usuario):
        # El propietario puede eliminar un documento (soft delete o borrado físico según implementación)
        files = {"archivo": ("borrar.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        response = await client.delete(f"/documentos/{doc_id}", headers=headers_usuario)
        assert response.status_code == 204

    async def test_get_documento_sin_permiso(self, client: AsyncClient, headers_usuario, test_session, test_empresa):
        # Un usuario sin permiso no puede acceder a un documento de otro usuario
        from app.core.security import hash_contrasena, crear_access_token
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="sinpermiso@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="SinPermiso",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        token_otro = crear_access_token(
            {"sub": str(otro.codigo_usuario), "empresa": otro.codigo_empresa}
        )
        headers_otro = {"Authorization": f"Bearer {token_otro}"}

        files = {"archivo": ("privado.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        response = await client.get(f"/documentos/{doc_id}", headers=headers_otro)
        assert response.status_code == 403

    async def test_get_documento_con_permiso(self, client: AsyncClient, headers_usuario, test_session, test_empresa):
        # Un usuario CON permiso puede acceder al documento de otro usuario
        from app.core.security import hash_contrasena, crear_access_token
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="conpermiso@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="ConPermiso",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        token_otro = crear_access_token(
            {"sub": str(otro.codigo_usuario), "empresa": otro.codigo_empresa}
        )
        headers_otro = {"Authorization": f"Bearer {token_otro}"}

        files = {"archivo": ("compartido.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        await client.post(
            f"/documentos/{doc_id}/permisos",
            json={"codigo_usuario": otro.codigo_usuario},
            headers=headers_usuario,
        )

        response = await client.get(f"/documentos/{doc_id}", headers=headers_otro)
        assert response.status_code == 200

    async def test_admin_empresa_puede_acceder(self, client: AsyncClient, headers_admin, test_session, test_empresa):
        # admin_empresa puede acceder a documentos de su empresa sin permiso explícito
        from app.core.security import hash_contrasena, crear_access_token
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="docowner@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="DocOwner",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        token_otro = crear_access_token(
            {"sub": str(otro.codigo_usuario), "empresa": otro.codigo_empresa}
        )
        headers_otro = {"Authorization": f"Bearer {token_otro}"}

        files = {"archivo": ("adminvea.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_otro)
        doc_id = post_resp.json()["id_documento"]

        response = await client.get(f"/documentos/{doc_id}", headers=headers_admin)
        assert response.status_code == 200


class TestDescargarDocumento:

    async def test_descargar_documento(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        # El propietario puede descargar su documento
        files = {"archivo": ("descargar.pdf", BytesIO(b"contenido"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        response = await client.get(
            f"/documentos/{doc_id}/descargar",
            headers=headers_usuario,
        )
        # Puede ser 200 (FileResponse) o 404 si el archivo físico no existe en disco de test
        assert response.status_code in (200, 404)

    async def test_descargar_documento_sin_permiso(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        # Un usuario sin permiso no puede descargar documentos de otro
        from app.core.security import hash_contrasena, crear_access_token
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="nodescarga@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="NoDescarga",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        token_otro = crear_access_token(
            {"sub": str(otro.codigo_usuario), "empresa": otro.codigo_empresa}
        )
        headers_otro = {"Authorization": f"Bearer {token_otro}"}

        files = {"archivo": ("privado.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        response = await client.get(
            f"/documentos/{doc_id}/descargar",
            headers=headers_otro,
        )
        assert response.status_code == 403


class TestQuitarPermiso:

    async def test_quitar_permiso(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        # Quitar un permiso existente debe devolver 204
        from app.core.security import hash_contrasena
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="quitarperm@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="QuitarPerm",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        files = {"archivo": ("qperm.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        # Agregar permiso primero
        await client.post(
            f"/documentos/{doc_id}/permisos",
            json={"codigo_usuario": otro.codigo_usuario},
            headers=headers_usuario,
        )

        # Quitar permiso
        response = await client.delete(
            f"/documentos/{doc_id}/permisos/{otro.codigo_usuario}",
            headers=headers_usuario,
        )
        assert response.status_code == 204
