import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { ToastProvider } from '../../../context/ToastContext'
import DocumentosAdmin from '../DocumentosAdmin'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() }
}))

vi.mock('../PermisosDoc', () => ({
  default: ({ doc, onClose }) => (
    <div data-testid="permisos-modal">
      <span>Permisos de {doc.nombre}</span>
      <button onClick={onClose}>Cerrar permisos</button>
    </div>
  )
}))

describe('DocumentosAdmin', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderDocs = () => {
    return render(
      <ToastProvider>
        <DocumentosAdmin />
      </ToastProvider>
    )
  }

  const mockDocs = [
    { id_documento: 1, nombre: 'informe.pdf', tipo_documento: 'DPD', usuario_subio: 3, fecha: '2026-06-01' },
    { id_documento: 2, nombre: 'manual.docx', tipo_documento: null, usuario_subio: 5, fecha: '2026-06-02' },
  ]

  it('shows loading spinner initially', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderDocs()
    expect(screen.getByText('Cargando documentos...')).toBeInTheDocument()
  })

  it('shows empty state when no documentos', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderDocs()
    await waitFor(() => {
      expect(screen.getByText('No hay documentos')).toBeInTheDocument()
    })
  })

  it('renders document table', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockDocs, total: 2 } })
    renderDocs()
    await waitFor(() => {
      expect(screen.getByText('informe.pdf')).toBeInTheDocument()
      expect(screen.getByText('manual.docx')).toBeInTheDocument()
      expect(screen.getByText('DPD')).toBeInTheDocument()
      expect(screen.getByText('#3')).toBeInTheDocument()
      expect(screen.getByText('#5')).toBeInTheDocument()
    })
  })

  it('opens upload modal', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } })
    renderDocs()
    await waitFor(() => expect(screen.getByText('No hay documentos')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Subir documento'))
    expect(screen.getByText('Archivo')).toBeInTheDocument()
  })

  it('opens permisos modal on Permisos click', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockDocs, total: 2 } })
    renderDocs()
    await waitFor(() => expect(screen.getByText('informe.pdf')).toBeInTheDocument())
    fireEvent.click(screen.getAllByText('Permisos')[0])
    await waitFor(() => {
      expect(screen.getByTestId('permisos-modal')).toBeInTheDocument()
    })
  })

  it('calls delete on Eliminar click', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { items: mockDocs, total: 2 } })
    api.delete.mockResolvedValueOnce({})
    renderDocs()
    await waitFor(() => expect(screen.getByText('informe.pdf')).toBeInTheDocument())
    const originalConfirm = window.confirm
    window.confirm = vi.fn(() => true)
    fireEvent.click(screen.getAllByText('Eliminar')[0])
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/documentos/1')
    })
    window.confirm = originalConfirm
  })
})
