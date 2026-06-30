import { render, screen, waitFor } from '@testing-library/react'
import AdminDashboard from '../AdminDashboard'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn() }
}))

describe('AdminDashboard', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('shows loading state initially', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    render(<AdminDashboard />)
    expect(screen.getByText('Cargando...')).toBeInTheDocument()
  })

  it('shows error message on API failure', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockRejectedValueOnce(new Error('fail'))
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText('Error al cargar estadisticas')).toBeInTheDocument()
    })
  })

  it('renders stat cards with data', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({
      data: {
        total_empresas: 5, total_usuarios: 20, fichajes_abiertos: 3,
        empresas_sin_web: 1, tickets_ultimo_mes: 10,
        usuarios_por_rol: [{ clave: 'admin', total: 2 }],
        tickets_por_estado: [{ clave: 'Pendiente', total: 4 }],
        tareas_por_columna: [{ clave: 'Todo', total: 8 }],
      }
    })
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('20')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('10')).toBeInTheDocument()
    })
  })

  it('renders detail tables', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({
      data: {
        total_empresas: 0, total_usuarios: 0, fichajes_abiertos: 0,
        empresas_sin_web: 0, tickets_ultimo_mes: 0,
        usuarios_por_rol: [{ clave: 'admin', total: 2 }],
        tickets_por_estado: [{ clave: 'Pendiente', total: 4 }],
        tareas_por_columna: [{ clave: 'Todo', total: 8 }],
      }
    })
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText('Usuarios por rol')).toBeInTheDocument()
      expect(screen.getByText('Tickets por estado')).toBeInTheDocument()
      expect(screen.getByText('Tareas por columna')).toBeInTheDocument()
    })
  })

  it('handles empty arrays in detail tables', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({
      data: {
        total_empresas: 0, total_usuarios: 0, fichajes_abiertos: 0,
        empresas_sin_web: 0, tickets_ultimo_mes: 0,
        usuarios_por_rol: [], tickets_por_estado: [], tareas_por_columna: [],
      }
    })
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
    })
  })
})
