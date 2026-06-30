import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../../context/AuthContext'
import MiEmpresa from '../MiEmpresa'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), patch: vi.fn() }
}))

describe('MiEmpresa', () => {
  const empresaMock = { codigo_empresa: 1, nombre: 'Mi Empresa', web: 'https://ejemplo.com' }

  beforeEach(() => { vi.clearAllMocks() })

  const renderMiEmpresa = (usuario) => {
    return render(
      <MemoryRouter>
        <AuthContext.Provider value={{ usuario, cargando: false, login: vi.fn(), logout: vi.fn() }}>
          <MiEmpresa />
        </AuthContext.Provider>
      </MemoryRouter>
    )
  }

  it('shows loading state', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderMiEmpresa({ rol: 'usuario' })
    expect(screen.getByText('Cargando...')).toBeInTheDocument()
  })

  it('stays on loading when API fails (component hides error behind loading)', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockRejectedValueOnce(new Error('fail'))
    renderMiEmpresa({ rol: 'usuario' })
    await waitFor(() => {
      expect(screen.getByText('Cargando...')).toBeInTheDocument()
    })
  })

  it('renders company data in view mode', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: empresaMock })
    renderMiEmpresa({ rol: 'usuario' })
    await waitFor(() => {
      expect(screen.getByText('Nombre:')).toBeInTheDocument()
      expect(screen.getAllByText('Mi Empresa').length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText('Código:')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('shows edit button only for admin roles', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: empresaMock })
    renderMiEmpresa({ rol: 'admin_total' })
    await waitFor(() => {
      expect(screen.getByText('Editar')).toBeInTheDocument()
    })
  })

  it('hides edit button for non-admin', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: empresaMock })
    renderMiEmpresa({ rol: 'usuario' })
    await waitFor(() => {
      expect(screen.queryByText('Editar')).not.toBeInTheDocument()
    })
  })

  it('switches to edit mode and saves', async () => {
    const api = (await import('../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: empresaMock })
    api.patch.mockResolvedValueOnce({ data: { ...empresaMock, nombre: 'Nuevo Nombre' } })
    renderMiEmpresa({ rol: 'admin_total' })
    await waitFor(() => expect(screen.getByText('Editar')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Editar'))
    expect(screen.getByDisplayValue('Mi Empresa')).toBeInTheDocument()
    fireEvent.change(screen.getByDisplayValue('Mi Empresa'), { target: { value: 'Nuevo Nombre' } })
    fireEvent.click(screen.getByText('Guardar'))
    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith('/empresa/mi-empresa', { nombre: 'Nuevo Nombre', web: 'https://ejemplo.com' })
    })
  })
})
