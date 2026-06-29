import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../../../context/AuthContext'
import Usuarios from '../Usuarios'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

describe('Usuarios', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderUsuarios = (usuario) => {
    return render(
      <MemoryRouter>
        <AuthContext.Provider value={{ usuario, cargando: false, login: vi.fn(), logout: vi.fn() }}>
          <Usuarios />
        </AuthContext.Provider>
      </MemoryRouter>
    )
  }

  it('shows user list for authenticated user', async () => {
    const api = (await import('../../../api/axios')).default
    const mockUsuarios = [
      { codigo_usuario: 1, correo: 'a@a.com', nombre: 'Juan', rol: 'user', codigo_empresa: 1 },
    ]
    api.get.mockResolvedValueOnce({ data: mockUsuarios })
    renderUsuarios({ codigo_usuario: 1, rol: 'user', codigo_empresa: 1 })
    await waitFor(() => {
      expect(screen.getByText('Juan')).toBeInTheDocument()
    })
  })

  it('shows create user button for admin', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [] })
    renderUsuarios({ codigo_usuario: 1, rol: 'admin_total', codigo_empresa: 1 })
    await waitFor(() => {
      expect(screen.getByText('Nuevo usuario')).toBeInTheDocument()
    })
  })

  it('displays user data in table rows', async () => {
    const api = (await import('../../../api/axios')).default
    const mockUsuarios = [
      { codigo_usuario: 1, correo: 'a@a.com', nombre: 'Juan', rol: 'user', codigo_empresa: 1 },
      { codigo_usuario: 2, correo: 'b@b.com', nombre: 'Ana', rol: 'admin_empresa', codigo_empresa: 1 },
    ]
    api.get.mockResolvedValueOnce({ data: mockUsuarios })
    renderUsuarios({ codigo_usuario: 1, rol: 'admin_total', codigo_empresa: 1 })
    await waitFor(() => {
      expect(screen.getByText('Juan')).toBeInTheDocument()
      expect(screen.getByText('Ana')).toBeInTheDocument()
      expect(screen.getByText('a@a.com')).toBeInTheDocument()
      expect(screen.getByText('b@b.com')).toBeInTheDocument()
    })
  })
})
