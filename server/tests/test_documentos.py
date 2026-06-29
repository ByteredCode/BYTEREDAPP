from io import BytesIO

import pytest
from httpx import AsyncClient


class TestDocumentos:

    async def test_subir_documento(self, client: AsyncClient, headers_usuario):
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
        files = {"archivo": ("malware.exe", BytesIO(b"datos"), "application/x-msdownload")}
        response = await client.post("/documentos", files=files, headers=headers_usuario)
        assert response.status_code == 400

    async def test_listar_documentos(self, client: AsyncClient, headers_usuario):
        files = {"archivo": ("doc1.pdf", BytesIO(b"contenido"), "application/pdf")}
        await client.post("/documentos", files=files, headers=headers_usuario)

        response = await client.get("/documentos", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_obtener_documento(self, client: AsyncClient, headers_usuario):
        files = {"archivo": ("doc.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        response = await client.get(f"/documentos/{doc_id}", headers=headers_usuario)
        assert response.status_code == 200
        assert response.json()["id_documento"] == doc_id

    async def test_agregar_permiso(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
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
        files = {"archivo": ("borrar.pdf", BytesIO(b"datos"), "application/pdf")}
        post_resp = await client.post("/documentos", files=files, headers=headers_usuario)
        doc_id = post_resp.json()["id_documento"]

        response = await client.delete(f"/documentos/{doc_id}", headers=headers_usuario)
        assert response.status_code == 204
