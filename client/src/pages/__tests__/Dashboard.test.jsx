import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../../context/AuthContext'
import Dashboard from '../Dashboard'

vi.mock('../../api/axios', () => ({
  default: { get: vi.fn(), post: vi.fn() }
}))

describe('Dashboard', () => {
  const renderDashboard = (usuario) => {
    return render(
      <MemoryRouter>
        <AuthContext.Provider value={{ usuario, cargando: false, login: vi.fn(), logout: vi.fn() }}>
          <Dashboard />
        </AuthContext.Provider>
      </MemoryRouter>
    )
  }

  it('renders welcome message with user name', () => {
    renderDashboard({ nombre: 'Juan', rol: 'user' })
    expect(screen.getByText('Panel de control')).toBeInTheDocument()
    expect(screen.getByText('Bienvenido, Juan')).toBeInTheDocument()
  })

  it('shows module links based on context', () => {
    renderDashboard({ nombre: 'Juan', rol: 'user' })
    expect(screen.getByText('Scrum')).toBeInTheDocument()
    expect(screen.getByText('Ticket de soporte')).toBeInTheDocument()
    expect(screen.getByText('Fichajes')).toBeInTheDocument()
    expect(screen.getByText('Tickets')).toBeInTheDocument()
    expect(screen.getByText('Documentos')).toBeInTheDocument()
    expect(screen.queryByText('Administración')).not.toBeInTheDocument()
  })

  it('shows admin link for admin user', () => {
    renderDashboard({ nombre: 'Admin', rol: 'admin_total' })
    expect(screen.getByText('Administración')).toBeInTheDocument()
  })
})
