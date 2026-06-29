import { render, screen } from '@testing-library/react'
import ErrorAlert from '../ErrorAlert'

describe('ErrorAlert', () => {
  it('renders error message', () => {
    render(<ErrorAlert mensaje="Algo salió mal" />)
    expect(screen.getByText('Algo salió mal')).toBeInTheDocument()
  })

  it('renders nothing when mensaje is null', () => {
    const { container } = render(<ErrorAlert mensaje={null} />)
    expect(container.firstChild).toBeNull()
  })
})
