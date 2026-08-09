/* ============================================================
   Capa de transporte.

   El modo por defecto viene de VITE_API_MODO (se resuelve al compilar),
   pero se puede cambiar en vivo desde la barra de demostración. Eso
   permite mostrar un 503 o un 500 cuando la API real no los va a devolver
   justo en el momento de la demostración.
   ============================================================ */

import { ENDPOINT, ErrorApi, type Analisis, type RespuestaError, type Solicitud } from './contrato'
import { analizarSimulado, type ModoDemo } from './mock'

export type ModoApi = 'mock' | 'real'

/** Valor inicial: lo que se eligió al construir la imagen. */
export const MODO_INICIAL: ModoApi = import.meta.env.VITE_API_MODO === 'real' ? 'real' : 'mock'

async function analizarReal(solicitud: Solicitud): Promise<Analisis> {
  let respuesta: Response
  try {
    respuesta = await fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(solicitud),
    })
  } catch {
    // Falla de red: ni siquiera llegamos al servidor.
    throw new ErrorApi({ status: 0, mensaje: 'No se pudo establecer la conexión con el servidor' })
  }

  const cuerpo: unknown = await respuesta.json().catch(() => null)

  if (respuesta.ok) return cuerpo as Analisis

  const parcial = (cuerpo ?? {}) as Partial<RespuestaError>
  throw new ErrorApi({
    status: parcial.status ?? respuesta.status,
    error: parcial.error ?? respuesta.statusText,
    mensaje: parcial.mensaje ?? `Error ${respuesta.status}`,
    ...(parcial.detalles ? { detalles: parcial.detalles } : {}),
    ...(parcial.timestamp ? { timestamp: parcial.timestamp } : {}),
  })
}

export interface OpcionesAnalisis {
  modoApi: ModoApi
  modoDemo: ModoDemo
}

export function analizar(solicitud: Solicitud, { modoApi, modoDemo }: OpcionesAnalisis): Promise<Analisis> {
  return modoApi === 'real' ? analizarReal(solicitud) : analizarSimulado(solicitud, modoDemo)
}
