import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AuthContext } from '../../../context/AuthContext'
import UsuarioForm from '../UsuarioForm'

vi.mock('../../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn() }
}))

describe('UsuarioForm', () => {
  beforeEach(() => { vi.clearAllMocks() })

  const renderForm = (id, usuarioActual = { rol: 'admin_total', codigo_empresa: 1 }) => {
    const initialPath = id ? `/admin/usuarios/${id}/editar` : '/admin/usuarios/nueva'
    return render(
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/admin/usuarios/nueva" element={
            <AuthContext.Provider value={{ usuario: usuarioActual, cargando: false, login: vi.fn(), logout: vi.fn() }}>
              <UsuarioForm />
            </AuthContext.Provider>
          } />
          <Route path="/admin/usuarios/:id/editar" element={
            <AuthContext.Provider value={{ usuario: usuarioActual, cargando: false, login: vi.fn(), logout: vi.fn() }}>
              <UsuarioForm />
            </AuthContext.Provider>
          } />
        </Routes>
      </MemoryRouter>
    )
  }

  it('renders create form with password field', () => {
    renderForm()
    expect(screen.getByText('Nuevo usuario')).toBeInTheDocument()
    expect(screen.getByText('Contrasena *')).toBeInTheDocument()
    expect(screen.getByText('Crear usuario')).toBeInTheDocument()
  })

  it('renders edit form without password field', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [{ codigo_usuario: 1, correo: 'a@a.com', nombre: 'Juan', rol: 'usuario', codigo_empresa: 1 }] })
    renderForm(1)
    await waitFor(() => {
      expect(screen.getByText('Editar usuario')).toBeInTheDocument()
      expect(screen.queryByText('Contrasena *')).not.toBeInTheDocument()
    })
  })

  it('shows empresa field only for admin_total', () => {
    renderForm(null, { rol: 'admin_total', codigo_empresa: 1 })
    expect(screen.getByText('Codigo de empresa')).toBeInTheDocument()
  })

  it('hides empresa field for admin_empresa', () => {
    renderForm(null, { rol: 'admin_empresa', codigo_empresa: 1 })
    expect(screen.queryByText('Codigo de empresa')).not.toBeInTheDocument()
  })

  it('calls POST on create submit', async () => {
    const api = (await import('../../../api/axios')).default
    api.post.mockResolvedValueOnce({})
    renderForm()
    const inputs = document.querySelectorAll('input')
    fireEvent.change(inputs[0], { target: { value: 'correo@test.com' } })
    fireEvent.change(inputs[1], { target: { value: 'Juan' } })
    fireEvent.change(inputs[2], { target: { value: 'Password1' } })
    fireEvent.click(screen.getByText('Crear usuario'))
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/admin/usuarios', expect.any(Object))
    })
  })

  it('calls PUT on edit submit', async () => {
    const api = (await import('../../../api/axios')).default
    api.get.mockResolvedValueOnce({ data: [{ codigo_usuario: 1, correo: 'a@a.com', nombre: 'Juan', rol: 'usuario', codigo_empresa: 1 }] })
    api.put.mockResolvedValueOnce({})
    renderForm(1)
    await waitFor(() => expect(screen.getByText('Editar usuario')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Actualizar usuario'))
    await waitFor(() => {
      expect(api.put).toHaveBeenCalledWith('/admin/usuarios/1', expect.any(Object))
    })
  })
})
