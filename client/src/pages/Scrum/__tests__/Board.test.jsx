// Tests unitarios del tablero Kanban (Board)
// Verificamos renderizado de columnas, tareas, drag & drop, filtros y formularios
import { act } from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Board from '../Board'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), put: vi.fn(), delete: vi.fn() }
}))

vi.mock('../../../hooks/useUsuarios', () => ({
  default: () => ({ usuarios: [], loading: false })
}))

vi.mock('../../../context/ToastContext', () => ({
  ToastProvider: ({ children }) => children,
  useToast: () => ({ showToast: vi.fn(), success: vi.fn(), error: vi.fn() })
}))

vi.mock('../../../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({ usuario: { nombre: 'Test', rol: 'user' } })
}))

vi.mock('../../../components/common/LoadingSpinner', () => ({
  default: ({ mensaje }) => <div>{mensaje}</div>
}))

const mockDnd = { onDragStart: null, onDragEnd: null }
let mockIsDragging = false
vi.mock('@dnd-kit/core', () => ({
  DndContext: ({ children, onDragStart, onDragEnd }) => {
    mockDnd.onDragStart = onDragStart
    mockDnd.onDragEnd = onDragEnd
    return <div data-dnd-context="">{children}</div>
  },
  DragOverlay: ({ children }) => <div data-drag-overlay="">{children}</div>,
  PointerSensor: vi.fn(() => ({})),
  useSensor: vi.fn((s) => s),
  useSensors: vi.fn((...s) => s),
  useDroppable: vi.fn(() => ({ setNodeRef: vi.fn(), isOver: false })),
}))

vi.mock('@dnd-kit/sortable', () => ({
  SortableContext: ({ children }) => <div data-sortable-context="">{children}</div>,
  useSortable: vi.fn(() => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: mockIsDragging,
  })),
  verticalListSortingStrategy: vi.fn(),
}))

vi.mock('../TareaForm', () => ({
  default: ({ onClose, editando, sprintActivo }) => (
    <div data-testid="tarea-form">
      Formulario de tarea
      {editando && <span data-testid="editando-id">{editando.codigo_tarea}</span>}
      {sprintActivo && <span data-testid="sprint-activo">{sprintActivo}</span>}
      <button onClick={onClose}>Cerrar</button>
    </div>
  )
}))

