// Tests unitarios del hook useUsuarios
// Verificamos el fallback de endpoints: primero /empresa/mi-empresa/usuarios,
// luego /admin/usuarios, y finalmente /admin/empresas/:id/usuarios
import { renderHook, waitFor } from '@testing-library/react'
import { AuthContext } from '../../context/AuthContext'
import useUsuarios from '../useUsuarios'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn() }
}))

const { default: api } = await import('../../api/axios')

const mockUsuario = { codigo_empresa: 1 }

const wrapper = ({ children }) => (
  <AuthContext.Provider value={{ usuario: mockUsuario }}>
    {children}
  </AuthContext.Provider>
)

describe('useUsuarios', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('retorna usuarios del primer endpoint exitoso', async () => {
    // El hook lanza las 3 peticiones simultáneamente via Promise.allSettled,
    // así que necesitamos mockear las 3 respuestas
    api.get
      .mockResolvedValueOnce({ data: [{ codigo_usuario: 1, nombre: 'Juan' }] })
      .mockResolvedValueOnce({ data: { items: [] } })
      .mockResolvedValueOnce({ data: { items: [] } })

    const { result } = renderHook(() => useUsuarios(), { wrapper })

    await waitFor(() => {
      expect(result.current.usuarios).toHaveLength(1)
    })
    expect(result.current.usuarios[0].nombre).toBe('Juan')
    expect(api.get).toHaveBeenCalledWith('/empresa/mi-empresa/usuarios')
  })

  it('fallback al segundo endpoint si el primero falla', async () => {
    // El primer endpoint falla, el segundo (/admin/usuarios) devuelve items
    api.get
      .mockRejectedValueOnce(new Error('403'))
      .mockResolvedValueOnce({ data: { items: [{ codigo_usuario: 2, nombre: 'Ana' }] } })
      .mockResolvedValueOnce({ data: { items: [] } })

    const { result } = renderHook(() => useUsuarios(), { wrapper })

    await waitFor(() => {
      expect(result.current.usuarios).toHaveLength(1)
    })
    expect(result.current.usuarios[0].nombre).toBe('Ana')
  })

  it('fallback al tercero si los dos primeros fallan', async () => {
    // Los dos primeros fallan, el tercero (/admin/empresas/1/usuarios) funciona
    api.get
      .mockRejectedValueOnce(new Error('403'))
      .mockRejectedValueOnce(new Error('403'))
      .mockResolvedValueOnce({ data: { items: [{ codigo_usuario: 3, nombre: 'Luis' }] } })

    const { result } = renderHook(() => useUsuarios(), { wrapper })

    await waitFor(() => {
      expect(result.current.usuarios).toHaveLength(1)
    })
    expect(result.current.usuarios[0].nombre).toBe('Luis')
    expect(api.get).toHaveBeenCalledWith('/admin/empresas/1/usuarios', { params: { limit: 200 } })
  })
})
