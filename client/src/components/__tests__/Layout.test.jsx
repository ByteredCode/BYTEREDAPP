import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../../context/AuthContext'
import Layout from '../Layout'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

describe('Layout', () => {
  const renderLayout = (usuario = null) => {
    return render(
      <MemoryRouter>
        <AuthContext.Provider value={{ usuario, cargando: false, logout: vi.fn() }}>
          <Layout />
        </AuthContext.Provider>
      </MemoryRouter>
    )
  }

  it('renders nav links for authenticated user', () => {
    renderLayout({ nombre: 'Juan', rol: 'user' })
    expect(screen.getByText('BYTERED')).toBeInTheDocument()
    expect(screen.getByText('Scrum')).toBeInTheDocument()
    expect(screen.getByText('Fichajes')).toBeInTheDocument()
    expect(screen.getByText('Tickets')).toBeInTheDocument()
    expect(screen.getByText('Documentos')).toBeInTheDocument()
    expect(screen.getByText('Juan')).toBeInTheDocument()
  })

  it('shows login link when no user', () => {
    renderLayout(null)
    expect(screen.queryByText('BYTERED')).not.toBeInTheDocument()
    expect(screen.queryByText('Scrum')).not.toBeInTheDocument()
    expect(screen.queryByText('Salir')).not.toBeInTheDocument()
  })

  it('does not render admin link for regular user', () => {
    renderLayout({ nombre: 'Juan', rol: 'user' })
    expect(screen.queryByText('Admin')).not.toBeInTheDocument()
  })

  it('renders admin link for admin user', () => {
    renderLayout({ nombre: 'Admin', rol: 'admin_total' })
    expect(screen.getByRole('link', { name: 'Admin' })).toBeInTheDocument()
  })

  it('calls logout on Salir click', () => {
    const mockLogout = vi.fn()
    render(
      <MemoryRouter>
        <AuthContext.Provider value={{ usuario: { nombre: 'Juan', rol: 'user' }, cargando: false, logout: mockLogout }}>
          <Layout />
        </AuthContext.Provider>
      </MemoryRouter>
    )
    fireEvent.click(screen.getByText('Salir'))
    expect(mockLogout).toHaveBeenCalled()
  })
})
