import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import EmpresaUsuarios from '../EmpresaUsuarios'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn() }
}))

describe('EmpresaUsuarios', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderEmpresaUsuarios = () => {
    return render(
      <MemoryRouter initialEntries={['/admin/empresas/1/usuarios']}>
        <Routes>
          <Route path="/admin/empresas/:id/usuarios" element={<EmpresaUsuarios />} />
        </Routes>
      </MemoryRouter>
    )
  }

  it('shows loading state', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderEmpresaUsuarios()
    expect(screen.getByText('Cargando usuarios...')).toBeInTheDocument()
  })

  it('shows error on API failure', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockRejectedValueOnce(new Error('fail'))
    renderEmpresaUsuarios()
    await waitFor(() => {
      expect(screen.getByText('Error al cargar usuarios de la empresa')).toBeInTheDocument()
    })
  })

  it('renders empresa name and users table', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url.includes('/empresas/1') && !url.includes('/usuarios')) return Promise.resolve({ data: { nombre: 'Empresa Test', codigo_empresa: 1 } })
      if (url.includes('/usuarios')) return Promise.resolve({ data: { items: [{ codigo_usuario: 1, correo: 'a@a.com', nombre: 'Juan', rol: 'usuario' }], total: 1 } })
      return Promise.reject(new Error('Unknown'))
    })
    renderEmpresaUsuarios()
    await waitFor(() => {
      expect(screen.getByText('Usuarios de Empresa Test')).toBeInTheDocument()
      expect(screen.getByText('Juan')).toBeInTheDocument()
      expect(screen.getByText('a@a.com')).toBeInTheDocument()
    })
  })

  it('shows empty state when no users', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url.includes('/empresas/1') && !url.includes('/usuarios')) return Promise.resolve({ data: { nombre: 'Empresa Test', codigo_empresa: 1 } })
      if (url.includes('/usuarios')) return Promise.resolve({ data: { items: [], total: 0 } })
      return Promise.reject(new Error('Unknown'))
    })
    renderEmpresaUsuarios()
    await waitFor(() => {
      expect(screen.getByText('No hay usuarios en esta empresa.')).toBeInTheDocument()
    })
  })

  it('shows back button and nuevo usuario link', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url.includes('/empresas/1') && !url.includes('/usuarios')) return Promise.resolve({ data: { nombre: 'Empresa Test', codigo_empresa: 1 } })
      if (url.includes('/usuarios')) return Promise.resolve({ data: { items: [], total: 0 } })
      return Promise.reject(new Error('Unknown'))
    })
    renderEmpresaUsuarios()
    await waitFor(() => {
      expect(screen.getByText('Volver a empresas', { exact: false })).toBeInTheDocument()
      expect(screen.getByText('Nuevo usuario')).toBeInTheDocument()
    })
  })
})
