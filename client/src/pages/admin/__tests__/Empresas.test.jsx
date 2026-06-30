import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ToastProvider } from '../../../context/ToastContext'
import Empresas from '../Empresas'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), delete: vi.fn() }
}))

describe('Empresas', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderEmpresas = () => {
    return render(
      <MemoryRouter>
        <ToastProvider>
          <Empresas />
        </ToastProvider>
      </MemoryRouter>
    )
  }

  it('shows loading state', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderEmpresas()
    expect(screen.getByText('Cargando empresas...')).toBeInTheDocument()
  })

  it('shows error on API failure', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockRejectedValueOnce(new Error('fail'))
    renderEmpresas()
    await waitFor(() => {
      expect(screen.getByText('Error al cargar empresas')).toBeInTheDocument()
    })
  })

  it('shows empty state when no empresas', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderEmpresas()
    await waitFor(() => {
      expect(screen.getByText('No hay empresas registradas.')).toBeInTheDocument()
    })
  })

  it('renders empresa table with data', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({
      data: {
        items: [
          { codigo_empresa: 1, nombre: 'Empresa A', web: 'https://a.com' },
          { codigo_empresa: 2, nombre: 'Empresa B', web: null },
        ],
        total: 2,
      }
    })
    renderEmpresas()
    await waitFor(() => {
      expect(screen.getByText('Empresa A')).toBeInTheDocument()
      expect(screen.getByText('Empresa B')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })

  it('shows action links for each empresa', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({
      data: { items: [{ codigo_empresa: 1, nombre: 'Test', web: null }], total: 1 }
    })
    renderEmpresas()
    await waitFor(() => {
      expect(screen.getByText('Editar')).toBeInTheDocument()
      expect(screen.getByText('Servicios')).toBeInTheDocument()
      expect(screen.getByText('Usuarios')).toBeInTheDocument()
      expect(screen.getByText('Eliminar')).toBeInTheDocument()
    })
  })

  it('shows Nueva empresa button', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderEmpresas()
    await waitFor(() => {
      expect(screen.getByText('Nueva empresa')).toBeInTheDocument()
    })
  })
})