describe('Board', () => {
  const mockColumnas = {
    Todo: [{ codigo_tarea: 1, titulo: 'Tarea 1', columna: 'Todo', prioridad: 'Alta', orden: 0 }],
    Haciendose: [{ codigo_tarea: 2, titulo: 'Tarea 2', columna: 'Haciendose', prioridad: 'Media', orden: 0 }],
    'En revision': [],
    Done: [],
  }

  beforeEach(() => { vi.clearAllMocks() })

  const renderBoard = async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url === '/scrum/tablero') return Promise.resolve({ data: mockColumnas })
      if (url === '/scrum/sprints') return Promise.resolve({ data: [] })
      return Promise.reject(new Error('Unknown'))
    })
    render(<Board />)
    await waitFor(() => expect(screen.getByText('Por hacer')).toBeInTheDocument())
  }

  it('renders 4 Kanban columns', async () => {
    await renderBoard()
    expect(screen.getByText('Por hacer')).toBeInTheDocument()
    expect(screen.getByText('En proceso')).toBeInTheDocument()
    expect(screen.getByText('En revisión')).toBeInTheDocument()
    expect(screen.getByText('Terminado')).toBeInTheDocument()
  })

  it('shows tasks in correct columns', async () => {
    await renderBoard()
    expect(screen.getByText('Tarea 1')).toBeInTheDocument()
    expect(screen.getByText('Tarea 2')).toBeInTheDocument()
  })

  it('add task button opens form', async () => {
    await renderBoard()
    const addButtons = screen.getAllByTitle('Agregar tarea')
    fireEvent.click(addButtons[0])
    expect(screen.getByTestId('tarea-form')).toBeInTheDocument()
  })

  it('renders sprint filter with options', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url === '/scrum/tablero') return Promise.resolve({ data: mockColumnas })
      if (url === '/scrum/sprints') return Promise.resolve({
        data: [{ codigo_sprint: 1, nombre: 'Sprint 1' }, { codigo_sprint: 2, nombre: 'Sprint 2' }]
      })
      return Promise.reject(new Error('Unknown'))
    })
    render(<Board />)
    await waitFor(() => expect(screen.getByText('Todos los sprints')).toBeInTheDocument())
    expect(screen.getByText('Sprint 1')).toBeInTheDocument()
    expect(screen.getByText('Sprint 2')).toBeInTheDocument()
  })

  it('changes sprint filter value', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockImplementation((url) => {
      if (url === '/scrum/tablero') return Promise.resolve({ data: mockColumnas })
      if (url === '/scrum/sprints') return Promise.resolve({
        data: [{ codigo_sprint: 1, nombre: 'Sprint 1' }]
      })
      return Promise.reject(new Error('Unknown'))
    })
    render(<Board />)
    await waitFor(() => expect(screen.getByText('Sprint 1')).toBeInTheDocument())
    const selects = screen.getAllByRole('combobox')
    fireEvent.change(selects[0], { target: { value: '1' } })
    expect(screen.getByDisplayValue('Sprint 1')).toBeInTheDocument()
  })

  it('adds task on last column', async () => {
    await renderBoard()
    const addButtons = screen.getAllByTitle('Agregar tarea')
    fireEvent.click(addButtons[3])
    expect(screen.getByTestId('tarea-form')).toBeInTheDocument()
  })

  it('closes TareaForm on cancel', async () => {
    await renderBoard()
    fireEvent.click(screen.getAllByTitle('Agregar tarea')[0])
    expect(screen.getByTestId('tarea-form')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Cerrar'))
    expect(screen.queryByTestId('tarea-form')).not.toBeInTheDocument()
  })

  it('opens edit form when clicking a task card', async () => {
    await renderBoard()
    fireEvent.click(screen.getByText('Tarea 1'))
    expect(screen.getByTestId('editando-id')).toHaveTextContent('1')
  })

  it('invokes handleDragStart when DndContext fires onDragStart', async () => {
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 1 } }) })
    const overlay = document.querySelector('.kanban-card-drag')
    expect(overlay).toBeInTheDocument()
  })

  it('invokes handleDragEnd to move task to another column', async () => {
    const api = (await import('../../../api/axios')).default
    api.put.mockResolvedValueOnce({})
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 1 } }) })
    act(() => { mockDnd.onDragEnd({ active: { id: 1 }, over: { id: 'Haciendose' } }) })
    await waitFor(() => expect(api.put).toHaveBeenCalled())
  })

  it('does not call API when drag ends without target', async () => {
    const api = (await import('../../../api/axios')).default
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 1 } }) })
    act(() => { mockDnd.onDragEnd({ active: { id: 1 }, over: null }) })
    expect(api.put).not.toHaveBeenCalled()
  })

  it('does not call API when dropping in same position', async () => {
    const api = (await import('../../../api/axios')).default
    api.put.mockResolvedValueOnce({})
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 1 } }) })
    act(() => { mockDnd.onDragEnd({ active: { id: 1 }, over: { id: 1 } }) })
    expect(api.put).not.toHaveBeenCalled()
  })

  it('calls fetchTablero on API error (rollback)', async () => {
    const api = (await import('../../../api/axios')).default
    api.put.mockRejectedValueOnce(new Error('Network error'))
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 1 } }) })
    act(() => { mockDnd.onDragEnd({ active: { id: 1 }, over: { id: 'Haciendose' } }) })
    await waitFor(() => expect(api.get).toHaveBeenCalledWith('/scrum/tablero', { params: {} }))
  })

  it('drops on another task card (not column)', async () => {
    const api = (await import('../../../api/axios')).default
    api.put.mockResolvedValueOnce({})
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 1 } }) })
    act(() => { mockDnd.onDragEnd({ active: { id: 1 }, over: { id: 2 } }) })
    await waitFor(() => expect(api.put).toHaveBeenCalled())
  })

  it('returns early when dropping on non-existent card', async () => {
    const api = (await import('../../../api/axios')).default
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 1 } }) })
    act(() => { mockDnd.onDragEnd({ active: { id: 1 }, over: { id: 999 } }) })
    expect(api.put).not.toHaveBeenCalled()
  })

  it('renders tarea with fecha_limite and asignacion', async () => {
    const api = (await import('../../../api/axios')).default
    const dataConExtra = {
      Todo: [{ codigo_tarea: 10, titulo: 'Completa', columna: 'Todo', prioridad: 'Baja', orden: 0, fecha_limite: '2025-12-31', asignacion: 5 }],
      Haciendose: [],
      'En revision': [],
      Done: [],
    }
    api.get.mockImplementation((url) => {
      if (url === '/scrum/tablero') return Promise.resolve({ data: dataConExtra })
      if (url === '/scrum/sprints') return Promise.resolve({ data: [] })
      return Promise.reject(new Error('Unknown'))
    })
    render(<Board />)
    await waitFor(() => expect(screen.getByText('Completa')).toBeInTheDocument())
    expect(screen.getByText('#5')).toBeInTheDocument()
    expect(screen.getByText('2025-12-31')).toBeInTheDocument()
    expect(screen.getByText('Baja')).toBeInTheDocument()
  })

  it('shows dragging opacity when isDragging is true', async () => {
    mockIsDragging = true
    await renderBoard()
    const cards = document.querySelectorAll('.kanban-card')
    expect(cards.length).toBeGreaterThan(0)
    expect(cards[0].style.opacity).toBe('0.4')
    mockIsDragging = false
  })

  it('returns null in CardPreview for unknown activeId', async () => {
    await renderBoard()
    act(() => { mockDnd.onDragStart({ active: { id: 999 } }) })
    const overlay = document.querySelector('.kanban-card-drag')
    expect(overlay).not.toBeInTheDocument()
  })
})
