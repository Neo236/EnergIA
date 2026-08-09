import { Link, useParams } from 'react-router-dom'
import { useTitulo } from '../lib/useTitulo'

/**
 * 404 general y, además, el caso de un análisis pedido por identificador.
 *
 * `/analisis/:id` existe a propósito aunque hoy SIEMPRE falle: la respuesta
 * de la API no incluye identificador ni hay persistencia (PA-19), así que
 * ningún análisis se puede recuperar por enlace. Dejar la ruta con su
 * mensaje propio documenta el hueco del contrato en vez de esconderlo, y
 * el día que la API devuelva un id, solo hay que implementar la búsqueda.
 */
export function NoEncontrado() {
  const { id } = useParams()
  useTitulo(id ? 'Análisis no encontrado' : 'Página no encontrada')
  const esAnalisis = id !== undefined

  return (
    <div className="col">
      <div className="aviso is-warning" role="alert">
        <div className="aviso__head">
          <span className="aviso__icon" aria-hidden="true">!</span>
          <h1 className="aviso__title">
            {esAnalisis ? 'No encontramos ese análisis' : 'Esta página no existe'}
          </h1>
        </div>
        <p className="aviso__text">
          {esAnalisis
            ? 'Los análisis no se guardan: cada resultado existe solo mientras dura tu visita. Hacé uno nuevo para ver tu perfil energético.'
            : 'La dirección a la que llegaste no corresponde a ninguna sección del sitio.'}
        </p>
        <Link className="btn btn--compact" to="/">
          {esAnalisis ? 'Hacer un análisis' : 'Volver al inicio'}
        </Link>
      </div>

      {esAnalisis && (
        <p className="note">
          Los enlaces compartibles quedan pendientes: requieren que la API devuelva un
          identificador y que exista persistencia.
        </p>
      )}
    </div>
  )
}
