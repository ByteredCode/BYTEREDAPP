import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ScrumLayout from '../ScrumLayout'

describe('ScrumLayout', () => {
  it('renders navigation links', () => {
    render(
      <MemoryRouter initialEntries={['/scrum/tablero']}>
        <ScrumLayout />
      </MemoryRouter>
    )
    expect(screen.getByText('Tablero')).toBeInTheDocument()
    expect(screen.getByText('Sprints')).toBeInTheDocument()
  })

  it('marks Tablero link as active when on tablero route', () => {
    render(
      <MemoryRouter initialEntries={['/scrum/tablero']}>
        <ScrumLayout />
      </MemoryRouter>
    )
    expect(screen.getByText('Tablero').closest('a')).toHaveClass('activo')
  })
})
