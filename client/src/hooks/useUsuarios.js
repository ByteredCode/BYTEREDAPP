import { useState, useEffect, useCallback } from "react"
import api from "../api/axios"
import { useAuth } from "../context/AuthContext"

export default function useUsuarios() {
  const { usuario } = useAuth()
  const [usuarios, setUsuarios] = useState([])

  const fetchUsuarios = useCallback(async () => {
    const intentos = [
      api.get("/empresa/mi-empresa/usuarios").then(r => r.data),
      api.get("/admin/usuarios", { params: { limit: 200 } }).then(r => r.data.items || r.data),
      usuario?.codigo_empresa
        ? api.get(`/admin/empresas/${usuario.codigo_empresa}/usuarios`, { params: { limit: 200 } }).then(r => r.data.items || r.data)
        : Promise.reject(),
    ]
    const resultados = await Promise.allSettled(intentos)
    const exitoso = resultados.find(r => r.status === "fulfilled")
    if (exitoso) setUsuarios(exitoso.value)
  }, [usuario])

  useEffect(() => { fetchUsuarios() }, [fetchUsuarios])

  return { usuarios, fetchUsuarios }
}
