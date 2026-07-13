import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { ToastProvider } from '../../../context/ToastContext'
import DocumentosAdmin from '../DocumentosAdmin'

const mockGet = vi.fn()
const mockDelete = vi.fn()
vi.mock('../../../api/axios', () => ({
  default: { get: (...args) => mockGet(...args), post: vi.fn(), delete: (...args) => mockDelete(...args) }
}))

vi.mock('../../../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({ usuario: { nombre: 'Admin', rol: 'admin_total' } })
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
    { id_documento: 1, nombre: 'informe.pdf', tipo_documento: 'DPD', usuario_subio: 3, fecha: '2026-06-01', codigo_empresa: 1 },
    { id_documento: 2, nombre: 'manual.docx', tipo_documento: null, usuario_subio: 5, fecha: '2026-06-02', codigo_empresa: 1 },
  ]

  const mockEmpresas = [
    { codigo_empresa: 1, nombre: 'TestCorp' }
  ]

  const setupMocks = (docs = mockDocs) => {
    mockGet.mockImplementation((url) => {
      if (url === '/admin/empresas') return Promise.resolve({ data: { items: mockEmpresas, total: 1 } })
      if (url === '/documentos') return Promise.resolve({ data: { items: docs, total: docs.length } })
      return Promise.reject(new Error('Unknown URL'))
    })
  }

  it('shows loading spinner initially', async () => {
    mockGet.mockReturnValueOnce(new Promise(() => {}))
    mockGet.mockReturnValueOnce(new Promise(() => {}))
    renderDocs()
    expect(screen.getByText('Cargando documentos...')).toBeInTheDocument()
  })

  it('shows empty state when no documentos', async () => {
    setupMocks([])
    renderDocs()
    await waitFor(() => {
      expect(screen.getByText('No hay documentos')).toBeInTheDocument()
    })
  })

  it('renders document table', async () => {
    setupMocks()
    renderDocs()
    await waitFor(() => {
      expect(screen.getByText('informe.pdf')).toBeInTheDocument()
      expect(screen.getByText('manual.docx')).toBeInTheDocument()
    })
    expect(screen.getByText('#3')).toBeInTheDocument()
    expect(screen.getByText('#5')).toBeInTheDocument()
  })

  it('opens upload modal', async () => {
    setupMocks([])
    renderDocs()
    await waitFor(() => expect(screen.getByText('No hay documentos')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Subir documento'))
    expect(screen.getByText('Archivo')).toBeInTheDocument()
  })

  it('opens permisos modal on Permisos click', async () => {
    setupMocks()
    renderDocs()
    await waitFor(() => expect(screen.getByText('informe.pdf')).toBeInTheDocument())
    fireEvent.click(screen.getAllByText('Permisos')[0])
    await waitFor(() => {
      expect(screen.getByTestId('permisos-modal')).toBeInTheDocument()
    })
  })

  it('calls delete on Eliminar click', async () => {
    mockDelete.mockResolvedValue({})
    setupMocks()
    renderDocs()
    await waitFor(() => expect(screen.getByText('informe.pdf')).toBeInTheDocument())
    const originalConfirm = window.confirm
    window.confirm = vi.fn(() => true)
    fireEvent.click(screen.getAllByText('Eliminar')[0])
    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith('/documentos/1')
    })
    window.confirm = originalConfirm
  })
})
