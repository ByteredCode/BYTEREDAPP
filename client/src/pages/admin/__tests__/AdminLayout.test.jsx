import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../../../context/AuthContext'
import AdminLayout from '../AdminLayout'

describe('AdminLayout', () => {
  const renderLayout = (usuario) => {
    return render(
      <MemoryRouter initialEntries={['/admin']}>
        <AuthContext.Provider value={{ usuario, cargando: false, login: vi.fn(), logout: vi.fn() }}>
          <AdminLayout />
        </AuthContext.Provider>
      </MemoryRouter>
    )
  }

  it('renders sidebar with all links for admin_total', () => {
    renderLayout({ rol: 'admin_total' })
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Empresas')).toBeInTheDocument()
    expect(screen.getByText('Usuarios')).toBeInTheDocument()
    expect(screen.getByText('Tickets')).toBeInTheDocument()
    expect(screen.getByText('Documentos')).toBeInTheDocument()
  })

  it('hides Empresas link for admin_empresa', () => {
    renderLayout({ rol: 'admin_empresa' })
    expect(screen.queryByText('Empresas')).not.toBeInTheDocument()
    expect(screen.getByText('Usuarios')).toBeInTheDocument()
    expect(screen.getByText('Tickets')).toBeInTheDocument()
  })

  it('renders sidebar title', () => {
    renderLayout({ rol: 'admin_total' })
    expect(screen.getByText('Administracion')).toBeInTheDocument()
  })
})
