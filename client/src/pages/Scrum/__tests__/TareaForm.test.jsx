import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { ToastProvider } from '../../../context/ToastContext'
import TareaForm from '../TareaForm'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn() }
}))

vi.mock('../../../hooks/useUsuarios', () => ({
  default: () => ({ usuarios: [{ codigo_usuario: 1, nombre: 'Ana' }, { codigo_usuario: 2, nombre: 'Luis' }], loading: false })
}))

describe('TareaForm', () => {
  const onClose = vi.fn()
  const onSaved = vi.fn()
  const sprintsMock = [{ codigo_sprint: 1, nombre: 'Sprint 1' }]

  beforeEach(() => { vi.clearAllMocks() })

  const renderForm = (props = {}) => {
    return render(
      <ToastProvider>
        <TareaForm
          editando={null}
          columna="Todo"
          sprints={sprintsMock}
          sprintActivo=""
          onClose={onClose}
          onSaved={onSaved}
          {...props}
        />
      </ToastProvider>
    )
  }

  it('renders form fields in create mode', () => {
    renderForm()
    expect(screen.getByText('Nueva tarea')).toBeInTheDocument()
    expect(screen.getByText('Título')).toBeInTheDocument()
    expect(screen.getByText('Guardar')).toBeInTheDocument()
  })

  it('pre-fills form in edit mode', () => {
    const editando = {
      codigo_tarea: 5,
      titulo: 'Tarea existente',
      descripcion: 'Descripción',
      prioridad: 'Alta',
      columna: 'Haciendose',
    }
    renderForm({ editando })
    expect(screen.getByText('Editar tarea')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Tarea existente')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Descripción')).toBeInTheDocument()
  })

  it('calls POST /scrum/tareas on create submit', async () => {
    const api = (await import('../../../api/axios')).default
    api.post.mockResolvedValueOnce({})
    renderForm()
    const inputs = document.querySelectorAll('input')
    fireEvent.change(inputs[0], { target: { value: 'Nueva tarea' } })
    fireEvent.click(screen.getByText('Guardar'))
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/scrum/tareas', expect.any(Object))
    })
  })

  it('calls PUT /scrum/tareas on edit submit', async () => {
    const api = (await import('../../../api/axios')).default
    api.put.mockResolvedValueOnce({})
    const editando = { codigo_tarea: 5, titulo: 'Editar', prioridad: 'Media', columna: 'Todo' }
    renderForm({ editando })
    fireEvent.click(screen.getByText('Guardar'))
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/scrum/tareas/5', expect.any(Object))
    })
  })

  it('calls onClose on cancel', () => {
    renderForm()
    fireEvent.click(screen.getByText('Cancelar'))
    expect(onClose).toHaveBeenCalled()
  })

  it('calls onSaved and onClose after successful save', async () => {
    const api = (await import('../../../api/axios')).default
    api.post.mockResolvedValueOnce({})
    renderForm()
    const inputs = document.querySelectorAll('input')
    fireEvent.change(inputs[0], { target: { value: 'Nueva' } })
    fireEvent.click(screen.getByText('Guardar'))
    await waitFor(() => {
      expect(onSaved).toHaveBeenCalled()
      expect(onClose).toHaveBeenCalled()
    })
  })
})
