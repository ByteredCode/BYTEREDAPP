import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../../context/AuthContext'
import AdminOnlyRoute from '../AdminOnlyRoute'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

describe('AdminOnlyRoute', () => {
  const renderAdmin = ({ usuario, cargando }) => {
    return render(
      <MemoryRouter>
        <AuthContext.Provider value={{ usuario, cargando, login: vi.fn(), logout: vi.fn() }}>
          <AdminOnlyRoute>
            <div>Contenido admin</div>
          </AdminOnlyRoute>
        </AuthContext.Provider>
      </MemoryRouter>
    )
  }

  it('renders children for admin_total', () => {
    renderAdmin({ usuario: { nombre: 'Admin', rol: 'admin_total' }, cargando: false })
    expect(screen.getByText('Contenido admin')).toBeInTheDocument()
  })

  it('renders children for admin_empresa', () => {
    renderAdmin({ usuario: { nombre: 'Admin', rol: 'admin_empresa' }, cargando: false })
    expect(screen.getByText('Contenido admin')).toBeInTheDocument()
  })

  it('redirects to /dashboard for regular user', () => {
    renderAdmin({ usuario: { nombre: 'User', rol: 'user' }, cargando: false })
    expect(screen.queryByText('Contenido admin')).not.toBeInTheDocument()
  })

  it('redirects to /login when not authenticated', () => {
    renderAdmin({ usuario: null, cargando: false })
    expect(screen.queryByText('Contenido admin')).not.toBeInTheDocument()
  })
})
