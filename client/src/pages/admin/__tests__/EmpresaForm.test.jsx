import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import EmpresaForm from '../EmpresaForm'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn() }
}))

describe('EmpresaForm', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderForm = (id) => {
    const initialPath = id ? `/admin/empresas/${id}/editar` : '/admin/empresas/nueva'
    return render(
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/admin/empresas/nueva" element={<EmpresaForm />} />
          <Route path="/admin/empresas/:id/editar" element={<EmpresaForm />} />
        </Routes>
      </MemoryRouter>
    )
  }

  it('renders create form without loading', () => {
    renderForm()
    expect(screen.getByText('Nueva empresa')).toBeInTheDocument()
    expect(screen.getByText('Crear empresa')).toBeInTheDocument()
    expect(screen.queryByText('Cargando empresa...')).not.toBeInTheDocument()
  })

  it('shows loading in edit mode', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockReturnValueOnce(new Promise(() => {}))
    renderForm(1)
    expect(screen.getByText('Cargando empresa...')).toBeInTheDocument()
  })

  it('loads existing data in edit mode', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { nombre: 'Test Corp', web: 'https://test.com' } })
    renderForm(1)
    await waitFor(() => {
      expect(screen.getByText('Editar empresa')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Test Corp')).toBeInTheDocument()
      expect(screen.getByDisplayValue('https://test.com')).toBeInTheDocument()
    })
  })

  it('calls POST on create submit', async () => {
    const api = (await import('../../../api/axios')).default
    api.post.mockResolvedValueOnce({})
    renderForm()
    const inputs = document.querySelectorAll('input')
    fireEvent.change(inputs[0], { target: { value: 'Nueva Emp' } })
    fireEvent.click(screen.getByText('Crear empresa'))
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/admin/empresas', expect.objectContaining({ nombre: 'Nueva Emp' }))
    })
  })

  it('calls PUT on edit submit', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: { nombre: 'Test Corp', web: null } })
    api.put.mockResolvedValueOnce({})
    renderForm(1)
    await waitFor(() => expect(screen.getByText('Editar empresa')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Actualizar empresa'))
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/admin/empresas/1', expect.objectContaining({ nombre: 'Test Corp' }))
    })
  })

  it('shows validation error for empty name', async () => {
    renderForm()
    fireEvent.submit(document.querySelector('form'))
    await waitFor(() => {
      expect(screen.getByText('El nombre es obligatorio')).toBeInTheDocument()
    })
  })
})
