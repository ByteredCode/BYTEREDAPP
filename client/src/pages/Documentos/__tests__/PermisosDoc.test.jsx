import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { ToastProvider } from '../../../context/ToastContext'
import PermisosDoc from '../PermisosDoc'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() }
}))

describe('PermisosDoc', () => {
  const docMock = { id_documento: 1, nombre: 'test.pdf' }
  const onClose = vi.fn()
  const onUpdated = vi.fn()

  beforeEach(() => { vi.clearAllMocks() })

  const renderPermisos = () => {
    return render(
      <ToastProvider>
        <PermisosDoc doc={docMock} onClose={onClose} onUpdated={onUpdated} />
      </ToastProvider>
    )
  }

  it('renders modal title with document name', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [] })
    renderPermisos()
    await waitFor(() => {
      expect(screen.getByText('Permisos: test.pdf')).toBeInTheDocument()
    })
  })

  it('loads and displays permisos list', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [{ codigo_usuario: 5 }] })
    renderPermisos()
    await waitFor(() => {
      expect(screen.getByText('#5')).toBeInTheDocument()
    })
  })

  it('adds a permiso via input and button', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [] })
    api.post.mockResolvedValueOnce({})
    renderPermisos()
    await waitFor(() => expect(screen.getByPlaceholderText('ID de usuario')).toBeInTheDocument())
    fireEvent.change(screen.getByPlaceholderText('ID de usuario'), { target: { value: '3' } })
    fireEvent.click(screen.getByText('Añadir'))
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/documentos/1/permisos', { codigo_usuario: 3 })
    })
  })

  it('opens and closes the modal', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [] })
    renderPermisos()
    await waitFor(() => expect(screen.getByText('Permisos: test.pdf')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Cerrar'))
    expect(onClose).toHaveBeenCalled()
  })

  it('shows empty state when no permisos', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [] })
    renderPermisos()
    await waitFor(() => {
      expect(screen.getByText('Sin permisos adicionales')).toBeInTheDocument()
    })
  })
})
