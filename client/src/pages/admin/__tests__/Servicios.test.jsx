import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import Servicios from '../Servicios'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), put: vi.fn() }
}))

describe('Servicios', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderServicios = () => {
    return render(
      <MemoryRouter initialEntries={['/admin/empresas/1/servicios']}>
        <Routes>
          <Route path="/admin/empresas/:id/servicios" element={<Servicios />} />
        </Routes>
      </MemoryRouter>
    )
  }

  const mockServicios = [
    { servicio: 'scrum', activo: true },
    { servicio: 'tickets', activo: false },
    { servicio: 'documentacion', activo: true },
    { servicio: 'redireccion', activo: false },
  ]

  it('shows loading state', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderServicios()
    expect(screen.getByText('Cargando servicios...')).toBeInTheDocument()
  })

  it('shows error on API failure', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockRejectedValueOnce(new Error('fail'))
    renderServicios()
    await waitFor(() => {
      expect(screen.getByText('Error al cargar servicios')).toBeInTheDocument()
    })
  })

  it('renders all 4 services with correct labels', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url.includes('/servicios')) return Promise.resolve({ data: mockServicios })
      if (url.includes('/empresas/1') && !url.includes('/servicios')) return Promise.resolve({ data: { nombre: 'Test Corp' } })
      return Promise.reject(new Error('Unknown'))
    })
    renderServicios()
    await waitFor(() => {
      expect(screen.getByText('Scrum')).toBeInTheDocument()
      expect(screen.getByText('Tickets')).toBeInTheDocument()
      expect(screen.getByText('Documentacion DPD/ISO')).toBeInTheDocument()
      expect(screen.getByText('Redireccion a web externa')).toBeInTheDocument()
    })
  })

  it('toggles a service via checkbox', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url.includes('/servicios')) return Promise.resolve({ data: mockServicios })
      if (url.includes('/empresas/1') && !url.includes('/servicios')) return Promise.resolve({ data: { nombre: 'Test Corp' } })
      return Promise.reject(new Error('Unknown'))
    })
    api.put.mockResolvedValueOnce({})
    renderServicios()
    await waitFor(() => expect(screen.getByText('Scrum')).toBeInTheDocument())
    const checkbox = screen.getAllByRole('checkbox')[1]
    fireEvent.click(checkbox)
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/admin/empresas/1/servicios', {
        servicio: 'tickets',
        activo: true,
      })
    })
  })

  it('shows empresa name in header', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url.includes('/servicios')) return Promise.resolve({ data: mockServicios })
      if (url.includes('/empresas/1') && !url.includes('/servicios')) return Promise.resolve({ data: { nombre: 'Test Corp' } })
      return Promise.reject(new Error('Unknown'))
    })
    renderServicios()
    await waitFor(() => {
      expect(screen.getByText(/Test Corp/)).toBeInTheDocument()
    })
  })
})
