import { Component } from "react"

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary capturó un error:", error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="error-boundary">
          <h1>Algo salió mal</h1>
          <p>Ha ocurrido un error inesperado. Intenta recargar la página.</p>
          <button onClick={() => window.location.reload()}>Recargar página</button>
        </div>
      )
    }
    return this.props.children
  }
}
