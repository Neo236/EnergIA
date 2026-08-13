/* ============================================================
   P-04 · La dirección no corresponde a ninguna sección.

   Distinta de «no encontramos ese análisis», que vive en Resultado: esa
   es una URL bien formada cuyo contenido no está; esta es una URL que no
   existe en el sitio.
   ============================================================ */

import { Link } from 'react-router-dom'

import { Aviso } from '../components/Aviso'
import { Boton } from '../components/Boton'

export function NoEncontrado() {
  return (
    <div className="columna columna--aviso">
      <Aviso
        titulo="Esta página no existe"
        texto="La dirección a la que llegaste no corresponde a ninguna sección del sitio."
        advertencia
      >
        <Link to="/"><Boton tipo="primario" ancho>Volver al inicio</Boton></Link>
      </Aviso>
    </div>
  )
}
