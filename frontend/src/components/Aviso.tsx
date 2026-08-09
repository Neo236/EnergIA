import { textoDeAviso } from '../lib/mensajes'
import type { RespuestaError } from '../lib/contrato'

interface Props {
  respuesta: RespuestaError
  onReintentar: () => void
}

/**
 * Aviso para los errores que no son de validación por campo.
 *
 * Muestra un texto escrito para el usuario y deja el mensaje crudo de la
 * API en un detalle plegable: durante la integración, poder ver qué
 * respondió el back-end sin abrir las herramientas del navegador ahorra
 * mucho ida y vuelta con el equipo.
 */
export function Aviso({ respuesta, onReintentar }: Props) {
  const { titulo, texto, advertencia } = textoDeAviso(respuesta.status)

  return (
    <div className={advertencia ? 'aviso is-warning' : 'aviso'} role="alert">
      <div className="aviso__head">
        <span className="aviso__icon" aria-hidden="true">!</span>
        <h2 className="aviso__title">{titulo}</h2>
      </div>

      <p className="aviso__text">{texto}</p>

      <button type="button" className="btn btn--compact" onClick={onReintentar}>
        Reintentar
      </button>

      {respuesta.mensaje && (
        <details className="detalle-tecnico">
          <summary>Detalle técnico</summary>
          <dl>
            <dt>Estado</dt>
            <dd>{respuesta.status}{respuesta.error ? ` · ${respuesta.error}` : ''}</dd>
            <dt>Mensaje de la API</dt>
            <dd>{respuesta.mensaje}</dd>
            {respuesta.timestamp && (
              <>
                <dt>Momento</dt>
                <dd>{respuesta.timestamp}</dd>
              </>
            )}
          </dl>
        </details>
      )}
    </div>
  )
}
