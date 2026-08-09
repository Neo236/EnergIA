import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface Estado {
  error: Error | null
}

/**
 * Sin esto, una excepción en cualquier componente deja la pantalla
 * completamente en blanco — el peor resultado posible durante una
 * demostración. Acá al menos queda un mensaje y una salida.
 *
 * Tiene que ser una clase: React todavía no ofrece equivalente en hooks.
 */
export class LimiteDeError extends Component<Props, Estado> {
  state: Estado = { error: null }

  static getDerivedStateFromError(error: Error): Estado {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Error no controlado en la interfaz:', error, info.componentStack)
  }

  render() {
    const { error } = this.state
    if (!error) return this.props.children

    return (
      <main className="page">
        <div className="col">
          <div className="aviso" role="alert">
            <div className="aviso__head">
              <span className="aviso__icon" aria-hidden="true">!</span>
              <h1 className="aviso__title">Algo salió mal</h1>
            </div>
            <p className="aviso__text">
              La aplicación encontró un problema inesperado. Recargar la página suele resolverlo.
            </p>
            <button type="button" className="btn btn--compact" onClick={() => window.location.assign('/')}>
              Volver al inicio
            </button>

            <details className="detalle-tecnico">
              <summary>Detalle técnico</summary>
              <dl>
                <dt>Error</dt>
                <dd>{error.message}</dd>
              </dl>
            </details>
          </div>
        </div>
      </main>
    )
  }
}
