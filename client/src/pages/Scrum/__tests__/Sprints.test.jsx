import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { ToastProvider } from '../../../context/ToastContext'
import Sprints from '../Sprints'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }
}))

describe('Sprints', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderSprints = () => {
    return render(
      <ToastProvider>
        <Sprints />
      </ToastProvider>
    )
  }

  const mockSprints = [
    { codigo_sprint: 1, nombre: 'Sprint 1', objetivo: 'Primer sprint', fecha_inicio: '2026-06-01', fecha_fin: '2026-06-15', estado: 'Activo' },
    { codigo_sprint: 2, nombre: 'Sprint 2', objetivo: null, fecha_inicio: null, fecha_fin: null, estado: 'Planificado' },
  ]

  it('shows loading spinner initially', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderSprints()
    expect(screen.getByText('Cargando sprints...')).toBeInTheDocument()
  })

  it('shows empty state when no sprints', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderSprints()
    await waitFor(() => {
      expect(screen.getByText('No hay sprints aún')).toBeInTheDocument()
    })
  })

  it('renders sprint list', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockSprints, total: 2 } })
    renderSprints()
    await waitFor(() => {
      expect(screen.getByText('Sprint 1')).toBeInTheDocument()
      expect(screen.getByText('Sprint 2')).toBeInTheDocument()
      expect(screen.getByText('Primer sprint')).toBeInTheDocument()
    })
  })

  it('opens create modal on Nuevo sprint click', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderSprints()
    await waitFor(() => expect(screen.getByText('No hay sprints aún')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Nuevo sprint'))
    expect(screen.getByText('Nombre')).toBeInTheDocument()
  })

  it('calls POST on create submit', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    api.post.mockResolvedValueOnce({})
    renderSprints()
    await waitFor(() => expect(screen.getByText('No hay sprints aún')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Nuevo sprint'))
    const inputs = document.querySelectorAll('input')
    fireEvent.change(inputs[0], { target: { value: 'Sprint Nuevo' } })
    fireEvent.click(screen.getByText('Guardar'))
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/scrum/sprints', expect.any(Object))
    })
  })

  it('calls DELETE on eliminar', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockSprints, total: 2 } })
    api.delete.mockResolvedValueOnce({})
    renderSprints()
    await waitFor(() => expect(screen.getByText('Sprint 1')).toBeInTheDocument())
    const originalConfirm = window.confirm
    window.confirm = vi.fn(() => true)
    fireEvent.click(screen.getAllByText('Eliminar')[0])
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/scrum/sprints/1')
    })
    window.confirm = originalConfirm
  })
})
